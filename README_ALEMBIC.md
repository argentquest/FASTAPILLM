# Database Migrations with Alembic

This project uses Alembic for database schema versioning and migrations.

## Setup

The database will be automatically initialized when you start the application. However, you can also run migrations manually.

## Manual Migration Commands

### Run all migrations
```bash
alembic upgrade head
```

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### View migration history
```bash
alembic history
```

### Downgrade to previous migration
```bash
alembic downgrade -1
```

### View current migration version
```bash
alembic current
```

## Project Structure

```
alembic/
├── env.py              # Alembic environment configuration
├── script.py.mako      # Template for new migrations
└── versions/           # Migration files
    └── 001_initial_migration.py  # Initial schema

alembic.ini            # Alembic configuration file
```

## Notes

- The database URL is configured in `alembic.ini` and can be overridden with the `DATABASE_URL` environment variable
- On application startup, migrations are automatically applied
- If Alembic fails for any reason, the app falls back to SQLAlchemy's `create_all()` method