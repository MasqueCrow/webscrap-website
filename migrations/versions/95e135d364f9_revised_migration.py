"""revised migration

Revision ID: 95e135d364f9
Revises:
Create Date: 2021-01-27 23:17:02.063269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95e135d364f9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("product") as batch_op:
        batch_op.drop_column('student_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('student_id', sa.INTEGER(), nullable=False))
    # ### end Alembic commands ###
