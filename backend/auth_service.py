"""
Authentication Service - Google OAuth verification and JWT token management
"""
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings
from firebase_service import firebase_service


security = HTTPBearer()


class AuthService:
    
    @staticmethod
    async def verify_google_token(token: str) -> Dict:
        """Verify Google OAuth ID token and return user info"""
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )
            
            # Token is valid, extract user info
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid issuer')
            
            return {
                'uid': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False)
            }
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
    
    @staticmethod
    def create_access_token(user_data: Dict) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        
        to_encode = {
            'sub': user_data['uid'],
            'email': user_data['email'],
            'name': user_data.get('name', ''),
            'exp': expire,
            'iat': datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict:
        """Decode and verify JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    @staticmethod
    async def authenticate_user(token: str) -> Dict:
        """
        Complete authentication flow:
        1. Verify Google token
        2. Create/update user in Firestore
        3. Generate JWT token
        """
        # Verify Google token
        google_user = await AuthService.verify_google_token(token)
        
        # Check if user exists, create if not
        existing_user = await firebase_service.get_user(google_user['uid'])
        
        if existing_user:
            # Update last login
            await firebase_service.update_user(google_user['uid'], {
                'last_login': datetime.utcnow()
            })
            user_data = {**existing_user, **google_user}
        else:
            # Create new user
            user_data = await firebase_service.create_user(google_user)
        
        # Create JWT token
        access_token = AuthService.create_access_token(user_data)
        
        return {
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': settings.JWT_EXPIRATION_HOURS * 3600,
            'user': user_data
        }
    
    @staticmethod
    async def authenticate_with_user_info(user_info: Dict) -> Dict:
        """
        Authentication flow with pre-fetched user info from frontend.
        Used when frontend already has user info from Google's userinfo API.
        """
        # Build user data from provided info
        google_user = {
            'uid': user_info.get('sub'),
            'email': user_info.get('email'),
            'name': user_info.get('name', ''),
            'picture': user_info.get('picture', ''),
            'email_verified': user_info.get('email_verified', True)
        }
        
        # Check if user exists, create if not
        existing_user = await firebase_service.get_user(google_user['uid'])
        
        if existing_user:
            # Update last login
            await firebase_service.update_user(google_user['uid'], {
                'last_login': datetime.utcnow()
            })
            user_data = {**existing_user, **google_user}
        else:
            # Create new user
            user_data = await firebase_service.create_user(google_user)
        
        # Create JWT token
        access_token = AuthService.create_access_token(user_data)
        
        return {
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': settings.JWT_EXPIRATION_HOURS * 3600,
            'user': user_data
        }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    
    user = await firebase_service.get_user(payload['sub'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[Dict]:
    """Dependency to optionally get current user (for public endpoints)"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = AuthService.decode_token(token)
        return await firebase_service.get_user(payload['sub'])
    except:
        return None


auth_service = AuthService()
