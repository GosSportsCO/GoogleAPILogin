from pydantic import BaseModel, EmailStr, Field, field_validator
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterForm(BaseModel):
    email: EmailStr
    password: str = Field(...)
    first_name: str
    last_name: str
    username: str

    @field_validator('password')
    def hash_password(cls, value):
        return bcrypt_context.hash(value)
