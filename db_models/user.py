import sqlalchemy
from db import metadata

"""
users: Table contains structure for users
"""
user = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("email", sqlalchemy.String(60), nullable=False),
    sqlalchemy.Column("password_hash", sqlalchemy.String(120)),
    sqlalchemy.Column("first_name", sqlalchemy.String(30), nullable=False),
    sqlalchemy.Column("last_name", sqlalchemy.String(30), nullable=False),
    sqlalchemy.Column("username", sqlalchemy.String(60), nullable=False),
    sqlalchemy.Column("oauth_channel", sqlalchemy.String(20), nullable=False),
    sqlalchemy.Column("device_type", sqlalchemy.String(20), nullable=False),
    sqlalchemy.Column("os_name", sqlalchemy.String(20), nullable=False),
    sqlalchemy.Column("browser_name", sqlalchemy.String(20), nullable=False),
    sqlalchemy.Column("client_host", sqlalchemy.String(20), nullable=False),
)
