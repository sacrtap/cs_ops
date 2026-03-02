"""empty message

Revision ID: 7f7a503fce4d
Revises: 002, 710228662a7a
Create Date: 2026-03-02 10:47:23.998201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f7a503fce4d'
down_revision: Union[str, Sequence[str], None] = ('002', '710228662a7a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
