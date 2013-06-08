"""added deploy settings for generic config

Revision ID: 2c1344d382f5
Revises: 1fd0c05a2eb
Create Date: 2013-06-07 21:52:04.208072

"""

# revision identifiers, used by Alembic.
revision = '2c1344d382f5'
down_revision = '1fd0c05a2eb'

from alembic import op
import sqlalchemy as sa
from app.lib import JSONEncodedDict



def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('deploy_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('namespace', sa.String(length=255), nullable=True),
    sa.Column('simple_data', sa.Text(), nullable=True),
    sa.Column('json_data', JSONEncodedDict, nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('deploy_settings')
    ### end Alembic commands ###