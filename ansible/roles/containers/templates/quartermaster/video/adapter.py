#!/usr/bin/env python3
"""OpenAI-style video API in front of Quartermaster's video jobs.

Open WebUI (0.13) creates a clip with ``POST /v1/videos`` (multipart: model, prompt, seconds, size,
input_reference), polls ``GET /v1/videos/{id}`` until the status is completed or failed, and downloads
``GET /v1/videos/{id}/content``. Quartermaster runs the same work as an sd-server job:
``POST /sdcpp/v1/vid_gen`` returns a job id, ``GET /sdcpp/v1/jobs/{id}`` returns its state and, once done,
the whole clip as ``result.b64_json`` with ``result.mime_type``. This adapter only translates between the
two; Quartermaster keeps the job, so the adapter holds no state.

It runs inside the Quartermaster container next to the server (see the image's qm-entrypoint.sh).

Settings (environment; the QM_VIDEO_ prefix keeps them apart from Quartermaster's own settings):
  QM_VIDEO_UPSTREAM Quartermaster base URL (default http://127.0.0.1:8080)
  QM_VIDEO_API_KEY  Bearer key for Quartermaster, if it has one (default: none)
  QM_VIDEO_OUTPUT_FORMAT
                    webp (animated WebP), webm, avi or gif (default webp). sd-server has no GIF output, so a GIF
                    is rendered as animated WebP and converted with Pillow; Pillow also reads the start image's
                    size, and it is the only non-standard module
  QM_VIDEO_FPS      frames per second (default 16)
  QM_VIDEO_SECONDS  clip length when the request gives none (default 3)
  QM_VIDEO_SIZE     WxH when the request gives none (default 672x384)
  QM_VIDEO_MAX_PIXELS
                    upper bound on width x height (default: QM_VIDEO_SIZE's pixel count). A larger requested size
                    (a chat model may ask for 768x1024) is scaled down to it with its aspect ratio kept, sides on
                    multiples of 16: render time and graphics memory grow faster than the pixel count, and an
                    8 s clip at 3x the pixels did not fit the 20 GB card
  QM_VIDEO_FRAME_STEP, QM_VIDEO_FRAME_OFFSET
                    the model's frame grid, frames = FRAME_STEP * n + FRAME_OFFSET
                    (Wan: 4n+1, LTX: 8n+1, MiniMax-H3: 17n+5; default 4 and 1)
  QM_VIDEO_PORT     listen port (default 8081)
  QM_VIDEO_STEPS    sampling steps (default: unset, so the model's --steps/--high-noise-steps apply)
"""
import base64
import email.parser
import io
import email.policy
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

QM_URL = os.environ.get("QM_VIDEO_UPSTREAM", "http://127.0.0.1:8080").rstrip("/")
QM_API_KEY = os.environ.get("QM_VIDEO_API_KEY", "")
OUTPUT_FORMAT = os.environ.get("QM_VIDEO_OUTPUT_FORMAT", "webp")
FPS = int(os.environ.get("QM_VIDEO_FPS", "16"))
SECONDS = float(os.environ.get("QM_VIDEO_SECONDS", "3"))
SIZE = os.environ.get("QM_VIDEO_SIZE", "672x384")
FRAME_STEP = int(os.environ.get("QM_VIDEO_FRAME_STEP", "4"))
FRAME_OFFSET = int(os.environ.get("QM_VIDEO_FRAME_OFFSET", "1"))
PORT = int(os.environ.get("QM_VIDEO_PORT", "8081"))
STEPS = int(os.environ["QM_VIDEO_STEPS"]) if os.environ.get("QM_VIDEO_STEPS") else None
_DEFAULT_W, _DEFAULT_H = (int(n) for n in re.fullmatch(r"(\d+)x(\d+)", SIZE).groups())
MAX_PIXELS = int(os.environ.get("QM_VIDEO_MAX_PIXELS", str(_DEFAULT_W * _DEFAULT_H)))

# Quartermaster/sd-server job states -> the states Open WebUI waits for (completed or failed end the wait).
STATUS = {"queued": "queued", "generating": "in_progress", "completed": "completed",
          "failed": "failed", "cancelled": "failed"}


