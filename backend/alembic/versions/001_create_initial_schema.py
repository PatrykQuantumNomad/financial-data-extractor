"""
Create initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-30 12:00:00.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all initial tables for the financial data extractor."""

    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('ir_url', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticker')
    )
    op.create_index(op.f('ix_companies_id'), 'companies', ['id'], unique=False)
    op.create_index(op.f('ix_companies_ticker'), 'companies', ['ticker'], unique=True)

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_company_id'), 'documents', ['company_id'], unique=False)
    op.create_index(op.f('ix_documents_fiscal_year'), 'documents', ['fiscal_year'], unique=False)

    # Create extractions table
    op.create_table(
        'extractions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('statement_type', sa.String(length=50), nullable=False),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_extractions_id'), 'extractions', ['id'], unique=False)
    op.create_index(op.f('ix_extractions_document_id'), 'extractions', ['document_id'], unique=False)
    op.create_index(op.f('ix_extractions_statement_type'), 'extractions', ['statement_type'], unique=False)

    # Create compiled_statements table
    op.create_table(
        'compiled_statements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('statement_type', sa.String(length=50), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'statement_type', name='uq_company_statement_type')
    )
    op.create_index(op.f('ix_compiled_statements_id'), 'compiled_statements', ['id'], unique=False)
    op.create_index(op.f('ix_compiled_statements_company_id'), 'compiled_statements', ['company_id'], unique=False)
    op.create_index(op.f('ix_compiled_statements_statement_type'), 'compiled_statements', ['statement_type'], unique=False)


def downgrade() -> None:
    """Drop all tables in reverse order."""

    # Drop compiled_statements table
    op.drop_index(op.f('ix_compiled_statements_statement_type'), table_name='compiled_statements')
    op.drop_index(op.f('ix_compiled_statements_company_id'), table_name='compiled_statements')
    op.drop_index(op.f('ix_compiled_statements_id'), table_name='compiled_statements')
    op.drop_table('compiled_statements')

    # Drop extractions table
    op.drop_index(op.f('ix_extractions_statement_type'), table_name='extractions')
    op.drop_index(op.f('ix_extractions_document_id'), table_name='extractions')
    op.drop_index(op.f('ix_extractions_id'), table_name='extractions')
    op.drop_table('extractions')

    # Drop documents table
    op.drop_index(op.f('ix_documents_fiscal_year'), table_name='documents')
    op.drop_index(op.f('ix_documents_company_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')

    # Drop companies table
    op.drop_index(op.f('ix_companies_ticker'), table_name='companies')
    op.drop_index(op.f('ix_companies_id'), table_name='companies')
    op.drop_table('companies')
