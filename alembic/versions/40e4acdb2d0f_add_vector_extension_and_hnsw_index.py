"""Add vector extension and HNSW index

Revision ID: 40e4acdb2d0f
Revises: 5449fbd7e244
Create Date: 2025-04-24 19:26:47.539729

"""
from typing import Sequence, Union

import pgvector.sqlalchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40e4acdb2d0f'
down_revision: Union[str, None] = '5449fbd7e244'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.create_table('message_vector',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=1536), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.execute("CREATE INDEX idx_message_vector_hnsw "
               "ON message_vector USING hnsw (embedding vector_l2_ops) "
               "WITH (m = 32, ef_construction = 64);")


def downgrade() -> None:
    op.drop_index(
        f'ix_message_vector_embedding_hnsw',
        table_name='message_vector'
    )
    op.drop_table('message_vector')
    op.execute("DROP EXTENSION vector;")
