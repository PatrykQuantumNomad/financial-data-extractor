"""
Seed initial companies.

Revision ID: 002
Revises: 001
Create Date: 2025-01-30 12:00:01.000000

"""
import json
import re

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def parse_tickers(ticker_string: str) -> tuple[str | None, list[dict[str, str]]]:
    """
    Parse ticker string into primary ticker and structured tickers list.

    Examples:
        "AZN (LSE, NASDAQ)" -> ("AZN", [{"ticker": "AZN", "exchange": "LSE"}, {"ticker": "AZN", "exchange": "NASDAQ"}])
        "ULVR (LSE), UNA (Euronext Amsterdam), UL (NYSE)" -> ("ULVR", [{"ticker": "ULVR", "exchange": "LSE"}, ...])
    """
    if not ticker_string:
        return None, []

    tickers_list = []
    primary_ticker = None

    # Pattern to match: "TICKER (EXCHANGE1, EXCHANGE2)" or "TICKER (EXCHANGE)"
    # Also handles: "TICKER1 (EXCHANGE1), TICKER2 (EXCHANGE2)"

    # First, split by commas that are NOT inside parentheses
    parts = re.split(r',\s*(?![^()]*\))', ticker_string)

    for part in parts:
        part = part.strip()
        # Match "TICKER (EXCHANGE1, EXCHANGE2, ...)"
        match = re.match(r'^([A-Z0-9]+)\s*\(([^)]+)\)', part)
        if match:
            ticker = match.group(1)
            exchanges_str = match.group(2)

            # Set first ticker as primary
            if primary_ticker is None:
                primary_ticker = ticker

            # Split exchanges by comma
            exchanges = [ex.strip() for ex in exchanges_str.split(',')]

            for exchange in exchanges:
                tickers_list.append({
                    'ticker': ticker,
                    'exchange': exchange
                })
        else:
            # Fallback: if no parentheses, treat whole string as ticker
            if not primary_ticker:
                primary_ticker = part
                tickers_list.append({
                    'ticker': part,
                    'exchange': None
                })

    return primary_ticker, tickers_list


def upgrade() -> None:
    """Seed initial companies from CSV data."""

    # Companies data
    companies_data = [
        {
            'name': 'AstraZeneca PLC',
            'ticker_string': 'AZN (LSE, NASDAQ)',
            'ir_url': 'https://www.astrazeneca.com/investor-relations/annual-reports.html'
        },
        {
            'name': 'SAP SE',
            'ticker_string': 'SAP (XETRA, NYSE)',
            'ir_url': 'https://www.sap.com/investors/en/financial-documents-and-events.html'
        },
        {
            'name': 'Siemens AG',
            'ticker_string': 'SIE (XETRA)',
            'ir_url': 'https://www.siemens.com/global/en/company/investor-relations/events-publications-ad-hoc/annualreports.html'
        },
        {
            'name': 'ASML Holding N.V.',
            'ticker_string': 'ASML (Euronext Amsterdam, NASDAQ)',
            'ir_url': 'https://www.asml.com/en/investors/annual-report'
        },
        {
            'name': 'Unilever PLC',
            'ticker_string': 'ULVR (LSE), UNA (Euronext Amsterdam), UL (NYSE)',
            'ir_url': 'https://www.unilever.com/investors/annual-report-and-accounts/'
        },
        {
            'name': 'Allianz SE',
            'ticker_string': 'ALV (XETRA)',
            'ir_url': 'https://www.allianz.com/en/investor_relations/results-reports/annual-reports.html'
        }
    ]

    # Parse and prepare companies for insertion
    companies_to_insert = []
    for company in companies_data:
        primary_ticker, tickers_list = parse_tickers(company['ticker_string'])
        companies_to_insert.append({
            'name': company['name'],
            'primary_ticker': primary_ticker,
            'tickers': json.dumps(tickers_list) if tickers_list else None,
            'ir_url': company['ir_url']
        })

    # Insert companies using raw SQL to handle JSONB properly
    conn = op.get_bind()
    for company in companies_to_insert:
        tickers_json = company['tickers'] if company['tickers'] else None
        primary_ticker = company['primary_ticker']

        # Handle NULL tickers case separately to avoid casting issues
        if tickers_json:
            stmt = text("""
                INSERT INTO companies (name, primary_ticker, tickers, ir_url)
                VALUES (:name, :primary_ticker, CAST(:tickers AS jsonb), :ir_url)
            """)
            params = {
                'name': company['name'],
                'primary_ticker': primary_ticker,
                'tickers': tickers_json,
                'ir_url': company['ir_url']
            }
        else:
            stmt = text("""
                INSERT INTO companies (name, primary_ticker, tickers, ir_url)
                VALUES (:name, :primary_ticker, NULL, :ir_url)
            """)
            params = {
                'name': company['name'],
                'primary_ticker': primary_ticker,
                'ir_url': company['ir_url']
            }

        conn.execute(stmt, params)


def downgrade() -> None:
    """Remove seeded companies."""

    # Delete the seeded companies by name
    op.execute(
        """
        DELETE FROM companies
        WHERE name IN (
            'AstraZeneca PLC',
            'SAP SE',
            'Siemens AG',
            'ASML Holding N.V.',
            'Unilever PLC',
            'Allianz SE'
        )
        """
    )
