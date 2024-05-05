import datetime
from jose import jwt
from decouple import config
from user_agents import parse
from passlib.context import CryptContext
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from managers.User.user_manager import UserManager

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


# Clase base para configuración y autenticación SSO
class AuthConfig:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, provider: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.provider = provider

        if provider == "google":
            self.sso = GoogleSSO(client_id=self.client_id, client_secret=self.client_secret,
                                 redirect_uri=self.redirect_uri)
        if provider == "facebook":
            self.sso = FacebookSSO(client_id=self.client_id, client_secret=self.client_secret,
                                   redirect_uri=self.redirect_uri)
        # Añadir más proveedores cuando estén disponibles.

    async def get_login_redirect(self, **params):
        with self.sso:
            return await self.sso.get_login_redirect(params=params)

    async def verify(self, request: Request):
        with self.sso:
            openid = await self.sso.verify_and_process(request)
            if not openid:
                raise HTTPException(status_code=401, detail="Authentication failed")
            return openid

    @staticmethod
    async def generate_jwt(sso_data, openid_id):
        expiration = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)
        token = jwt.encode({
            "usr": sso_data["display_name"],
            "sub": openid_id,  # sso id must check what to do when regular login with same sso email
            "exp": expiration.timestamp()
        }, key=config("SECRET_KEY"), algorithm="HS256")
        return token

    @staticmethod
    async def get_current_user(request: Request):
        try:
            token = request.cookies.get("ss_usr_crd")
            if token is None:
                return None
            payload = jwt.decode(token, config("SECRET_KEY"), algorithms=["HS256"])
            username: str = payload.get("usr")
            user_id: int = payload.get("sub")
            expiration: str = payload.get("exp")
            if username is None or user_id is None:
                return None
            return {"username": username, "sso_id": user_id, "exp": expiration}
        except (jwt.JWTError, jwt.ExpiredSignatureError):
            return None

    @staticmethod
    async def process_sso_validation(request: Request, openid):
        client_host = request.client.host
        user_agent = parse(request.headers.get('User-agent'))
        sso_data = openid.model_dump()

        user_info = await UserManager.oauth_register_user(client_host, user_agent, sso_data)  # Calls DB to create User

        token = await AuthConfig.generate_jwt(sso_data, openid.id)

        message = "Logged in successfully" if user_info['new'] is False else "User created successfully"
        response = JSONResponse(content={
            "message": message,
            "access_token": token,
            "user_id": user_info['id']  # Additional User data can be included as needed
        }, status_code=200)

        response.set_cookie(key="ss_usr_crd", value=token, httponly=True, max_age=1800, samesite="lax", secure=True)
        response.delete_cookie(key="session")

        return response

    async def register_user(self, form_data, request: Request):
        # Extracción de datos del cliente desde la solicitud
        client_host = request.client.host
        user_agent = parse(request.headers.get('User-agent'))

        # Preparación de los datos para UserManager
        user_data = {
            "email": form_data.email,
            "password": form_data.password,
            "first_name": form_data.first_name,
            "last_name": form_data.last_name,
            "username": form_data.username,
            "provider": "platform"  # Asumiendo que es un registro directo sin SSO
        }

        # Llamada a UserManager para crear o verificar el usuario
        result = await UserManager.platform_register_user(client_host, user_agent, user_data)
        if not result:
            raise HTTPException(status_code=400, detail="Error registering User")

        # Devolver información sobre el éxito del registro o redireccionar si ya existe
        if result['new'] is True:
            return {"message": "User registered successfully", "user_id": result['id']}
        elif result['new'] is False and result['oauth_channel'] != "platform":
            # Redireccionar según el proveedor si el usuario ya existe
            provider = result['oauth_channel']
            print(provider)
            redirect_url = f"http://127.0.0.1:8000/auth/login/{provider}"
            return {"message": "User already exists", "redirect_to": redirect_url, "user_id": result['id']}

        return {"message": "User login successfully", "user_id": result['id'], "login": True}
