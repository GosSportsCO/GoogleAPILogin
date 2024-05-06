import databases
import sqlalchemy
from decouple import config

DATABASE_URL = f"mysql+aiomysql://{config('DB_USER')}:{config('DB_PASSWORD')}@localhost:3306/gossports"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
