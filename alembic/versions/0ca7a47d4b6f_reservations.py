"""reservations

Revision ID: 0ca7a47d4b6f
Revises: 3e90acda5d9c
Create Date: 2023-04-02 18:33:34.979778

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ca7a47d4b6f'
down_revision = '3e90acda5d9c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reservations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('date_reservation', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('people_count', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('comment', sa.String(length=1024), nullable=True),
    sa.Column('admin_comment', sa.String(length=1024), nullable=True),
    sa.Column('createdAt', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updatedAt', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reservations')
    # ### end Alembic commands ###
