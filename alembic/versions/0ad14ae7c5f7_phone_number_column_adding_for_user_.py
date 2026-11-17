"""phone number column adding for user table

Revision ID: 0ad14ae7c5f7
Revises: 
Create Date: 2026-11-15 21:07:10.175979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ad14ae7c5f7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',sa.Column('phone_number'),sa.String(20),nullable=True)

def downgrade() -> None:
    """Downgrade schema."""
    pass
