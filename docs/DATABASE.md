# Database Documentation

## Database Engine

SQLite (Development)

Future:

- PostgreSQL (Production)

---

## Current Tables

### Users

Stores student accounts.

### Schools

Stores participating colleges and universities.

### Categories

Stores marketplace item categories.

---

## Planned Tables

- Listings
- Messages
- Reviews
- Favorites
- Verification
- Notifications
- Reports
- Transactions

---

## Relationships

School

↓

Users

↓

Listings

↓

Transactions

---

## Data Integrity

Future improvements:

- Foreign key constraints
- Unique indexes
- Database migrations