"""add subscription fields to organisations

Revision ID: 37ecc6911fc9
Revises: db70148c9922
Create Date: 2026-05-31 17:20:11.072135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '37ecc6911fc9'
down_revision: Union[str, Sequence[str], None] = 'db70148c9922'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('organisations', sa.Column('subscription_tier', sa.String(length=50), nullable=False, server_default='free'))
    op.add_column('organisations', sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
    op.add_column('organisations', sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True))
    op.add_column('organisations', sa.Column('subscription_status', sa.String(length=50), nullable=False, server_default='active'))
    op.add_column('organisations', sa.Column('assessment_count_this_month', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('organisations', sa.Column('assessment_reset_date', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('organisations', 'assessment_reset_date')
    op.drop_column('organisations', 'assessment_count_this_month')
    op.drop_column('organisations', 'subscription_status')
    op.drop_column('organisations', 'stripe_subscription_id')
    op.drop_column('organisations', 'stripe_customer_id')
    op.drop_column('organisations', 'subscription_tier')
