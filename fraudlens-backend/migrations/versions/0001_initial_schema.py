"""Initial complete schema for FraudLens AI

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-20 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Companies Master Dataset
    op.create_table(
        'companies',
        sa.Column('cin', sa.String(length=100), primary_key=True),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('normalized_name', sa.String(length=255), nullable=False),
        sa.Column('company_status', sa.String(length=50), nullable=False),
        sa.Column('company_class', sa.String(length=100), nullable=True),
        sa.Column('company_category', sa.String(length=100), nullable=True),
        sa.Column('registered_state', sa.String(length=100), nullable=True),
        sa.Column('registrar_of_companies', sa.String(length=150), nullable=True),
        sa.Column('date_of_registration', sa.String(length=50), nullable=True),
        sa.Column('brand_name', sa.String(length=150), nullable=True),
        sa.Column('official_domain', sa.String(length=150), nullable=True),
        sa.Column('official_website', sa.String(length=255), nullable=True),
        sa.Column('domain_status', sa.String(length=100), nullable=True),
        sa.Column('domain_match_type', sa.String(length=100), nullable=True),
        sa.Column('primary_authority', sa.String(length=255), nullable=True),
        sa.Column('reference_dataset', sa.String(length=255), nullable=True),
        sa.Column('verification_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_companies_normalized_name', 'companies', ['normalized_name'])
    op.create_index('ix_companies_official_domain', 'companies', ['official_domain'])
    op.create_index('ix_companies_brand_name', 'companies', ['brand_name'])
    op.create_index('ix_companies_status', 'companies', ['company_status'])

    # Spam URLs Threat Feed
    op.create_table(
        'spam_urls',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('normalized_url', sa.String(length=1000), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_spam_urls_normalized_url', 'spam_urls', ['normalized_url'])
    op.create_index('ix_spam_urls_domain', 'spam_urls', ['domain'])

    # Investigations
    op.create_table(
        'investigations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), default='PENDING', nullable=False),
        sa.Column('risk_score', sa.Float(), default=0.0, nullable=False),
        sa.Column('risk_level', sa.String(length=50), default='LOW', nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('target_entity', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_investigations_user_id', 'investigations', ['user_id'])
    op.create_index('ix_investigations_type', 'investigations', ['type'])

    # Evidence
    op.create_table(
        'evidence',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('investigation_id', sa.String(length=36), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('signal', sa.String(length=150), nullable=False),
        sa.Column('observed_value', sa.String(length=255), nullable=True),
        sa.Column('reference_value', sa.String(length=255), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Float(), default=1.0, nullable=False),
        sa.Column('risk_contribution', sa.Float(), default=0.0, nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_evidence_investigation_id', 'evidence', ['investigation_id'])

    # Risk Factors
    op.create_table(
        'risk_factors',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('investigation_id', sa.String(length=36), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('weight', sa.Float(), default=1.0, nullable=False),
        sa.Column('contribution', sa.Float(), default=0.0, nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_risk_factors_investigation_id', 'risk_factors', ['investigation_id'])

    # Investigation Results (Persistent Derived Outcome)
    op.create_table(
        'investigation_results',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('investigation_id', sa.String(length=36), sa.ForeignKey('investigations.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('recommendation', sa.Text(), nullable=False),
        sa.Column('evidence_json', sa.JSON(), nullable=False),
        sa.Column('risk_factors_json', sa.JSON(), nullable=False),
        sa.Column('verification_json', sa.JSON(), nullable=False),
        sa.Column('attack_patterns_json', sa.JSON(), nullable=False),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_investigation_results_user_id', 'investigation_results', ['user_id'])

    # Uploaded Files (Tracked for End-Task Deletion)
    op.create_table(
        'uploaded_files',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('investigation_id', sa.String(length=36), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('stored_path', sa.String(length=500), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('uploaded_files')
    op.drop_table('investigation_results')
    op.drop_table('risk_factors')
    op.drop_table('evidence')
    op.drop_table('investigations')
    op.drop_table('spam_urls')
    op.drop_table('companies')
    op.drop_table('users')
