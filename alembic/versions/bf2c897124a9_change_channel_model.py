"""change channel model

Revision ID: bf2c897124a9
Revises: d0a7184a6635
Create Date: 2024-10-11 10:34:46.334197

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bf2c897124a9"
down_revision: Union[str, None] = "d0a7184a6635"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("message_channel_id_fkey", "message", type_="foreignkey")

    op.alter_column("channel", "channel_id", new_column_name="id")

    op.drop_column("channel", "channel_type")
    op.add_column("channel", sa.Column("type", sa.String(), nullable=True))

    op.add_column("channel", sa.Column("name", sa.String(), nullable=True))

    op.create_foreign_key("message_channel_id_fkey", "message", "channel", ["channel_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("message_channel_id_fkey", "message", type_="foreignkey")

    op.alter_column("channel", "id", new_column_name="channel_id")

    op.drop_column("channel", "type")
    op.add_column("channel", sa.Column("channel_type", sa.Integer(), nullable=True))

    op.drop_column("channel", "name")

    op.create_foreign_key("message_channel_id_fkey", "message", "channel", ["channel_id"], ["channel_id"])
