from managers.Auth.auth_manager import AuthConfig

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


platform_auth = AuthConfig(
    client_id=None,
    client_secret=None,
    redirect_uri=None,
    provider="platform"
)
