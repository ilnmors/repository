#!/usr/bin/env python3
"""Register or update Ansible-managed Open WebUI functions (filters) on startup.

Runs inside the Open WebUI container via ExecStartPost after /health is ready,
so database migrations are complete and no extra API key endpoints need to be exposed.
User-edited valves and activation flags on existing rows are preserved; content and
metadata are synced whenever the mounted source file changes, and retired managed
function ids are removed cleanly.
"""
import asyncio
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:%s" % os.environ.get("PORT", "8080")
MANAGED_FUNCTIONS = [
    {
        "id": "qwen_image_2_1_guide",
        "name": "Qwen-Image-2.1 Prompt Guide",
        "type": "filter",
        "description": "Injects Qwen-Image-2.1 prompt safeguards (no literal N-head tokens, positive phrasing for CFG 1.0, 32-multiple sizes) when image generation is active.",
        "path": "/app/functions/qwen-image-filter.py",
        "is_active": True,
        "is_global": True,
    },
]
RETIRED_FUNCTION_IDS = [
    "flux2_klein_lora_guide",
]


def wait_for_health(timeout_s: int = 900) -> None:
    deadline = time.time() + timeout_s
    while True:
        try:
            with urllib.request.urlopen(BASE + "/health", timeout=10) as resp:
                if resp.status == 200:
                    return
        except (urllib.error.URLError, OSError):
            pass
        if time.time() > deadline:
            sys.exit("Open WebUI did not answer /health within %ds" % timeout_s)
        time.sleep(5)


async def sync_all() -> None:
    from sqlalchemy import select
    from open_webui.internal.db import get_async_db_context
    from open_webui.models.functions import FunctionForm, FunctionMeta, Functions
    from open_webui.models.users import User

    async with get_async_db_context() as session:
        row = (
            await session.execute(select(User.id).where(User.role == "admin").limit(1))
        ).first()
        user_id = row[0] if row else "system"

    for retired_id in RETIRED_FUNCTION_IDS:
        existing = await Functions.get_function_by_id(retired_id)
        if existing is not None:
            await Functions.delete_function_by_id(retired_id)
            print(f"sync-functions: removed retired {retired_id}", flush=True)

    for spec in MANAGED_FUNCTIONS:
        src = pathlib.Path(spec["path"])
        if not src.is_file():
            print("sync-functions: skipping missing", src, flush=True)
            continue
        content = src.read_text(encoding="utf-8")
        meta = FunctionMeta(description=spec["description"], manifest={})
        existing = await Functions.get_function_by_id(spec["id"])
        if existing is None:
            form = FunctionForm(
                id=spec["id"],
                name=spec["name"],
                content=content,
                meta=meta,
                commit_message="initial register via sync-functions.py",
            )
            created = await Functions.insert_new_function(user_id, spec["type"], form)
            if created is None:
                sys.exit(f"sync-functions: failed to insert {spec['id']}")
            await Functions.update_function_by_id(
                spec["id"],
                {"is_active": spec["is_active"], "is_global": spec["is_global"]},
                user_id=user_id,
            )
            print(f"sync-functions: registered {spec['id']} (active={spec['is_active']}, global={spec['is_global']})", flush=True)
        else:
            if existing.content != content or existing.name != spec["name"]:
                await Functions.update_function_by_id(
                    spec["id"],
                    {
                        "name": spec["name"],
                        "content": content,
                        "meta": meta.model_dump(),
                    },
                    user_id=user_id,
                )
                print(f"sync-functions: updated {spec['id']}", flush=True)
            else:
                print(f"sync-functions: up-to-date {spec['id']}", flush=True)


def main() -> None:
    wait_for_health()
    asyncio.run(sync_all())


if __name__ == "__main__":
    main()
