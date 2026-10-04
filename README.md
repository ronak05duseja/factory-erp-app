# Factory ERP (demo)

Minimal Flask app built for the ASDD Jira/GitHub traceability experiment.
Covers two Jira epics:

- **User Authentication** — register, login/logout, password strength
  validation, incomplete-credentials error handling.
- **Inventory Management** — view stock levels, low-stock alert.

## Endpoints

| Method | Path                        | Jira issue |
|--------|-----------------------------|------------|
| POST   | /api/register               | FE-9, FE-10 |
| POST   | /api/login                  | FE-11, FE-6 |
| POST   | /api/logout                 | FE-11 |
| GET    | /api/inventory               | FE-7 |
| GET    | /api/inventory/low-stock     | FE-12 |

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

## Run tests

```bash
pytest -v
```

## Commit convention

Every commit message includes the Jira issue key it addresses, e.g.:

```
FE-9: add user registration endpoint
FE-10: add password strength validation
FE-6: add incomplete-credentials error message
FE-11: add login/logout session handling
FE-7: add inventory listing endpoint
FE-12: add low-stock alert endpoint
```

This is what links commits to issues automatically once the
"GitHub for Jira" app is connected.
