"""Add asset_document table

Revision ID: c117af3cf49b
Revises: b756275b3369
Create Date: 2025-09-21 12:23:16.585940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c117af3cf49b'
down_revision: Union[str, None] = 'b756275b3369'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('asset_document',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='ID automático de provento.'),
    sa.Column('asset_b3_code', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False, comment='Títutlo do documento.'),
    sa.Column('url', sa.String(), nullable=False, comment='URL do documento.'),
    sa.Column('publish_date', sa.Date(), nullable=False, comment='Data de publicação do documento.'),
    sa.ForeignKeyConstraint(['asset_b3_code'], ['asset.b3_code'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_asset_document_publish_date'), 'asset_document', ['publish_date'], unique=False)
    op.create_index(op.f('ix_asset_document_title'), 'asset_document', ['title'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_asset_document_title'), table_name='asset_document')
    op.drop_index(op.f('ix_asset_document_publish_date'), table_name='asset_document')
    op.drop_table('asset_document')
