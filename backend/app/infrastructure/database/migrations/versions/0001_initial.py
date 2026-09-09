"""initial schema"""
from alembic import op
from app.infrastructure.database.models import Base
revision="0001"; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    bind=op.get_bind(); Base.metadata.create_all(bind=bind)
def downgrade():
    bind=op.get_bind(); Base.metadata.drop_all(bind=bind)
