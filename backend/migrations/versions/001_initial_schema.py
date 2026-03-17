"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-03-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'role_briefs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('thread_id', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'VALIDATING', 'GENERATING', 'CHECKING', 'PENDING_REVIEW', 'PUBLISHED', 'FAILED', name='rolebriefstatus'), nullable=False),
        sa.Column('role_title', sa.String(), nullable=False),
        sa.Column('team', sa.String(), nullable=False),
        sa.Column('seniority', sa.String(), nullable=False),
        sa.Column('work_type', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('must_have_skills', sa.JSON(), nullable=False),
        sa.Column('nice_to_have_skills', sa.JSON(), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=False),
        sa.Column('salary_max', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('headcount', sa.Integer(), nullable=False),
        sa.Column('years_of_experience', sa.Integer(), nullable=True),
        sa.Column('reports_to', sa.String(), nullable=True),
        sa.Column('key_outcomes', sa.JSON(), nullable=True),
        sa.Column('context_note', sa.Text(), nullable=True),
        sa.Column('tone_preference', sa.String(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_briefs_id'), 'role_briefs', ['id'], unique=False)
    op.create_index(op.f('ix_role_briefs_thread_id'), 'role_briefs', ['thread_id'], unique=True)

    op.create_table(
        'job_descriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_brief_id', sa.Integer(), nullable=False),
        sa.Column('thread_id', sa.String(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'PENDING_REVIEW', 'PUBLISHED', name='jdstatus'), nullable=False),
        sa.Column('jd_content', sa.JSON(), nullable=False),
        sa.Column('guardrail_passed', sa.Integer(), nullable=False),
        sa.Column('guardrail_issues', sa.JSON(), nullable=True),
        sa.Column('guardrail_corrected_jd', sa.JSON(), nullable=True),
        sa.Column('tone_score', sa.Float(), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['role_brief_id'], ['role_briefs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_descriptions_id'), 'job_descriptions', ['id'], unique=False)
    op.create_index(op.f('ix_job_descriptions_thread_id'), 'job_descriptions', ['thread_id'], unique=False)

    op.create_table(
        'sourcing_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_brief_id', sa.Integer(), nullable=False),
        sa.Column('job_description_id', sa.Integer(), nullable=False),
        sa.Column('thread_id', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', name='sourcingqueuestatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['job_description_id'], ['job_descriptions.id'], ),
        sa.ForeignKeyConstraint(['role_brief_id'], ['role_briefs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sourcing_queue_id'), 'sourcing_queue', ['id'], unique=False)
    op.create_index(op.f('ix_sourcing_queue_thread_id'), 'sourcing_queue', ['thread_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_sourcing_queue_thread_id'), table_name='sourcing_queue')
    op.drop_index(op.f('ix_sourcing_queue_id'), table_name='sourcing_queue')
    op.drop_table('sourcing_queue')
    
    op.drop_index(op.f('ix_job_descriptions_thread_id'), table_name='job_descriptions')
    op.drop_index(op.f('ix_job_descriptions_id'), table_name='job_descriptions')
    op.drop_table('job_descriptions')
    
    op.drop_index(op.f('ix_role_briefs_thread_id'), table_name='role_briefs')
    op.drop_index(op.f('ix_role_briefs_id'), table_name='role_briefs')
    op.drop_table('role_briefs')
    
    sa.Enum(name='sourcingqueuestatus').drop(op.get_bind())
    sa.Enum(name='jdstatus').drop(op.get_bind())
    sa.Enum(name='rolebriefstatus').drop(op.get_bind())
