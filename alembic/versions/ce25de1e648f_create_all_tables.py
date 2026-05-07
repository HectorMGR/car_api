"""create all tables

Revision ID: ce25de1e648f
Revises: 
Create Date: 2026-04-12 19:55:36.916536

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'DEJÁ_EL_QUE_TENGA'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'brands',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    op.create_table(
        'currencies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(3), nullable=False),
        sa.Column('symbol', sa.String(5), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )

    op.create_table(
        'vehicle_status',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    op.create_table(
        'models',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'vehicles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency_id', sa.Integer(), nullable=False),
        sa.Column('status_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['model_id'], ['models.id']),
        sa.ForeignKeyConstraint(['currency_id'], ['currencies.id']),
        sa.ForeignKeyConstraint(['status_id'], ['vehicle_status.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'vehicle_images',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('vehicle_images')
    op.drop_table('vehicles')
    op.drop_table('models')
    op.drop_table('vehicle_status')
    op.drop_table('currencies')
    op.drop_table('brands')