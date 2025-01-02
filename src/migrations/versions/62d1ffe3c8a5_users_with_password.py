"""users_with_password

Revision ID: 62d1ffe3c8a5
Revises: 7ee8b43dcb46
Create Date: 2024-10-27 21:48:10.673831

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "62d1ffe3c8a5"
down_revision = "7ee8b43dcb46"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("password_hashed", sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "password_hashed")
    # ### end Alembic commands ###
