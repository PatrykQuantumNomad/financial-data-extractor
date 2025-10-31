"""
Seed initial companies.

Revision ID: 002
Revises: 001
Create Date: 2025-01-30 12:00:01.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Integer, String
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Seed initial companies for the take-home test."""

    # Create a simple table representation for inserting data
    companies_table = table(
        'companies',
        column('name', String),
        column('ticker', String),
        column('ir_url', String)
    )

    # Insert initial companies
    op.bulk_insert(
        companies_table,
        [
            {
                'name': 'Adyen',
                'ticker': 'ADYEN',
                'ir_url': 'https://www.adyen.com/investors'
            },
            {
                'name': 'Heineken',
                'ticker': 'HEIA',
                'ir_url': 'https://www.theheinekencompany.com/investors'
            }
        ]
    )


def downgrade() -> None:
    """Remove seeded companies."""

    # Delete the seeded companies by ticker
    op.execute(
        "DELETE FROM companies WHERE ticker IN ('ADYEN', 'HEIA')"
    )
