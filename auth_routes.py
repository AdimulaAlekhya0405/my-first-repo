from datetime import timedelta
from fastapi import APIRouter, Depends, Security, logger,status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from database import engine, AsyncSessionLocal
#from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import  SignUpModel,LoginModel
from models import User
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash,check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from pydantic import BaseSettings
from fastapi.logger import logger
from fastapi.security import HTTPBearer





auth_route=APIRouter(
    prefix="/auth"
)

class Settings(BaseSettings):
    authjwt_secret_key: str = "super-secret-key"
    authjwt_algorithm: str = "HS256"
    authjwt_access_token_expires: timedelta = timedelta(minutes=15)
    authjwt_refresh_token_expires: timedelta = timedelta(days=7)


@AuthJWT.load_config
def get_config():
    return Settings()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

session: AsyncSession = Depends(get_db)
#security= HTTPBearer
bearer_scheme = HTTPBearer(
    bearerFormat="JWT",
    scheme_name="BearerAuth",
    description="Enter JWT token in the format: Bearer <token>",
    auto_error=False
)


@auth_route.get("/")
async def aa(Authorize: AuthJWT=Depends(), credentials = Security(bearer_scheme) ):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid token")
    return {"message": "Hello world"}

@auth_route.post("/signup",response_model=SignUpModel,status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel,session: AsyncSession = Depends(get_db)):
    result=await session.execute(select(User).where(User.email==user.email))
    db_email= result.scalars().first()

    if db_email is not None:
        return HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="user with the email already exist")
    
    result1= await session.execute(select(User).where(User.username== user.username))
    db_username=result1.scalars().first()

    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with the username already exists")
    new_user=User(username=user.username,email=user.email,password=generate_password_hash(user.password),is_active=user.is_active,is_staff=user.is_staff)
    session.add(new_user)
    await session.commit()
    return new_user

@auth_route.post('/login')
async def login(user: LoginModel,Authorize: AuthJWT=Depends(),session: AsyncSession = Depends(get_db)):
    result2= await session.execute(select(User).where(User.username==user.username))
    db_user=result2.scalars().first()
    print(db_user.password)
    if db_user and check_password_hash(db_user.password,user.password):

        access_token=Authorize.create_access_token(subject=db_user.username)
        refresh_token=Authorize.create_refresh_token(subject=db_user.username)
        response={
            "access":access_token,
            "refresh": refresh_token
        }
        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Username or pssword")

@auth_route.get("/refresh")
async def refresh_token(
    Authorize: AuthJWT = Depends(),
    credentials = Security(bearer_scheme)
):
    try:
        Authorize.jwt_refresh_token_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please provide a valid refresh token"
        )

    current_user = Authorize.get_jwt_subject()
    access_token = Authorize.create_access_token(subject=current_user)

    return {"access": access_token}


