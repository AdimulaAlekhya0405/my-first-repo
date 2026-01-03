from fastapi import FastAPI
from order_routes import order_route
from auth_routes import auth_route
from fastapi_jwt_auth import AuthJWT
#from schemas import Settings
from pydantic import BaseSettings


app=FastAPI()


app.include_router(order_route)
app.include_router(auth_route)


