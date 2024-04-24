import datetime  # to calculate expiration of the JWT
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Security, Request, Security,HTTPException, Response
from fastapi.responses import RedirectResponse , JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_sso.sso.google import GoogleSSO  # pip install fastapi-sso
from fastapi_sso.sso.base import OpenID
from jose import jwt  # pip install python-jose[cryptography]


app = FastAPI()
CLIENT_ID = "43408078560-vqll83sca0454in8n6a85kjlbh1dg5ns.apps.googleusercontent.com"  # <-- paste your client id here
CLIENT_SECRET = "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" # <-- paste your client secret here
SECRET_KEY = "this-is-very-secret"  # used to sign JWTs, make sure it is really secret


sso = GoogleSSO(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri="http://127.0.0.1:8000/auth")

security = HTTPBearer()
app = FastAPI()


#Logic that looks on decoded data from JWT that contains user session
async def get_logged_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> OpenID:
    """Get user's JWT from the header, parse it and return the user's OpenID."""
    try:
        token = credentials.credentials
        claims = jwt.decode(token, key=SECRET_KEY, algorithms=["HS256"])
        print(claims)
        return OpenID(**claims["pld"])
    except Exception as error:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials") from error


#Test of protected route --> Points logic of get_logged_user
@app.get("/protected")
async def protected_endpoint(user: OpenID = Depends(get_logged_user)):
    return {"message": f"You are very welcome, {user.email}!"}


@app.get("/google/auth/login")
async def login():
    """Redirect the user to the Google login page."""
    with sso:
        return await sso.get_login_redirect(
            params={"prompt": "consent", "access_type": "offline"}
            )


#Check option to create id used as return for User Server end instead of JWT that can be co-related to original JWT saved in server side (cookies or DB)
@app.get("/auth")
async def login_callback(request: Request):
    with sso:
        openid = await sso.verify_and_process(request)
        if not openid:
            raise HTTPException(status_code=401, detail="Authentication failed")
    expiration = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)
    token = jwt.encode({"pld": openid.model_dump(), "exp": expiration, "sub": openid.id}, key=SECRET_KEY, algorithm="HS256")
    response = Response()
    response = JSONResponse(content={"message": "Logged in successfully"}, status_code=200)
    response.set_cookie(key="uid", value=token, httponly=True, max_age=1800, samesite='Lax', secure=True)
    return response


# Pending Adjustment
@app.get("/auth/logout")
async def logout():
    """Forget the user's session."""
    response = RedirectResponse(url="/prot")
    response.delete_cookie(key="uid")
    return response


if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)