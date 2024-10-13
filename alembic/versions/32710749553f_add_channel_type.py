"""add channel_type

Revision ID: 32710749553f
Revises: bf2c897124a9
Create Date: 2024-10-12 12:10:21.561330

"""

from email.policy import default
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from src.models import NOT_SPECIFIED_CHANNEL_TYPE

# revision identifiers, used by Alembic.
revision: str = "32710749553f"
down_revision: Union[str, None] = "bf2c897124a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "channel_type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type_", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("channel", sa.Column("type_id", sa.Integer(), nullable=True, default=0))

    op.execute(f"INSERT INTO channel_type (id, type_) VALUES (0, '{NOT_SPECIFIED_CHANNEL_TYPE}')")
    op.execute('INSERT INTO channel_type (type_) SELECT DISTINCT "type" FROM channel WHERE "type" IS NOT NULL')
    op.execute(
        "UPDATE channel SET type_id = (" " SELECT id FROM channel_type" " WHERE channel_type.type_ = channel.type);"
    )

    op.drop_column("channel", "type")
    op.create_foreign_key("channel_channel_type_fkey", "channel", "channel_type", ["type_id"], ["id"])


def downgrade() -> None:
    op.add_column("channel", sa.Column("type", sa.VARCHAR(), nullable=True))
    op.execute('UPDATE channel SET "type" = (SELECT type_ FROM channel_type WHERE channel_type.id = channel.type_id)')

    op.drop_constraint("channel_channel_type_fkey", "channel", type_="foreignkey")
    op.drop_column("channel", "type_id")
    op.drop_table("channel_type")
