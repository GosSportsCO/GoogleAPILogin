from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from schemas.request.Auth.auth_schemas import google_auth, platform_auth
from schemas.request.User.user_auth_schema import RegisterForm

router = APIRouter(prefix="/auth", tags=["auth"], responses={401: {"User": "Not authorized"}})


# Function that checks provider and runs login_redirect
@router.get("/login/{provider}")
async def login(provider: str):
    if provider == "google":
        return await google_auth.get_login_redirect(prompt="consent", access_type="offline")
    # elif provider == "facebook":
    #     return await facebook_auth.get_login_redirect()
    else:
        raise HTTPException(status_code=404, detail="Provider not supported")


# Function that fetch provider response data to generate a jwt
@router.get("/verif/{provider}")
async def auth_callback(provider: str, request: Request):
    if provider == "google":
        auth_config = google_auth
    # elif provider == "facebook":
    #     openid = await facebook_auth.verify_and_process(request)
    else:
        raise HTTPException(status_code=404, detail="Provider not supported")

    openid = await auth_config.verify(request)
    return await auth_config.process_sso_validation(request, openid)


@router.post("/register", summary="Allows new User registration", description="Registers a new User with the given "
                                                                              "details. If the User already exists,"
                                                                              "it can redirect to a login provider or "
                                                                              "handle the situation accordingly.")
async def register_user(request: Request, form_data: RegisterForm):
    auth_config = platform_auth
    # Llamar al método de registro en AuthConfig
    response = await auth_config.register_user(form_data, request)

    # Comprobar si el registro fue exitoso o si se requiere redirección
    if "redirect_to" in response:
        # Redirigir al usuario a la ruta de inicio de sesión del proveedor si el usuario ya existe
        print(response["redirect_to"])
        return RedirectResponse(url=response["redirect_to"], status_code=status.HTTP_303_SEE_OTHER)
    elif "login" in response:
        return JSONResponse(content=response, status_code=status.HTTP_200_OK)  # Needs to handle as User already exists
    return JSONResponse(content=response, status_code=status.HTTP_201_CREATED)


# Logout Function by deleting cookie not revision from server User session
@router.get("/logout")
async def logout():
    response = JSONResponse(content={"message": "You have been logged out"}, status_code=200)
    response.delete_cookie(key="ss_usr_crd")
    return response
