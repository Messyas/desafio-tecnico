"""add auth and product schema

Revision ID: c7b8d4e9f2a1
Revises: 9e04db8451d3
Create Date: 2026-02-11 09:45:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c7b8d4e9f2a1"
down_revision = "9e04db8451d3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column(
        "user",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )
    op.execute('UPDATE "user" SET email = name || \'@local.test\' WHERE email IS NULL')
    op.execute('UPDATE "user" SET password_hash = \'\' WHERE password_hash IS NULL')
    op.alter_column("user", "email", nullable=False)
    op.alter_column("user", "password_hash", nullable=False)
    op.create_index("ix_user_email", "user", ["email"], unique=False)

    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("marca", sa.String(length=255), nullable=False),
        sa.Column("valor", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("product")
    op.drop_index("ix_user_email", table_name="user")
    op.drop_column("user", "password_hash")
    op.drop_column("user", "email")
