from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from src.database.users import models
from src.database.batabase import get_database


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
    SECRET_KEY = "secret"
    ALGORITHM = "HS256"

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update(
            {"exp": expire, "iat": datetime.now(timezone.utc), "scope": "access_token"}
        )
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=1)
        to_encode.update(
            {"exp": expire, "iat": datetime.now(timezone.utc), "scope": "refresh_token"}
        )
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    async def decode_refresh_token(
        self, token: str, db: Session = Depends(get_database)
    ):
        try:
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username = payload["sub"]
            if username is None:
                raise credentials_exception
            user = (
                db.query(models.User)
                .filter(models.User.username == payload["sub"])
                .first()
            )
            if user is None:
                raise credentials_exception
            return user
        except JWTError:
            raise credentials_exception

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_database)
    ) -> Optional[models.User]:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                username = payload["sub"]
                if username is None:
                    raise credentials_exception
                user = (
                    db.query(models.User)
                    .filter(models.User.username == payload["sub"])
                    .first()
                )
                if user is None:
                    raise credentials_exception
                return user
            elif payload["scope"] == "refresh_token":
                username = payload["sub"]
                if username is None:
                    raise credentials_exception

            else:
                raise credentials_exception

        except JWTError:
            raise credentials_exception
