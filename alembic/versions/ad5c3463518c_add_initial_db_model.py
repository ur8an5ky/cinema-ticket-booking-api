"""Add initial db model

Revision ID: ad5c3463518c
Revises: 31de2ba66b41
Create Date: 2023-05-15 10:43:04.072521

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad5c3463518c'
down_revision = '31de2ba66b41'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cinemas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('location', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('movies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('age_restrictions', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('trailer_link', sa.String(length=255), nullable=True),
    sa.Column('duration_minutes', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('repertoir',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cinema_id', sa.Integer(), nullable=True),
    sa.Column('movie_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cinema_id'], ['cinemas.id'], ),
    sa.ForeignKeyConstraint(['movie_id'], ['movies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('screenings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('repertoir_id', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('room_number', sa.Integer(), nullable=False),
    sa.Column('translation', sa.Enum('Dubbing', 'Subtitles', 'Voice-over', name='translation_types'), nullable=False),
    sa.Column('image_format', sa.Enum('2D', '3D', name='image_formats'), nullable=False),
    sa.Column('ticket_price', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['repertoir_id'], ['repertoir.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reservations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('screening_id', sa.Integer(), nullable=True),
    sa.Column('seat_number', sa.Integer(), nullable=False),
    sa.Column('row_number', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['screening_id'], ['screenings.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('screening_id', 'seat_number', 'row_number', name='uq_screening_seat_row')
    )
    op.add_column('users', sa.Column('date_of_birth', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'date_of_birth')
    op.drop_table('reservations')
    op.drop_table('screenings')
    op.drop_table('repertoir')
    op.drop_table('movies')
    op.drop_table('cinemas')
    op.drop_table('categories')
    # ### end Alembic commands ###
