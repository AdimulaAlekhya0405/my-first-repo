from pydantic import BaseModel
from typing import Optional

class SignUpModel(BaseModel):
     id: Optional[int]
     username: str 
     email:str
     password:str
     is_staff:Optional[bool]=None
     is_active: Optional[bool] = None

     class Config:
          orm_mode=True
          schema_extra={
               'example': {
                    "username": "johndoe",
                    "email": "johndoe@gmail.com",
                    "password": "password",
                    "is_staff": False,
                    "is-active": True
               }
          }
    
class Settings(BaseModel):
     authjwt_secret_Key:str='9fa8e74509005930161a09b89ae7ec7bc34721797c88d22c550641c3ce63acf6'

class LoginModel(BaseModel):
     username: str
     password:str

class OrderModel(BaseModel):
    id: Optional[int]
    quantity:int
    choices:Optional[str]="PENDING"
    pizza_size:Optional[str]="SMALL"
    user_id: Optional[int]
    
    class Config:
         orm_mode=True
         schema_extra={
              "example": {
                   "quantity": 2,
                   "choices": "PENDING",
                   "pizza_size": "LARGE"
              }
         }
         


