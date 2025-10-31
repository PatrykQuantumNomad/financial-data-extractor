#!/usr/bin/env python3
"""
Database management utility script for development.

Usage:
    python scripts/db_manager.py migrate      # Run all pending migrations
    python scripts/db_manager.py reset        # Drop all tables and re-migrate
    python scripts/db_manager.py seed         # Seed database with test data
    python scripts/db_manager.py status       # Show migration status
"""

import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.base import Base, SessionLocal, engine
from app.db.models.company import Company


def run_alembic_command(command: str):
    """Run an alembic command."""
    result = subprocess.run(
        f"alembic {command}",
        shell=True,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def migrate():
    """Run all pending migrations."""
    print("Running database migrations...")
    return run_alembic_command("upgrade head")


def reset():
    """Drop all tables and re-run migrations."""
    print("Resetting database (this will drop all data)...")
    response = input("Are you sure? Type 'yes' to continue: ")

    if response.lower() != 'yes':
        print("Reset cancelled.")
        return 1

    print("Dropping all tables...")
    run_alembic_command("downgrade base")

    print("Running migrations...")
    return run_alembic_command("upgrade head")


def status():
    """Show current migration status."""
    print("Migration Status:")
    print("\nCurrent version:")
    run_alembic_command("current")
    print("\nMigration history:")
    return run_alembic_command("history")


def seed():
    """Seed database with additional test data (beyond migration seeds)."""
    print("Seeding database with test data...")

    db = SessionLocal()

    try:
        # Check if companies already exist
        existing = db.query(Company).count()

        if existing > 0:
            print(f"Database already has {existing} companies.")
            print("   Companies:")
            for company in db.query(Company).all():
                print(f"   - {company.name} ({company.ticker})")
            return 0

        # Add more test companies if needed
        print("Companies are seeded via migrations (002_seed_initial_companies.py)")
        print("   Run 'alembic upgrade head' to seed initial companies.")

        return 0

    except Exception as e:
        print(f"Error seeding database: {e}")
        return 1
    finally:
        db.close()


def create_db():
    """Create database (for development setup)."""
    print("Creating database tables (without Alembic)...")
    print("This is for development only. Use migrations in production!")

    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    # Also seed initial companies
    db = SessionLocal()
    try:
        if db.query(Company).count() == 0:
            companies = [
                Company(name='Adyen', ticker='ADYEN', ir_url='https://www.adyen.com/investors'),
                Company(name='Heineken', ticker='HEIA', ir_url='https://www.theheinekencompany.com/investors')
            ]
            db.add_all(companies)
            db.commit()
            print("Seeded initial companies.")
        else:
            print("Companies already exist, skipping seed.")
    finally:
        db.close()

    return 0


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1].lower()

    commands = {
        'migrate': migrate,
        'reset': reset,
        'status': status,
        'seed': seed,
        'create': create_db,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print(__doc__)
        return 1

    return commands[command]()


if __name__ == '__main__':
    sys.exit(main())
