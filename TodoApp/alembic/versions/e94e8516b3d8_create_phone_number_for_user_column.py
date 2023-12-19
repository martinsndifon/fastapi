"""Create phone number for user column

Revision ID: e94e8516b3d8
Revises:
Create Date: 2023-12-19 12:39:15.291313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e94e8516b3d8"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("phone_number", sa.String(length=20), nullable=True, unique=True),
    )


def downgrade() -> None:
    op.drop_column("users", "phone_number")
