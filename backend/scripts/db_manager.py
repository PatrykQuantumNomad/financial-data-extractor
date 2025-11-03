#!/usr/bin/env python3
"""
Database management utility script for development.

This script provides database inspection utilities that complement Alembic migrations.
For migrations, use: make migrate (or alembic upgrade head)

Usage (via Makefile - recommended):
    make db-list-companies  # List all companies in database
    make db-info            # Show database info and migration status

Usage (direct):
    python scripts/db_manager.py list-companies      # List all companies in database
    python scripts/db_manager.py info                # Show database info and migration status
    python scripts/db_manager.py cleanup-company <id> # Clean up data for a company (keeps company record)

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
from app.db.models.document import Document
from app.db.models.extraction import CompiledStatement, Extraction


def run_alembic_command(command: str):
    """Run an alembic command."""
    result = subprocess.run(
        f"alembic {command}",
        shell=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parent.parent,
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
                    exchanges = [t.get("exchange", "N/A") for t in company.tickers]
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


def cleanup_company_data(company_id: int):
    """Clean up all data for a company (documents, extractions, compiled_statements) while keeping the company record.

    This allows you to rerun the extraction process for a company from scratch.

    Args:
        company_id: The ID of the company to clean up.

    Returns:
        0 on success, 1 on error.
    """
    db = SessionLocal()
    try:
        # Verify company exists
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            print(f"Error: Company with ID {company_id} not found.", file=sys.stderr)
            return 1

        print(f"Cleaning up data for company: {company.name} (ID: {company_id})")
        print("-" * 60)

        # Count records before deletion
        doc_count = db.query(Document).filter(Document.company_id == company_id).count()
        extract_count = (
            db.query(Extraction).join(Document).filter(Document.company_id == company_id).count()
        )
        compiled_count = (
            db.query(CompiledStatement).filter(CompiledStatement.company_id == company_id).count()
        )

        print("Records to be deleted:")
        print(f"  - Documents: {doc_count}")
        print(f"  - Extractions: {extract_count}")
        print(f"  - Compiled Statements: {compiled_count}")

        if doc_count == 0 and extract_count == 0 and compiled_count == 0:
            print("\nNo data to clean up. Company record will remain unchanged.")
            return 0

        # Delete in order (respecting foreign key constraints)
        # 1. Compiled statements (standalone, no dependencies)
        if compiled_count > 0:
            deleted_compiled = (
                db.query(CompiledStatement)
                .filter(CompiledStatement.company_id == company_id)
                .delete()
            )
            print(f"\n✓ Deleted {deleted_compiled} compiled statement(s)")

        # 2. Documents (this will cascade delete extractions via FK constraint)
        if doc_count > 0:
            deleted_docs = db.query(Document).filter(Document.company_id == company_id).delete()
            print(f"✓ Deleted {deleted_docs} document(s) (and their extractions via CASCADE)")

        # Commit the transaction
        db.commit()

        print("\n" + "=" * 60)
        print("Cleanup completed successfully!")
        print(f"Company record for '{company.name}' (ID: {company_id}) has been preserved.")
        print("You can now rerun the extraction process for this company.")
        return 0

    except Exception as e:
        db.rollback()
        print(f"Error cleaning up company data: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1
    finally:
        db.close()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1].lower()

    # Handle cleanup-company command which requires an ID argument
    if command == "cleanup-company":
        if len(sys.argv) < 3:
            print("Error: cleanup-company requires a company ID", file=sys.stderr)
            print("Usage: python scripts/db_manager.py cleanup-company <company_id>")
            return 1
        try:
            company_id = int(sys.argv[2])
            return cleanup_company_data(company_id)
        except ValueError:
            print(
                f"Error: Invalid company ID '{sys.argv[2]}'. Must be an integer.", file=sys.stderr
            )
            return 1

    commands = {
        "list-companies": list_companies,
        "info": info,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print(__doc__)
        return 1

    return commands[command]()


if __name__ == "__main__":
    sys.exit(main())
