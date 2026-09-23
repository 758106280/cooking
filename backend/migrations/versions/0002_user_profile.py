"""Add nickname and avatar to users."""

import sqlalchemy as sa
from alembic import op


revision = "0002_user_profile"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "nickname" not in columns:
        op.add_column("users", sa.Column("nickname", sa.String(length=64), nullable=True))
    if "avatar" not in columns:
        op.add_column("users", sa.Column("avatar", sa.String(length=255), nullable=True))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "avatar" in columns:
        op.drop_column("users", "avatar")
    if "nickname" in columns:
        op.drop_column("users", "nickname")
