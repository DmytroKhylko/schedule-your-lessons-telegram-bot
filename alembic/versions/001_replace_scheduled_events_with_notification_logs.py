"""Replace scheduled_events with notification_logs

Revision ID: 001
Revises:
Create Date: 2026-05-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS scheduled_events CASCADE")
    op.execute("DROP TYPE IF EXISTS event_type")
    op.execute("DROP TYPE IF EXISTS event_status")

    notification_type = sa.Enum("lesson_reminder", "new_assignment", name="notification_type")
    notification_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("schedule_id", sa.Integer(), sa.ForeignKey("schedules.id"), nullable=False),
        sa.Column("occurrence_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notification_type", notification_type, nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint(
            "user_id", "schedule_id", "occurrence_time", "notification_type",
            name="uq_notification_log_entry",
        ),
    )


def downgrade() -> None:
    op.drop_table("notification_logs")
    op.execute("DROP TYPE IF EXISTS notification_type")
