"""add original msg id

Revision ID: 3884a621bef1
Revises: 64a1d73f3453
Create Date: 2024-09-21 20:05:55.477332

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3884a621bef1"
down_revision: Union[str, None] = "64a1d73f3453"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("message", sa.Column("original_message_id", sa.Integer(), nullable=True))
    op.execute("UPDATE message SET original_message_id = 0")
    op.alter_column("message", "original_message_id", nullable=False)


def downgrade() -> None:
    op.drop_column("message", "original_message_id")
