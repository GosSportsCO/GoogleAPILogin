from contextlib import asynccontextmanager
from db import database
import uvicorn
from user_agents import parse
from fastapi import FastAPI, Depends, HTTPException, Security, Request,HTTPException, Response
from fastapi.responses import RedirectResponse , JSONResponse
from jose import jwt  # pip install python-jose[cryptography]
from sso_methods import AuthConfig


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await database.connect()
    try:
        yield
    finally:
        await database.disconnect()

app = FastAPI(lifespan=app_lifespan)

SECRET_KEY = "this-is-very-secret"  # used to sign JWTs, make sure it is really secret

# Crear instancias de AuthConfig para cada proveedor
google_auth = AuthConfig(
    client_id="43408078560-vqll83sca0454in8n6a85kjlbh1dg5ns.apps.googleusercontent.com",
    client_secret="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",
    redirect_uri="http://127.0.0.1:8000/auth/verif/google",
    provider="google"
)

# Suponiendo que tengas configuración similar para Facebook
# facebook_auth = AuthConfig(
#     client_id="facebook_client_id",
#     client_secret="facebook_secret",
#     redirect_uri="http://127.0.0.1:8000/auth/facebook",
#     provider="facebook"
# )


#Funcion that checks provider and runs login_redirect
@app.get("/auth/login/{provider}")
async def login(provider: str):
    if provider == "google":
        return await google_auth.get_login_redirect(prompt="consent", access_type="offline")
    # elif provider == "facebook":
    #     return await facebook_auth.get_login_redirect()
    else:
        raise HTTPException(status_code=404, detail="Provider not supported")
    

#Function that fetch provider response data to generate a jwt
@app.get("/auth/verif/{provider}")
async def auth_callback(provider: str, request: Request):
    if provider == "google":
        auth_config = google_auth
    # elif provider == "facebook":
    #     openid = await facebook_auth.verify_and_process(request)
    else:
        raise HTTPException(status_code=404, detail="Provider not supported")

    openid = await auth_config.verify(request)
    return await auth_config.process(request, openid)

#Logout Function by deleting cookie not revision from server user session
@app.get("/auth/logout")
async def logout():
    response = JSONResponse(content={"message": "You have been logged out"}, status_code=200)
    response.delete_cookie(key="uid")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)