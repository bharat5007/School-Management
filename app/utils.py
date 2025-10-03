import base64
from datetime import datetime, timedelta

from Cryptodome.Cipher import AES
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import settings
from app.constants.constants import UTF8

# Initialize password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def aes_encrypt_token(message, token_encryption_key="", aes_iv=""):
    message = message.encode(UTF8)
    token_encryption_key = token_encryption_key.encode(UTF8)
    aes_iv = aes_iv.encode(UTF8)
    obj = AES.new(token_encryption_key, AES.MODE_CFB, aes_iv)
    ciphertext = obj.encrypt(message)
    return str(base64.b64encode(ciphertext), UTF8)


def aes_decrypt_token(encrypted_token, token_encryption_key="", aes_iv=""):
    encrypted_token = encrypted_token.encode(UTF8)
    token_encryption_key = token_encryption_key.encode(UTF8)
    aes_iv = aes_iv.encode(UTF8)
    obj = AES.new(token_encryption_key, AES.MODE_CFB, aes_iv)
    return obj.decrypt(base64.b64decode(encrypted_token)).decode("utf-8")


def create_access_token(data, expires_delta=None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token):
    """Decode JWT access token"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None
