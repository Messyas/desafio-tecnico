"""make user identifiers unique ci

Revision ID: 6f53f2e7c6d8
Revises: c7b8d4e9f2a1
Create Date: 2026-02-11 16:40:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6f53f2e7c6d8"
down_revision = "c7b8d4e9f2a1"
branch_labels = None
depends_on = None


def _raise_if_ci_duplicates_exist() -> None:
    bind = op.get_bind()

    duplicated_name = bind.execute(
        sa.text(
            """
            SELECT lower(name) AS normalized_name, COUNT(*) AS qty
            FROM "user"
            GROUP BY lower(name)
            HAVING COUNT(*) > 1
            LIMIT 1
            """
        )
    ).first()
    if duplicated_name is not None:
        raise RuntimeError(
            "Migration aborted: duplicate user.name values found (case-insensitive)."
        )

    duplicated_email = bind.execute(
        sa.text(
            """
            SELECT lower(email) AS normalized_email, COUNT(*) AS qty
            FROM "user"
            GROUP BY lower(email)
            HAVING COUNT(*) > 1
            LIMIT 1
            """
        )
    ).first()
    if duplicated_email is not None:
        raise RuntimeError(
            "Migration aborted: duplicate user.email values found (case-insensitive)."
        )


def upgrade():
    _raise_if_ci_duplicates_exist()

    op.execute('DROP INDEX IF EXISTS ix_user_email')
    op.execute('CREATE UNIQUE INDEX uq_user_email_ci ON "user" (lower(email))')
    op.execute('CREATE UNIQUE INDEX uq_user_name_ci ON "user" (lower(name))')


def downgrade():
    op.execute('DROP INDEX IF EXISTS uq_user_name_ci')
    op.execute('DROP INDEX IF EXISTS uq_user_email_ci')
    op.execute('CREATE INDEX IF NOT EXISTS ix_user_email ON "user" (email)')
