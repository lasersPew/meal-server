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
    """Handles authentication processes including login and token management."""

    def __init__(self):
        self.router = APIRouter(prefix="/auth")
        self._add_routes()

    def _add_routes(self):
        self.router.post("/login", response_model=AuthResponse)(self.login)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(username: str) -> str:
        """Creates a JWT access token for the given username."""
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
        """Login and create a JWT token.
        This function verifies the username and password, and if valid, returns an access token.
        """
        query = select(UserDB).where(UserDB.username == username)
        user = session.exec(query).first()
        if not user or not self.verify_password(password, user.password):
            raise UnauthorizedError(detail="Incorrect username or password")
        return AuthResponse(data=self.create_access_token(user.username))

    @staticmethod
    async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session),
    ) -> UserDB:
        """Get the current user from the token.
        This function decodes the JWT token and retrieves the user from the database.
        If the token is invalid or the user does not exist, it raises an error.
        This function is used as a dependency in FastAPI routes.
        It uses the OAuth2PasswordBearer dependency to extract the token from the request.
        The token is then decoded to get the username, which is used to fetch the user from the database.
        If the token is invalid or the user does not exist, it raises an error.
        This function is used to protect routes that require authentication.
        """
        try:
            payload = jwt.decode(
                token,
                os.environ.get("SECRET_KEY"),
                algorithms=os.environ.get("ALGORITHM"),
            )
            username = payload.get("sub")
            if not username:
                raise BadRequestError(detail="Invalid token")
        except JWTError:
            raise BadRequestError(detail="Invalid token")
        query = select(UserDB).where(UserDB.username == username)
        user = session.exec(query).first()
        if not user:
            raise NotFoundError(detail="User not found")
        return user
