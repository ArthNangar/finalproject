from pydantic import BaseModel, EmailStr, Field

class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class ProfileUpdateIn(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr

class PasswordChangeIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
