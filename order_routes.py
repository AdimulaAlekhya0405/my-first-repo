from fastapi import APIRouter, Depends, Security,status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select
from models import User,Order
from schemas import OrderModel
from database import AsyncSessionLocal,engine
from sqlalchemy.ext.asyncio import AsyncSession 
from fastapi.encoders import jsonable_encoder


order_route=APIRouter(prefix="/order",tags=['orders'])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

session: AsyncSession = Depends(get_db)
bearer_scheme = HTTPBearer(
    bearerFormat="JWT",
    scheme_name="BearerAuth",
    description="Enter JWT token in the format: Bearer <token>",
    auto_error=False
)

@order_route.get("/")
async def bb():
    return {"message": "Hello world"}

@order_route.get('/')
async def hello(Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    
    return {"message":"Hello world"}


@order_route.post('/order',status_code=status.HTTP_201_CREATED)

async def place_an_order(order: OrderModel,Authorize: AuthJWT=Depends(),session: AsyncSession = Depends(get_db), credentials = Security(bearer_scheme) ):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    current_user= Authorize.get_jwt_subject()
    result= await session.execute(select(User).where(User.username== current_user))
 
    #result=await session.execute(select(User).where(User.email==user.email))
    user= result.scalars().first()

    new_order= Order(
        pizza_size= order.pizza_size,
        quantity=order.quantity
    )
    new_order.user= user
    new_order.id=order.id
    session.add(new_order)
    await session.commit()
    response={
        "pizza_size": new_order.pizza_size,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status":new_order.order_statuses
    }
    return jsonable_encoder(response)

@order_route.get('/orderss')
async def list_all_orders(Authorize: AuthJWT=Depends(),session: AsyncSession = Depends(get_db), credentials = Security(bearer_scheme) ):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=" Invalid token")
    current_user=Authorize.get_jwt_subject()
    user= await session.execute(select(User).where(User.username== current_user))
    result = await session.execute(
    select(User).where(User.username == current_user)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="you are not a superuser"
        )

    result = await session.execute(select(User))
    orders = result.scalars().all()

    return jsonable_encoder(orders)

'''@order_route.get('/orders')
async def list_all_orders(name:int, Authorize: AuthJWT=Depends(),session: AsyncSession = Depends(get_db), credentials = Security(bearer_scheme) ):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=" Invalid token")
    current_user=Authorize.get_jwt_subject()
    #user= await session.execute(select(User).where(User.username== current_user))
    result = await session.execute(
    select(User).where(User.username == current_user)
    )
    user = result.scalar_one_or_none()

    if user:
        result = await session.execute(select(Order).where(Order.user_id==name))
        orders = result.scalars().first()
        return jsonable_encoder(orders)

    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="you are not a superuser"
        )'''

@order_route.get("/orders")
async def get_order_by_id(
    user_id: int,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_db),
    credentials = Security(bearer_scheme) 
):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    current_username = Authorize.get_jwt_subject()

    result = await session.execute(
        select(User).where(User.username == current_username)
    )
    current_user = result.scalar_one_or_none()
    print("hello", current_user)

    if not current_user or not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a superuser"
        )

    result = await session.execute(
        select(Order).where(Order.id == user_id)
    )
    #print(result)
    total = result.scalars().all()
    print("hello1", total)

    if total is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return total

@order_route.get('/user/orders')
async def get_user_orders(Authorize: AuthJWT = Depends(),
                          session: AsyncSession = Depends(get_db),
                          credentials = Security(bearer_scheme) ):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    current_username = Authorize.get_jwt_subject()

    result = await session.execute(select(User).where(User.username == current_username))
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    return jsonable_encoder(current_user.orders)

@order_route.get('/user/order/{id}/', response_model= OrderModel)
async def get_user_orders(id: int, Authorize: AuthJWT = Depends(),
                          session: AsyncSession = Depends(get_db),
                          credentials = Security(bearer_scheme) ):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    subject=Authorize.get_jwt_subject()
    result = await session.execute(select(User).where(User.username == subject))
    current_user = result.scalar_one_or_none()
    orders= current_user.orders
    for o in orders:
        if o.id== id:
            return o
    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail=" no order with such id")
    