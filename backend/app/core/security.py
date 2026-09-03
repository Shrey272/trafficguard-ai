import hashlib
import hmac
import json
import base64
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.config import settings

# Attempt bcrypt / passlib or fallback to secure SHA256 PBKDF2
try:
    import bcrypt
    def get_password_hash(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            # Fallback check
            return verify_fallback_hash(plain_password, hashed_password)
except ImportError:
    pass

def hash_fallback(password: str) -> str:
    salt = "tg_salt_2026"
    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"pbkdf2:{salt}:{h.hex()}"

def verify_fallback_hash(plain: str, hashed: str) -> bool:
    if hashed.startswith("pbkdf2:"):
        parts = hashed.split(":")
        salt = parts[1]
        expected = parts[2]
        actual = hashlib.pbkdf2_hmac('sha256', plain.encode(), salt.encode(), 100000).hex()
        return hmac.compare_digest(actual, expected)
    return False

if 'get_password_hash' not in locals():
    get_password_hash = hash_fallback
    verify_password = verify_fallback_hash

# Attempt PyJWT or fallback standard compliant JWT encoder/decoder
try:
    import jwt
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except Exception:
            return None
except ImportError:
    def _b64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

    def _b64url_decode(s: str) -> bytes:
        padding = 4 - (len(s) % 4)
        if padding != 4:
            s += '=' * padding
        return base64.urlsafe_b64decode(s.encode('ascii'))

    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        to_encode = data.copy()
        exp = time.time() + (expires_delta.total_seconds() if expires_delta else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        to_encode.update({"exp": int(exp), "type": "access"})
        
        h_str = _b64url_encode(json.dumps(header).encode())
        p_str = _b64url_encode(json.dumps(to_encode).encode())
        sig = hmac.new(settings.SECRET_KEY.encode(), f"{h_str}.{p_str}".encode(), hashlib.sha256).digest()
        return f"{h_str}.{p_str}.{_b64url_encode(sig)}"

    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        to_encode = data.copy()
        exp = time.time() + (expires_delta.total_seconds() if expires_delta else settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)
        to_encode.update({"exp": int(exp), "type": "refresh"})
        
        h_str = _b64url_encode(json.dumps(header).encode())
        p_str = _b64url_encode(json.dumps(to_encode).encode())
        sig = hmac.new(settings.SECRET_KEY.encode(), f"{h_str}.{p_str}".encode(), hashlib.sha256).digest()
        return f"{h_str}.{p_str}.{_b64url_encode(sig)}"

    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            h_str, p_str, sig_str = parts
            expected_sig = _b64url_encode(hmac.new(settings.SECRET_KEY.encode(), f"{h_str}.{p_str}".encode(), hashlib.sha256).digest())
            if not hmac.compare_digest(sig_str, expected_sig):
                return None
            payload = json.loads(_b64url_decode(p_str).decode())
            if "exp" in payload and payload["exp"] < time.time():
                return None
            return payload
        except Exception:
            return None
