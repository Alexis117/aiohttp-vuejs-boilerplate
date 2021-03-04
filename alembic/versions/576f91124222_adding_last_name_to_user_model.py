"""Adding last_name to user model

Revision ID: 576f91124222
Revises: 8549b26106eb
Create Date: 2021-03-03 19:35:25.825500

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '576f91124222'
down_revision = '8549b26106eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_name')
    # ### end Alembic commands ###
