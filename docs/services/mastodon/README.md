# mastodon

| Item | Value |
| --- | --- |
| Host | app |
| Version (2026-11-13) | v4.7.5 |

## Login

`OMNIAUTH_ONLY=true`.

## Local patches

- Files under `ansible/roles/containers/templates/mastodon/patches/` are mounted read-only over the image's copies in the web and worker containers. `releases.yaml` lists each one with the SHA256 of the upstream file it was made from, and the deploy stops when the image's copy differs (`ansible/roles/containers/tasks/check-patches.yaml`), so a new tag forces the patches to be ported.
- `vips_lazy_thumbnail.rb`, `media_attachment.rb`: animated WebP stays animated WebP, and GIF uploads become WebP instead of an MP4 gifv.
- `media_attachment.rb` (2026-11-27): uploads up to 50 MB for images and 1 GB for videos (upstream 16 MB and 99 MB), videos cut after 216,000 frames (an hour at 60 fps), and images kept up to 7680×4320 px (upstream 3840×2160).
- `media_controller.rb`, `post_status_service.rb`, `post_process_media_worker.rb` (2026-11-27): videos, audio and GIFs uploaded through `POST /api/v1/media` are processed in the background as in v2, so clients that wait only a few seconds for the upload answer (Flare waits 10 s) no longer fail while the video is transcoded. A post may carry media that is still processing and shows it once the worker is done; if the processing fails for good, the worker removes the post and its media.
