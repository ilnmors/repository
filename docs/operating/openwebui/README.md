# openwebui

| Item | Value |
| --- | --- |
| Host | app (8002) |
| Version (2026-11-13) | v0.13.3 |

## Notes

- Backend is [quartermaster](../quartermaster/README.md). Sure no longer uses Open WebUI as its AI gateway: its AI variables were removed on 2026-11-13, and API keys stay enabled for a later reconnection.
- Reset on 2026-11-15: the database was dropped and recreated (with the `vector` extension), and the data directory and the `open-webui` bucket were emptied. Accounts are created again on the first Authelia login.
- Models cannot create or save skills and memories on their own: `DEFAULT_MODEL_METADATA` sets `builtinTools.skills` and `builtinTools.memory` to `false`, and `ENABLE_MEMORY_BACKGROUND_REVIEW=false`. Skills and memories added by the user still apply (attached skills are inlined into the system prompt, memories into the system context). Model presets created later need the same `builtinTools` values.
- Images are requested at 512×512 (`IMAGE_SIZE`), see [quartermaster](../quartermaster/README.md).
- Files are stored in RustFS (`open-webui` bucket); vectors in PostgreSQL (pgvector).
- Library (2026-11-23): `/library/` is a files gallery (`templates/openwebui/library/index.html`, mounted read-only into `/app/build/library`), so Open WebUI serves it under its own login; without a valid token it sends the browser to `/auth?redirect=/library/`. It has a left sidebar (search, folders, type filter, summary) and opens on the folder overview, not on the files; clicking a file opens a viewer with its details and actions. Folders are the page's own: they live in the user's settings under the top-level key `library` (`{"folders": [...], "map": {"<file id>": "<folder id>"}}`), which Open WebUI does not read; new files are in "Unsorted". Renames and deletes go through Open WebUI's file API, so the database and the bucket stay in step. `loader.js` replaces the empty `/static/loader.js` hook (mounted over `/app/build/static/loader.js`, copied to the static folder at start) and adds a Library row below Workspace in the sidebar's user menu; check both after an Open WebUI upgrade.

## Login

`ENABLE_LOGIN_FORM=false`, `OAUTH_AUTO_REDIRECT=false`.
