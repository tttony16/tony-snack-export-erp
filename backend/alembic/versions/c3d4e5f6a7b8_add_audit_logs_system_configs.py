"""add audit_logs and system_configs tables

Revision ID: c3d4e5f6a7b8
Revises: b7c8d9e0f1a2
Create Date: 2026-02-27 18:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID

revision = "c3d4e5f6a7b8"
down_revision = "b7c8d9e0f1a2"
branch_labels = None
depends_on = None

audit_action = ENUM(
    "create",
    "update",
    "delete",
    "export",
    "status_change",
    "login",
    "logout",
    "permission_change",
    name="audit_action",
    create_type=False,
)


def upgrade() -> None:
    # Create audit_action enum type
    audit_action_type = ENUM(
        "create",
        "update",
        "delete",
        "export",
        "status_change",
        "login",
        "logout",
        "permission_change",
        name="audit_action",
    )
    audit_action_type.create(op.get_bind(), checkfirst=True)

    # --- audit_logs ---
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("action", audit_action, nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("detail", JSONB, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    # --- system_configs ---
    op.create_table(
        "system_configs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("config_key", sa.String(200), unique=True, nullable=False),
        sa.Column("config_value", JSONB, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.Column(
            "updated_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
    )
    op.create_index("ix_system_configs_config_key", "system_configs", ["config_key"])

    # Insert default configs
    op.execute(
        """
        INSERT INTO system_configs (config_key, config_value, description)
        VALUES
            ('shelf_life_threshold', '0.667', '保质期阈值比例（剩余/总保质期 < 此值则告警）'),
            ('default_shipping_days', '30', '默认运输天数')
        ON CONFLICT (config_key) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_table("system_configs")
    op.drop_table("audit_logs")
    op.execute("DROP TYPE IF EXISTS audit_action")
