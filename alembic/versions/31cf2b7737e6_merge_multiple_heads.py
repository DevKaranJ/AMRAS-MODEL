"""merge multiple heads

Revision ID: 31cf2b7737e6
Revises: 1775c1189b9d, bf6d04ac8efd
Create Date: 2026-07-10 08:58:18.907776

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "31cf2b7737e6"
down_revision: Union[str, Sequence[str], None] = ("1775c1189b9d", "bf6d04ac8efd")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
