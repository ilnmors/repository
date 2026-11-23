# readur

| Item | Value |
| --- | --- |
| Host | app |
| Version (2026-11-13) | 3.1.2 |
| Replaces | papra |

## Storage

- Database: PostgreSQL `readur_db` (owner `readur`), daily `postgresql-data-backup@readur.timer`.
- Documents: RustFS bucket `readur` through `https://rustfs.<public domain>` with path-style addressing. The `readur` service account may only list, read, write and delete in that bucket.
- `~/data/containers/readur/uploads` keeps only local working files (thumbnails, temporary files).

## Login

- OIDC only (`ALLOW_LOCAL_AUTH=false`). Authelia client `readur`: PKCE S256 and `client_secret_basic`, both required by Readur.
- First OIDC login creates a regular user (`OIDC_AUTO_REGISTER=true`). Readur has no group-to-role mapping, so promote administrators once in the database:

  ```sql
  UPDATE users SET role = 'admin', updated_at = NOW()
  WHERE username = '<user>' AND auth_provider = 'oidc';
  ```

  Later logins find the user by its OIDC subject and keep the role.
- Readur also creates a local `admin` account on first start (password in `uploads/.readur/initial-admin-password`); it cannot log in while local login is off.

## Details tab patch

- Readur always opens a document on the Text tab, which shows the extracted text. The deploy task copies the drawer chunk (`/app/frontend/dist/assets/DocumentDrawer-<hash>.js`) out of the image, changes the two `text` tab defaults to `details`, and mounts the result read-only over the original.
- The chunk name changes with every Readur build, so the task looks it up per image. The deploy stops if the two defaults are not found exactly once, so an upgrade never serves an unpatched or broken drawer.

## Settings

- OCR: `eng+kor`, two concurrent jobs.
- Upload limit: 200 MB (the largest Papra document was 53 MB; the default is 50 MB).

## Migration from Papra (2026-11-13)

- All Papra documents were uploaded through the API with a temporary API key of the owner account, revoked afterwards. SHA-256 hashes match the Papra originals.
- `created_at` and `original_created_at` were set to the document date (00:00 local time) so lists sort by document date.
- File names were normalized (no spaces, one numbering style). Details and the naming rule are in the private notes, [private/notes.md](private/notes.md) (outside Git).
