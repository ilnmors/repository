# searxng

| Item | Value |
| --- | --- |
| Host | app (8012 → 8080), internal domain `searxng.app.ilnmors.internal`; containers on app use `host.containers.internal:8012` |
| Version (2026-11-22) | 2026.11.6-ac11e14c5 (`docker.io/searxng/searxng`) |

## Notes

- Metasearch backend for Open WebUI's web search (`WEB_SEARCH_ENGINE=searxng`, `SEARXNG_QUERY_URL=http://host.containers.internal:8012/search?q=<query>`); Open WebUI asks for `format=json`, so `search.formats` includes json.
- `settings.yml` lists only the differences from the image defaults (`use_default_settings: true`); the default engine set is kept.
- No limiter and no Valkey: the instance has no public route and one client.
- `server.secret_key` comes from the podman secret `SEARXNG_SECRET` (`secrets.searxng.secret_key`, generated on the first run of the task).
- `/etc/searxng` and `/var/cache/searxng` are owned by subuid 100976 (searxng, uid 977, in the container), so the entrypoint does not chown them.
- Searches leave from the home IP; heavy use can trigger CAPTCHAs on single engines, which SearXNG then suspends for a while.
