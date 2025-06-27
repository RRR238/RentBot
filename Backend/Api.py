from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from Repositories.User_repository import User_repository
from Repositories.Offers_repository import Offers_repository
from Dependency_injection import get_db, endpoint_verification
from Entities import User
from Singletons import security_manager
from Models import User_model
import uvicorn
from dotenv import load_dotenv
import os
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

load_dotenv()
host = os.getenv('HOST')
port = int(os.getenv('PORT'))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL e.g., ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Or ["POST", "GET", "OPTIONS"]
    allow_headers=["*"],
)

@app.post("/registration")
async def registration(user: User_model,
                       db_connection: AsyncSession = Depends(get_db)):
    user_repo = User_repository(db_connection)
    existing_user = await user_repo.get_user_by_name(user.username)

    if existing_user is not None:
        raise HTTPException(status_code=409,
                            detail="Username already exists")

    hashed_password = security_manager.hash_password(user.password)
    new_user = User(username=user.username,
                    password=hashed_password)
    added_user = await user_repo.create_user(new_user)

    return JSONResponse(
        status_code=201,
        content={
            "message": "User created successfully",
            "user": added_user.as_dict(),
        },
    )


@app.post("/login")
async def login(user: User_model,
                db_connection: AsyncSession = Depends(get_db)):
    user_repo = User_repository(db_connection)
    existing_user: User = await user_repo.get_user_by_name(user.username)

    if existing_user is None:
        raise HTTPException(status_code=401,
                            detail="User does not exist")

    hashed_password = existing_user.password
    valid_password = security_manager.verify_password(user.password, hashed_password)

    if not valid_password:
        raise HTTPException(status_code=401,
                            detail="Invalid password")

    token = security_manager.create_jwt_token({
        "userID": existing_user.id,
        "name": user.username,
        "password": user.password
    })
    return JSONResponse(
        status_code=200,
        content={
            "token": token,
            "type": "bearer"
        }
    )


@app.delete("/delete-user")
async def delete_user(user_id: int,
                      jwtTokenPayload: dict = Depends(endpoint_verification),
                      db_connection: AsyncSession = Depends(get_db)):
    user_repo = User_repository(db_connection)
    success = await user_repo.delete_user_by_id(user_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found."
        )

    return JSONResponse(
        status_code=200,
        content={"message": f"User with ID {user_id} has been deleted successfully."}
    )


@app.get("/offers")
async def offers(page:int,
                   limit:int,
                   price_min:int,
                   price_max: int,
                   size_min: int,
                    size_max:  int,
                    types: str,
                    jwtTokenPayload: dict = Depends(endpoint_verification),
                    db_connection: AsyncSession = Depends(get_db)
                    ):

    types_list = types.split(',')
    rooms = [int(i[0]) for i in types_list if 'rooms' in i or 'plus' in i]
    filtered_types = [t for t in types_list if 'rooms' not in t.lower() and 'plus' not in t.lower()]
    # Check if any item was removed (i.e., it matched 'rooms' or 'plus')
    if len(filtered_types) < len(types_list):
        filtered_types.append('flat')
    offers_repo = Offers_repository(db_connection)
    rent_offers = await offers_repo.get_filtered_rent_offers(price_max,
                                                             size_min,
                                                             size_max,
                                                             filtered_types,
                                                             rooms,
                                                             page)
    return JSONResponse(
        status_code=200,
        content=rent_offers
    )


if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)
