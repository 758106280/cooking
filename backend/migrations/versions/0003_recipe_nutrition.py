"""Add optional nutrition information to recipes."""

import sqlalchemy as sa
from alembic import op


revision = "0003_recipe_nutrition"
down_revision = "0002_user_profile"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("recipes")}
    if "nutrition" not in columns:
        op.add_column("recipes", sa.Column("nutrition", sa.Text(), nullable=True))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("recipes")}
    if "nutrition" in columns:
        op.drop_column("recipes", "nutrition")
