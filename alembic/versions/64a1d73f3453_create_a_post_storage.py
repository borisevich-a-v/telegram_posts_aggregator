"""Create a post storage

Revision ID: 64a1d73f3453
Revises: cba6952028e3
Create Date: 2024-06-20 16:31:11.199545

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "64a1d73f3453"
down_revision: Union[str, None] = "cba6952028e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "channel",
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("channel_type", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("channel_id"),
    )
    op.create_table(
        "message",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("grouped_id", sa.BigInteger(), nullable=True),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("sent", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel.channel_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_table("messages")


def downgrade() -> None:
    op.create_table(
        "messages",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("message_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("grouped_id", sa.BIGINT(), autoincrement=False, nullable=True),
        sa.Column("sent", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="messages_pkey"),
    )
    op.drop_table("message")
    op.drop_table("channel")
