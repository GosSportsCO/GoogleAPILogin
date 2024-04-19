from fastapi import FastAPI, Request
from authlib.integrations.starlette_client import OAuth
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.jose import jwt
from fastapi.responses import RedirectResponse
from authlib.jose.errors import JoseError
import httpx

app = FastAPI()

oauth = OAuth()

SECRET_KEY = "your-secret-key-here"

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

oauth.register(
    name="google",
    client_id="43408078560-vqll83sca0454in8n6a85kjlbh1dg5ns.apps.googleusercontent.com",
    client_secret="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",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={
        "scope": "openid email profile",
        "response_type": "code"
    }
)

@app.get("/google_login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri, prompt="select_account")


async def fetch_jwks(uri):
    async with httpx.AsyncClient() as client:
        response = await client.get(uri)
        response.raise_for_status()
        return response.json()

@app.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        id_token = token.get('id_token')
        jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
        jwks = await fetch_jwks(jwks_uri)
        claims = jwt.decode(id_token, jwks)
        claims.validate()
        # Añadir información del usuario a la sesión
        request.session['user'] = dict(claims)
        return JSONResponse(content={"user": claims})
    except JoseError as e:
        print(f"JOSE Error: {e}")
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        print(f"General Error: {e}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.get("/view-session")
def view_session(request: Request):
    return request.session
@app.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/', status_code=302)