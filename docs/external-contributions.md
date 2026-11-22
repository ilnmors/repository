# External contributions

Issues, pull requests and comments posted upstream for the stacks this repository runs. Rules for new posts are in
AGENT.md ("External contributions"). Surface Laptop 7 posts are recorded in the `surface-laptop7-debian` bundle
(`docs/EXTERNAL-CONTRIBUTIONS.md`).

| Date (UTC) | Stack | Where | Kind | Subject | State |
| --- | --- | --- | --- | --- | --- |
| 2026-11-12 | OxiCloud | [AtalayaLabs/OxiCloud #880](https://github.com/AtalayaLabs/OxiCloud/pull/880) | PR | fix(auth): accept two-character usernames in setup and OIDC JIT | Merged 2026-11-21 (`8dfda52`) |

## OxiCloud #880

- Problem here: OIDC JIT provisioning replaced the 2-character LDAP id `il` with `user_<sub>`, and first-admin setup
  rejected 2-character names, while `validate_username` and the `users_username_shape_v2` check already allow 2.
- Change: both lower bounds set to 2 (`src/application/services/auth_application_service.rs`).
- Review: rebase requested and done (2026-11-18); clippy asked about, answered after running `just check` unchanged
  (`--all-features`, clean on rustc 1.100.0).
- Not in a release yet (latest v0.10.1, 2026-11-18). Until then keep the rename step in
  [operating/oxicloud](operating/oxicloud/README.md).
- Left upstream: the admin "create user" form still has a client-side 3-character check (`minlength="3"`).
- The fork `ilnmors/OxiCloud` held only this branch (the others were copied from upstream when it was forked); it
  and the local clone were deleted 2026-11-22.