def webp_to_gif(data):
    """Animated WebP -> looping GIF, keeping each frame's duration."""
    from PIL import Image, ImageSequence  # pylint: disable=import-outside-toplevel
    clip = Image.open(io.BytesIO(data))
    frames, durations = [], []
    for frame in ImageSequence.Iterator(clip):
        frames.append(frame.convert("RGB").convert("P", palette=Image.Palette.ADAPTIVE, colors=256))
        durations.append(frame.info.get("duration", round(1000 / FPS)))
    out = io.BytesIO()
    frames[0].save(out, format="GIF", save_all=True, append_images=frames[1:], duration=durations, loop=0,
                   disposal=2, optimize=False)
    return out.getvalue()


def frames_for(seconds):
    """Smallest frame count on the model's grid that covers the requested length."""
    want = max(1, round(seconds * FPS))
    n = max(0, -(-(want - FRAME_OFFSET) // FRAME_STEP))
    return FRAME_STEP * n + FRAME_OFFSET


def parse_size(value, image=None):
    """Requested WxH; without one, the start image's aspect ratio at the default size's pixel count
    (sides rounded to multiples of 16), so a square still is not squeezed into a landscape clip."""
    m = re.fullmatch(r"\s*(\d+)\s*[xX]\s*(\d+)\s*", value or "")
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.fullmatch(r"(\d+)x(\d+)", SIZE)
    width, height = int(m.group(1)), int(m.group(2))
    if image:
        try:
            from PIL import Image  # pylint: disable=import-outside-toplevel
            image_width, image_height = Image.open(io.BytesIO(image)).size
        except Exception:  # pylint: disable=broad-except
            return width, height
        area, ratio = width * height, image_width / image_height
        width = max(16, round((area * ratio) ** 0.5 / 16) * 16)
        height = max(16, round((area / ratio) ** 0.5 / 16) * 16)
    return width, height


def cap_pixels(width, height):
    """Scale WxH down to at most MAX_PIXELS, aspect ratio kept, sides floored to multiples of 16."""
    if width * height <= MAX_PIXELS:
        return width, height
    scale = (MAX_PIXELS / (width * height)) ** 0.5
    return max(16, int(width * scale) // 16 * 16), max(16, int(height * scale) // 16 * 16)


def parse_form(content_type, body):
    """multipart/form-data or JSON -> (fields, files); files map name -> (content type, bytes)."""
    if content_type.startswith("application/json"):
        return json.loads(body or b"{}"), {}
    message = email.parser.BytesParser(policy=email.policy.HTTP).parsebytes(
        b"Content-Type: " + content_type.encode() + b"\r\n\r\n" + body)
    fields, files = {}, {}
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        payload = part.get_payload(decode=True) or b""
        if part.get_filename() is not None:
            files[name] = (part.get_content_type(), payload)
        else:
            fields[name] = payload.decode("utf-8", "replace")
    return fields, files


# sd-server 79dc7ca reads a "model" field on /sdcpp/v1/vid_gen as a model-catalog selection object and answers the
# model name with 400 "expected an object". Quartermaster's /upstream/<model>/ passthrough routes by path instead, so
# the body carries no model, and the video id the client sees is "<model>--<job id>" so status calls find the model.
ID_SEP = "--"


def job_path(video_id):
    model, _, job = video_id.partition(ID_SEP)
    return "/upstream/%s/sdcpp/v1/jobs/%s" % (urllib.parse.quote(model, safe=""), urllib.parse.quote(job, safe=""))


def quartermaster(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(QM_URL + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
    if QM_API_KEY:
        request.add_header("Authorization", "Bearer " + QM_API_KEY)
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as error:
        text = error.read().decode("utf-8", "replace")
        try:
            return error.code, json.loads(text)
        except ValueError:
            return error.code, {"error": {"message": text[:500]}}
    except (urllib.error.URLError, OSError) as error:
        # Quartermaster not up yet (the adapter starts first) or restarting: a clean error, not a dropped connection.
        return 503, {"error": {"message": "Quartermaster is not reachable: %s" % error}}


def video_object(job):
    status = STATUS.get(job.get("status"), job.get("status") or "queued")
    out = {"id": job.get("id"), "object": "video", "status": status, "created_at": job.get("created")}
    if status == "failed":
        error = job.get("error")
        message = error.get("message") if isinstance(error, dict) else error
        out["error"] = {"message": message or "the video job " + str(job.get("status"))}
    return out


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def send(self, code, body, content_type="application/json"):
        if not isinstance(body, bytes):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def path_parts(self):
        path = self.path.split("?", 1)[0].rstrip("/")
        if path.startswith("/v1/"):
            path = path[3:]
        return [p for p in path.split("/") if p]

    def do_GET(self):
        parts = self.path_parts()
        if parts == ["health"]:
            return self.send(200, {"status": "ok"})
        if len(parts) in (2, 3) and parts[0] == "videos" and (len(parts) == 2 or parts[2] == "content"):
            if ID_SEP not in parts[1]:
                return self.send(404, {"error": {"message": "unknown video id"}})
            code, job = quartermaster("GET", job_path(parts[1]))
            if code != 200:
                return self.send(code, job)
            job["id"] = parts[1]
            if len(parts) == 2:
                return self.send(200, video_object(job))
            result = job.get("result") or {}
            if job.get("status") != "completed" or not result.get("b64_json"):
                return self.send(409, {"error": {"message": "the video is not ready"}})
            data = base64.b64decode(result["b64_json"])
            mime = result.get("mime_type") or "application/octet-stream"
            if OUTPUT_FORMAT == "gif" and mime == "image/webp":
                data, mime = webp_to_gif(data), "image/gif"
            return self.send(200, data, mime)
        return self.send(404, {"error": {"message": "not found"}})

    def do_POST(self):
        parts = self.path_parts()
        if parts != ["videos"]:
            return self.send(404, {"error": {"message": "not found"}})
        length = int(self.headers.get("Content-Length") or 0)
        fields, files = parse_form(self.headers.get("Content-Type", ""), self.rfile.read(length))
        if not fields.get("model") or not fields.get("prompt"):
            return self.send(400, {"error": {"message": "model and prompt are required"}})
        image = files.get("input_reference")
        asked = parse_size(fields.get("size"), image[1] if image else None)
        width, height = cap_pixels(*asked)
        seconds = float(fields.get("seconds") or fields.get("duration") or SECONDS)
        # The job's shape only (never the prompt): what was asked, what is rendered.
        sys.stderr.write("video job: size %s -> %dx%d%s, %.1f s -> %d frames\n" % (
            fields.get("size") or "default", width, height,
            " (capped from %dx%d)" % asked if asked != (width, height) else "", seconds, frames_for(seconds)))
        payload = {
            "prompt": fields["prompt"],
            "negative_prompt": fields.get("negative_prompt", ""),
            "width": width,
            "height": height,
            "seed": int(fields.get("seed", -1)),
            "video_frames": frames_for(seconds),
            "fps": FPS,
            "output_format": "webp" if OUTPUT_FORMAT == "gif" else OUTPUT_FORMAT,
        }
        if STEPS is not None:
            payload["steps"] = STEPS
        if image:
            mime, data = image
            payload["init_image"] = "data:%s;base64,%s" % (mime or "image/png", base64.b64encode(data).decode())
        model = fields["model"]
        code, job = quartermaster("POST", "/upstream/%s/sdcpp/v1/vid_gen" % urllib.parse.quote(model, safe=""), payload)
        if code not in (200, 202):
            return self.send(code, job)
        job["id"] = model + ID_SEP + str(job.get("id"))
        return self.send(200, video_object(job))

    def log_message(self, fmt, *args):
        # Open WebUI polls every few seconds while a clip renders; log only requests that are not status polls.
        if self.command == "GET" and re.fullmatch(r"/(v1/)?videos/[^/]+", self.path.split("?", 1)[0]):
            return
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


class DualStackServer(ThreadingHTTPServer):
    """Listen on IPv6 and IPv4: pasta can forward a published port to the container over either."""
    address_family = socket.AF_INET6

    def server_bind(self):
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()


if __name__ == "__main__":
    DualStackServer(("::", PORT), Handler).serve_forever()
