# StudExEl Architecture

## Project Structure

```
StudExEl/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── extensions.py
│   │
│   ├── models/
│   ├── routes/
│   ├── forms/
│   ├── templates/
│   ├── static/
│   │
│   └── database/
│
├── database/
│   ├── schools.csv
│   ├── seed_schools.py
│   └── studexel.db
│
├── docs/
│
├── requirements.txt
│
└── README.md
```

---

## Architecture Pattern

StudExEl follows the MVC (Model-View-Controller) pattern.

### Models

Responsible for database structure.

Examples:

- User
- School
- Category

### Views

HTML templates displayed to users.

### Controllers

Flask routes responsible for processing requests and responses.

---

## Future Architecture

Additional folders planned:

- services/
- utils/
- migrations/
- tests/