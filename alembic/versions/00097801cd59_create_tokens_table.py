"""create tokens table

Revision ID: 00097801cd59
Revises:
Create Date: 2020-08-10 15:48:35.203807

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "00097801cd59"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tokens",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("namespace", sa.String, unique=True, nullable=False),
        sa.Column("repository", sa.String, unique=True, nullable=False),
        sa.Column("token", sa.String, unique=True, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
    )


def downgrade():
    op.drop_table("tokens")
