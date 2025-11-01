#!/usr/bin/env python3
"""
Database management utility script for development.

This script provides database inspection utilities that complement Alembic migrations.
For migrations, use: make migrate (or alembic upgrade head)

Usage (via Makefile - recommended):
    make db-list-companies  # List all companies in database
    make db-info            # Show database info and migration status

Usage (direct):
    python scripts/db_manager.py list-companies  # List all companies in database
    python scripts/db_manager.py info            # Show database info and migration status

Note: For migrations, use the Makefile commands:
    make migrate          # Run migrations
    make migrate-down     # Rollback migration
    make migrate-history  # Show migration history
    make db-reset         # Reset database
"""

import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.base import SessionLocal
from app.db.models.company import Company


def run_alembic_command(command: str):
    """Run an alembic command."""
    result = subprocess.run(
        f"alembic {command}",
        shell=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parent.parent
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def list_companies():
    """List all companies in the database."""
    print("Companies in database:")
    print("-" * 60)

    db = SessionLocal()
    try:
        companies = db.query(Company).all()

        if not companies:
            print("No companies found.")
            print("\nTo seed companies, run: make migrate")
            return 0

        for company in companies:
            ticker_display = company.primary_ticker or "No ticker"
            ticker_count = len(company.tickers) if company.tickers else 0
            print(f"  {company.name}")
            print(f"    Primary Ticker: {ticker_display}")
            if ticker_count > 0:
                print(f"    Total Tickers: {ticker_count}")
                if company.tickers:
                    exchanges = [t.get('exchange', 'N/A') for t in company.tickers]
                    print(f"    Exchanges: {', '.join(exchanges)}")
            print(f"    IR URL: {company.ir_url}")
            print()

        print(f"Total: {len(companies)} companies")
        return 0

    except Exception as e:
        print(f"Error querying database: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()


def info():
    """Show database information and migration status."""
    print("Database Information")
    print("=" * 60)

    # Show migration status
    print("\nMigration Status:")
    print("-" * 60)
    print("Current version:")
    run_alembic_command("current")
    print("\nMigration history:")
    run_alembic_command("history")

    # Show company count
    print("\n" + "=" * 60)
    print("Database Contents:")
    print("-" * 60)

    db = SessionLocal()
    try:
        company_count = db.query(Company).count()
        print(f"Companies: {company_count}")
    except Exception as e:
        print(f"Error querying database: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()

    print("\nFor more details, run: python scripts/db_manager.py list-companies")
    return 0


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1].lower()

    commands = {
        'list-companies': list_companies,
        'info': info,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print(__doc__)
        return 1

    return commands[command]()


if __name__ == '__main__':
    sys.exit(main())
