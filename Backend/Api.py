from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from Repositories.User_repository import User_repository
from Repositories.Offers_repository import Offers_repository
from Repositories.Chat_sessions_repository import Chat_session_repository
from Repositories.Cached_vector_search_results_repository import Cached_vector_search_results_repository
from Dependency_injection import get_db, endpoint_verification
from Entities import User, Chat_session, Chat_history, Cached_vector_search_results
from Singletons import security_manager
from Models import User_model, User_message_model, Chat_session_model
import uvicorn
from dotenv import load_dotenv
import os
from sqlalchemy.ext.asyncio import AsyncSession
from AI.Singletons import llm_langchain, llm, vector_db
from AI.Utils import prepare_chat_memory
from AI.Services import generate_ai_answer, search_by_summarized_preferences
from Utils import process_types_and_rooms_filters

load_dotenv()
host = os.getenv('HOST')
port = int(os.getenv('PORT'))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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

    processed_filters = process_types_and_rooms_filters(types)
    offers_repo = Offers_repository(db_connection)
    rent_offers = await offers_repo.get_filtered_rent_offers(price_max,
                                                             size_min,
                                                             size_max,
                                                             processed_filters['types'],
                                                             processed_filters['rooms'],
                                                             page)
    return JSONResponse(
        status_code=200,
        content=rent_offers
    )


@app.post("/chat/create-session")
async def create_session_id(jwtTokenPayload: dict = Depends(endpoint_verification),
                        db_connection: AsyncSession = Depends(get_db)):
    chat_session_repo = Chat_session_repository(db_connection)
    user_id = jwtTokenPayload['userID']
    new_session = Chat_session(user_id=user_id)
    session_id = await chat_session_repo.create_chat_session(new_session)

    return JSONResponse(
        status_code=200,
        content={"session_id":session_id}
    )


@app.post("/chat/generate-answer")
async def generate_answer(user_message:User_message_model,
                    jwtTokenPayload: dict = Depends(endpoint_verification),
                    db_connection: AsyncSession = Depends(get_db)
                    ):
    chat_session_repo = Chat_session_repository(db_connection)
    is_active_session = await chat_session_repo.is_session_active_by_session_id(user_message.session_id)
    if not is_active_session:
        await chat_session_repo.mark_session_inactive_by_session_id(user_message.session_id)
        raise HTTPException(
            status_code=404,
            detail="Session expired."
        )
    new_user_message = Chat_history(session_id=user_message.session_id,
                                    role='Human',
                                    message=user_message.message)
    new_user_message_id = await chat_session_repo.add_new_message(new_user_message)
    chat_history = await chat_session_repo.get_active_chat_history(user_message.session_id)
    chat_memory = prepare_chat_memory(chat_history)
    generated_answer = await generate_ai_answer(llm_langchain,
                                          chat_memory)

    new_ai_message = Chat_history(session_id=user_message.session_id,
                                    role='AI',
                                    message=generated_answer)

    new_ai_message_id = await chat_session_repo.add_new_message(new_ai_message)
    await chat_session_repo.update_last_interaction(user_message.session_id)

    return JSONResponse(
        status_code=200,
        content={"reply": generated_answer}
    )


@app.get("/chat/fetch-history")
async def fetch_history(jwtTokenPayload: dict = Depends(endpoint_verification),
                    db_connection: AsyncSession = Depends(get_db)):
    chat_session_repo = Chat_session_repository(db_connection)
    user_id = jwtTokenPayload['userID']
    active_session = await chat_session_repo.get_active_session_by_user_id(user_id)
    if not active_session:
        await chat_session_repo.mark_all_sessions_inactive_by_user(user_id)
        raise HTTPException(
            status_code=404,
            detail="Active session not found."
        )
    chat_history = await chat_session_repo.get_active_chat_history(active_session)
    await chat_session_repo.update_last_interaction(active_session)

    return JSONResponse(
        status_code=200,
        content={'history':chat_history,
                 'session_id':active_session}
    )


@app.post("/chat/close-session")
async def close_session(session: Chat_session_model,
                        jwtTokenPayload: dict = Depends(endpoint_verification),
                        db_connection: AsyncSession = Depends(get_db)
                        ):
    chat_session_repo = Chat_session_repository(db_connection)
    await chat_session_repo.mark_session_inactive_by_session_id(session.session_id)

    return Response(status_code=204)


@app.get("/search/find-results/{session_id}")
async def find_results(session_id:int,
                        jwtTokenPayload: dict = Depends(endpoint_verification),
                        db_connection: AsyncSession = Depends(get_db)
                        ):
    chat_session_repo = Chat_session_repository(db_connection)
    cached_results_repo = Cached_vector_search_results_repository(db_connection)
    is_active_session = await chat_session_repo.is_session_active_by_session_id(session_id)
    await cached_results_repo.delete_items_by_session_id(session_id)
    if not is_active_session:
        await chat_session_repo.mark_session_inactive_by_session_id(session_id)
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )
    chat_history = await chat_session_repo.get_active_chat_history(session_id)
    chat_memory = prepare_chat_memory(chat_history)
    results = await search_by_summarized_preferences(llm,
                                                     vector_db,
                                                     chat_memory)
    for result in results:
        new_item = Cached_vector_search_results(
                                                session_id=session_id,
                                                source_url=result['source_url'],
                                                location=result['location'],
                                                price_total=result['price_total'],
                                                size=result['size'],
                                                property_type=result['property_type'],
                                                rooms=result['rooms'],
                                                score=result['score']
                                                )
        added_item = await cached_results_repo.add_item(new_item)

    filtered_results = [{'source_url':result['source_url'],
                         'price_total':result['price_total'],
                         'location':result['location']} for result in results]

    return JSONResponse(status_code=200,
                        content={'total':len(filtered_results),
                                 'offers':filtered_results[:20]})

@app.get("/search/fetch-filtered-results/{session_id}")
async def fetch_filtered_results(session_id:int,
                                 page:int,
                                 limit:int,
                                 price_min:int,
                                 price_max: int,
                                 size_min: int,
                                 size_max:  int,
                                 types: str,
                                 jwtTokenPayload: dict = Depends(endpoint_verification),
                                 db_connection: AsyncSession = Depends(get_db)):
    cached_results_repo = Cached_vector_search_results_repository(db_connection)
    chat_session_repo = Chat_session_repository(db_connection)
    is_active_session = await chat_session_repo.is_session_active_by_session_id(session_id)
    await cached_results_repo.delete_items_by_session_id(session_id)
    if not is_active_session:
        await cached_results_repo.delete_items_by_session_id(session_id)
        await chat_session_repo.mark_session_inactive_by_session_id(session_id)
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )
    processed_filters = process_types_and_rooms_filters(types)
    filtered_cached_results = await cached_results_repo.get_filtered_vector_search_results(price_max,
                                                                                 size_min,
                                                                                 size_max,
                                                                                 processed_filters['types'],
                                                                                 processed_filters['rooms'],
                                                                                 page)

    return JSONResponse(
        status_code=200,
        content=filtered_cached_results
    )


if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)
