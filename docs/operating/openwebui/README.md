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

## Login

`ENABLE_LOGIN_FORM=false`, `OAUTH_AUTO_REDIRECT=false`.
