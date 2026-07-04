"""add proceeded_despite_warning to site_risk_checks

Revision ID: 3e62d5ef3e89
Revises: bb3349e05c3f
Create Date: 2026-07-04 03:20:04.608459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3e62d5ef3e89'
down_revision: Union[str, None] = 'bb3349e05c3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Hand-trimmed: autogenerate also picked up pre-existing drift between the
# models and the DB (timezone-aware columns, index/FK names) that predates
# this change and was already reconciled via `alembic stamp` in the initial
# revision — only the actual new column belongs in this migration.


def upgrade() -> None:
    op.add_column('site_risk_checks', sa.Column('proceeded_despite_warning', sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column('site_risk_checks', 'proceeded_despite_warning')
