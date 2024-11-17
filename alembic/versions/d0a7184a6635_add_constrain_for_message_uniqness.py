"""add constrain for message uniqueness

Revision ID: d0a7184a6635
Revises: 3884a621bef1
Create Date: 2024-10-09 21:15:37.090175

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d0a7184a6635"
down_revision: Union[str, None] = "3884a621bef1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("source_message_uniq", "message", ["original_message_id", "channel_id"])


def downgrade() -> None:
    op.drop_constraint("source_message_uniq", "message", type_="unique")
