"""add normalized_title to food_logs

Revision ID: 7af8a7d32bfc
Revises: 
Create Date: 2025-06-16 16:53:00.384688

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7af8a7d32bfc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('target_calories', sa.Float(), nullable=True),
    sa.Column('target_protein', sa.Float(), nullable=True),
    sa.Column('target_carbs', sa.Float(), nullable=True),
    sa.Column('target_fats', sa.Float(), nullable=True),
    sa.Column('height', sa.Float(), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('activity_level', sa.String(), nullable=True),
    sa.Column('dietary_restrictions', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)
    op.create_table('food_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('food_description', sa.String(), nullable=True),
    sa.Column('normalized_title', sa.String(), nullable=True),
    sa.Column('meal_type', sa.String(), nullable=True),
    sa.Column('calories', sa.Float(), nullable=True),
    sa.Column('protein', sa.Float(), nullable=True),
    sa.Column('carbs', sa.Float(), nullable=True),
    sa.Column('fats', sa.Float(), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_food_logs_id'), 'food_logs', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_food_logs_id'), table_name='food_logs')
    op.drop_table('food_logs')
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
