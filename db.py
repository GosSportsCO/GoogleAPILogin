import databases
import sqlalchemy



DATABASE_URL = f"postgresql://postgres:Brian0625@127.0.0.1:5432/test_db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()



"""
users: Table contains structure for users
"""
user = sqlalchemy.Table(
    "user_account",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(60), nullable=False),
    sqlalchemy.Column("first_name", sqlalchemy.String(120), nullable=False),
    sqlalchemy.Column("last_name", sqlalchemy.String(120), nullable=False),  # Asegúrate de que no haya espacio al final
    sqlalchemy.Column("username", sqlalchemy.String(120), nullable=False),   # Asegúrate de que no haya espacio al final
)


async def create_or_update_user(user_data):
    query = sqlalchemy.select([user.c.id]).where(user.c.email == user_data["email"])
    result = await database.fetch_one(query)
    user_id = result["id"] if result else None
    
    if user_id is None:
        # Insert new user
        query = user.insert().values(
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            username=user_data["username"]
        )
        last_record_id = await database.execute(query)
        return {"id": last_record_id, **user_data}