from src.schemas.user import schemas

import src.database.users.models as models

from fastapi import status, APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm

import src.database.batabase as database

from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone
from src.services import auth


router = APIRouter(prefix="/users", tags=["users"])
auth_obj = auth.Auth()


@router.post(
    "/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: schemas.User,
    db: Session = Depends(database.get_database),
) -> schemas.UserResponse:
    exist_user = (
        db.query(models.User).filter(models.User.username == body.username).first()
    )

    if exist_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exist")

    hash_password = auth_obj.get_password_hash(body.password)

    new_user = models.User(
        username=body.username,
        hash_password=hash_password,
        created_at=datetime.now(timezone.utc),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    user_db = schemas.UserDB.from_orm(new_user)
    return schemas.UserResponse(user=user_db, detail="User successfully created")


@router.post(
    "/login", response_model=schemas.TokenModel, status_code=status.HTTP_200_OK
)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_database),
) -> schemas.TokenModel:
    exist_user = (
        db.query(models.User).filter(models.User.username == body.username).first()
    )

    if exist_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if not auth_obj.verify_password(body.password, exist_user.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    access_token = await auth_obj.create_access_token(data={"sub": body.username})
    refresh_token = await auth_obj.create_refresh_token(data={"sub": body.username})

    exist_user.refresh_token = refresh_token
    db.commit()
    db.refresh(exist_user)

    return schemas.TokenModel(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    user: models.User = Depends(auth_obj.get_current_user),
    db: Session = Depends(database.get_database),
) -> None:
    db.query(models.User).filter(models.User.id == user.id).update({"refresh_token": None})
    db.commit()

