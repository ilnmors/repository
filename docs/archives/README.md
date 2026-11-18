# Archived stacks

Stacks that are not part of the active repository, kept in the current repository schema so they can be brought back without re-deriving them from the old homelab layout. Nothing here is loaded by Ansible.

| Path | Contents |
| --- | --- |
| `services.yaml`, `releases.yaml` | Entries in the same schema as `ansible/inventory/group_vars/repository/{services,releases}.yaml`. |
| `roles/containers/{tasks,templates,handlers}` | Container tasks following the active role conventions (PostgreSQL/MariaDB/Authelia/valkey includes, podman secrets, `deploy.yaml`, `nodes[...]['paths']`). `tasks/main.yaml` and `handlers/main.yaml` hold only the entries to append. |
| `roles/packages/{tasks,templates,handlers}` | Host packages and systemd services (blocky, wsl-alive, chromium). |
| `tools/extract_secret.sh` | Archived homelab secret helper, kept verbatim. |

All templates render against the current repository variables (with `secrets` stubbed), and the task files pass `ansible-lint` (production profile) when merged into a copy of `ansible/`.

## Why each stack is here

Reasons come from the homelab notes, commit messages and the owner (2026-11-12). The last column names the active service with a similar role.

### Archived in homelab

| Stack | Archived | Reason | Similar active service |
| --- | --- | --- | --- |
| affine | before 2026-06-17 | Heavy, and the whiteboard/canvas features were not used enough; Outline was released as its replacement (`1256122`). The community edition also limits workspace seats to 10 and adds storage quotas (`affine.md`). | outline |
| trilium | 2026-05-09 (`4527e39`) | OIDC was unstable: users could not get in on the first attempt and had to log in twice (`02fa912`, `trilium.md`). | outline, bookstack |
| vikunja | 2026-05-09 (`4527e39`) | No local + OIDC dual login, so the local fallback was removed (`d1e0eb3`, `vikunja.md`); Nextcloud groupware was to replace it (`278dd3c`). | nextcloud (groupware), kaneo |
| opencloud | 2026-05-09 (`4527e39`) | Official desktop/mobile apps hardcode the OIDC client IDs and scopes, so no group claim and no role control; role mapping has no regex and needed manual `proxy.yaml` edits per user (`opencloud.md`). Nextcloud was to replace it (`278dd3c`). | oxicloud |
| actual-budget | 2026-05-09 (`4527e39`) | Its particular budgeting workflow did not fit (owner's note). | sure |
| ezbookkeeping | 2026-05-09 (`4527e39`) | No multi-user support for family use (no per-user access control). | sure |
| wikijs | 2026-05-09 (`4527e39`) | Too heavy and complex for family use. | bookstack, outline |
| bonfire | 2026-07-05 (`e0df8cf`, Mastodon release) | Did not work properly. | mastodon |
| paperless | 2026-07-09 (`3a38271`, Papra release) | Too heavy, and the UI/UX was poor. | readur |
| memos | 2026-08-23 (`56fb571`) | Too light as a social service, and overlapped with Outline for notes. | - |
| booklogr | 2026-08-29 (`9226043`) | Rarely used. | - |
| linkwarden | 2026-08-29 (`9226043`) | Too limited unless its internal Chromium is enabled. | linkding |
| mealie | 2026-08-29 (`9226043`) | Not used. | tandoor |
| romm | 2026-08-29 (`9226043`) | Not used. | - |
| ovms | 2026-09-09 (`99536c5`) | Replaced by llama.cpp. | llama |
| chromium (console) | 2026-05-11 (`0afc841`) | Not used. | - |
| extract_secret.sh | 2026-05-15 (`a7e2320`) | Not used. | `ansible/roles/secrets/files/scripts/edit_secret.sh` |

Readur, archived on 2026-07-09 with the Papra release, was moved back to `ansible/` on 2026-11-13 to replace Papra (see `docs/operating/readur/README.md`).

### Stopped on 2026-11-13

| Stack | Reason | Similar active service |
| --- | --- | --- |
| papra | Replaced by Readur; all documents were moved (see `docs/operating/readur/README.md`). Moved here from `ansible/`. | readur |
| nextcloud | Groupware no longer used. Calendars and contacts went to OxiCloud on 2026-11-12, user files on 2026-11-13 (sample files left out). | oxicloud |
| groupoffice | Groupware no longer used. Its user files were moved to OxiCloud on 2026-11-13. | oxicloud |

### Still running in homelab, not yet moved to the repository

homebox, llama and stablediffusion ran on the homelab `app` host when this archive was made. They are written in the repository schema here so they can be promoted into `ansible/` when needed. Nextcloud had been introduced as the groupware stack (`278dd3c`). tandoor was promoted into `ansible/` on 2026-11-17 (see `docs/operating/tandoor/README.md`).

### Superseded by an active repository service

| Archived | Replaced by | Note |
| --- | --- | --- |
| gitea | forgejo | Same port (3001) as forgejo; run only one. |
| maddy | postfix + dovecot | Same SMTP/IMAPS ports (2587/2993). |
| ca | step-ca | Same port (9000); uses the repository intermediate CA secrets. |
| redis | valkey | Archived stacks use the active `valkey.yaml` sidecar; `templates/redis` is the old shared template in the current form. |
| blocky | bind RPZ blocklist | The same blocklist URLs are in `services.packages.bind.units.main.blocklist`. fw no longer exists, so the entry targets vmm and needs `networks.segments.server.hosts.blocky`. |
| wsl-alive | - | Only for a WSL console. |

## Changes made while converting

- Ports that collide with active services were moved: llama 10000 → 10002, romm 8002 → 8008, memos 3005 → 3008, ovms 5000 → 5001. Stacks that had no port got free ones (actual-budget 5006, affine 3010 + manticore 9308, bonfire 4001, ezbookkeeping 8009, opencloud 9200, paperless 8010, trilium 8012, wikijs 3011). Valkey sidecars: nextcloud 6380, romm 6384, affine 6385, paperless 6386.
- Redis sidecars became the repository valkey sidecar (`units.valkey`, `valkey_<service>.service`).
- `hostvars['fw']` addresses were replaced by `containers_trusted_proxies` and `networks.segments.server.hosts`; certificates use `secrets.ca.x509.{root,intermediate,leaf}`.
- The secrets key for Actual Budget is `actual-budget` (homelab used `actualbudget`).
- Random application secrets (session keys, salts, JWT secrets) are generated into `secrets.yaml` on first deploy, like the active roles do.
- `stablediffusion` is pinned by digest (`master-sycl@sha256:...`); check that `deploy.yaml` pulls a tag of that form before promoting it.

## Bringing a stack back

1. Copy its `services.yaml` and `releases.yaml` entries into `ansible/inventory/group_vars/repository/`.
2. Copy `roles/<role>/tasks/<stack>.yaml` and `roles/<role>/templates/<stack>/`, then append its block from `tasks/main.yaml` and `handlers/main.yaml`.
3. Add the secrets below (OIDC stacks also need `<stack>.oidc.hash` for the Authelia client).
4. Authelia: the active template does not yet render `claims_policy`, CORS or public clients. linkwarden, romm and trilium need an ID-token claims policy (`dependency.oidc.claims`), booklogr and opencloud need CORS, and opencloud needs public PKCE clients (plus the desktop/mobile clients in the old homelab config).
5. Model-backed stacks (llama, stablediffusion, ovms) sync models from `<data>/containers/<stack>/models/`; place the models there first.

| Stack | secrets.yaml keys |
| --- | --- |
| actual-budget | actual-budget.oidc.{secret,hash} |
| affine | affine.secret_key (ed25519 PEM), affine.oidc.{secret,hash}, postgresql.password.affine |
| bonfire | bonfire.{session_secret,session_salt,encrypt_salt,release_cookie} (generated), bonfire.oidc.{secret,hash}, postgresql.password.bonfire |
| booklogr | booklogr.secret_key (generated), booklogr.oidc.{secret,hash}, postgresql.password.booklogr |
| ca | ca.x509.intermediate.{crt,key,password} |
| ezbookkeeping | ezbookkeeping.oidc.{secret,hash}, postgresql.password.ezbookkeeping |
| gitea | gitea.oidc.{secret,hash}, postgresql.password.gitea |
| groupoffice | mariadb.password.groupoffice |
| homebox | homebox.api_secret (generated), homebox.oidc.{secret,hash}, postgresql.password.homebox |
| linkwarden | linkwarden.secret_key (generated), linkwarden.oidc.{secret,hash}, postgresql.password.linkwarden |
| maddy | ldap.password.services.maddy, postgresql.password.maddy, x509 leaf for `maddy` |
| mealie | mealie.oidc.{secret,hash}, postgresql.password.mealie |
| memos | memos.oidc.{secret,hash}, postgresql.password.memos |
| nextcloud | nextcloud.admin.{id,password}, nextcloud.oidc.{secret,hash}, postgresql.password.nextcloud |
| opencloud | opencloud.admin |
| papra | papra.secret_key (generated), papra.oidc.{secret,hash} |
| paperless | paperless.session_secret (generated), paperless.oidc.{secret,hash}, postgresql.password.paperless |
| romm | romm.secret_key (generated), romm.oidc.{secret,hash}, postgresql.password.romm |
| trilium | trilium.oidc.{secret,hash} |
| vikunja | vikunja.session_secret (generated), vikunja.oidc.{secret,hash}, postgresql.password.vikunja |
| wikijs | wikijs.oidc.{secret,hash}, postgresql.password.wikijs |
| blocky | x509 leaf for `blocky` |
