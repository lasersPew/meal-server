import datetime
import os
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from .database import UserDB, get_session
from .errors import BadRequestError, NotFoundError, UnauthorizedError
from .responses import AuthResponse

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # Define the token URL


class Auth:
    def __init__(self):
        self.router = APIRouter(prefix="/auth")
        self._add_routes()

    def _add_routes(self):
        self.router.post("/login", response_model=AuthResponse)(self.login)

    def verify_password(self, plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, username: str):
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=30
        )
        to_encode = {"sub": username, "exp": expire}
        return jwt.encode(
            to_encode,
            os.environ.get("SECRET_KEY"),
            algorithm=os.environ.get("ALGORITHM"),
        )

    async def login(
        self, username: str, password: str, session: Session = Depends(get_session)
    ) -> AuthResponse:
        user = session.exec(select(UserDB).where(UserDB.username == username)).first()
        if not user or not self.verify_password(password, user.password):
            raise UnauthorizedError(detail="Incorrect username or password")
        return AuthResponse(access_token=self.create_access_token(user.username))

    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session),
    ) -> UserDB:  # Updated to use OAuth2PasswordBearer
        try:
            payload = jwt.decode(
                token,
                os.environ.get("SECRET_KEY"),
                algorithms=os.environ.get("ALGORITHM"),
            )
            username = payload.get("sub")
            if not username:
                raise BadRequestError(details="Invalid token")
        except JWTError:
            raise BadRequestError(details="Invalid token")
        user = session.exec(select(UserDB).where(UserDB.username == username)).first()
        if not user:
            raise NotFoundError(detail="User not found")
        return user
