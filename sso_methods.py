import datetime
from fastapi import FastAPI, Depends, HTTPException, Request, Security, Response
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_sso.sso.google import GoogleSSO
from user_agents import parse
from fastapi_sso.sso.facebook import FacebookSSO
from jose import jwt
from db import create_or_update_user 


SECRET_KEY = "this-is-very-secret"  # used to sign JWTs, make sure it is really secret

# Clase base para configuración y autenticación SSO
class AuthConfig:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, provider: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.provider = provider

        if provider == "google":
            self.sso = GoogleSSO(client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
        if provider == "facebook":
            self.sso = FacebookSSO(client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
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
        

    async def process(self, request: Request, openid):
        client_host = request.client.host
        user_agent = parse(request.headers.get('user-agent'))
        
        expiration = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)
        token = jwt.encode({
            "pld": openid.model_dump(),
            "exp": expiration.timestamp(),
            "sub": openid.id
        }, key=SECRET_KEY, algorithm="HS256")

        # Aquí creas un diccionario simple solo con información básica sobre el user agent para incluir en el JSON
        user_agent_info = {
            "browser": user_agent.browser.family,
            "browser_version": user_agent.browser.version_string,
            "os": user_agent.os.family,
            "os_version": user_agent.os.version_string,
            "device": user_agent.device.family
        }
        print(openid)
        # Guardar o actualizar usuario en la base de datos
        user_info = await create_or_update_user(openid.model_dump())

        response = JSONResponse(content={
            "message": "Logged in successfully",
            "client_host": client_host,
            "user_agent": user_agent_info  # Usar el diccionario simplificado
        }, status_code=200)

        response.set_cookie(key="uid", value=token, httponly=True, max_age=1800, samesite='Lax', secure=True)
        response.delete_cookie(key="session")
        return response
