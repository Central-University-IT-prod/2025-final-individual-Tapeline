"""add moderation_enabled flag

Revision ID: 690b6b4d1d0a
Revises: 780580a7ab34
Create Date: 2025-02-18 14:11:01.454600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '690b6b4d1d0a'
down_revision: Union[str, None] = '780580a7ab34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('moderation_enabled', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.create_unique_constraint(None, 'words_blacklist', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'words_blacklist', type_='unique')
    op.drop_column('settings', 'moderation_enabled')
    # ### end Alembic commands ###
