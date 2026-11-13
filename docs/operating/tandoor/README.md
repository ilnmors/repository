# tandoor

| Item | Value |
| --- | --- |
| Host | app |
| Version (2026-11-13) | 2.7.2 |

## Notes

- 2.7 dropped `HIDE_LOGIN_FORM`; the new login page reads `SOCIALACCOUNT_ONLY`.

## Login

`SOCIALACCOUNT_ONLY=1`. Break-glass sign-in: `/accounts/login/?form=1` (per upstream docs).
