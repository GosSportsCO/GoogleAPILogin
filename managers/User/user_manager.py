import sqlalchemy
from db import database
from db_models import user


class UserManager:
    @staticmethod
    async def oauth_register_user(client_host: str, user_agent, sso_data):
        # Intenta encontrar el usuario primero
        query = sqlalchemy.select(user).where(user.c.email == str(sso_data["email"]))
        existing_user = await database.fetch_one(query)

        if existing_user is None:
            query = sqlalchemy.insert(user).values(
                email=sso_data["email"],
                first_name=sso_data["first_name"],
                last_name=sso_data["last_name"],
                username=sso_data["display_name"],
                oauth_channel=sso_data["provider"],
                device_type=user_agent.device.family,
                os_name=user_agent.os.family,
                browser_name=user_agent.browser.family,
                client_host=client_host,

            )
            last_record_id = await database.execute(query)
            print("creado")
            return {"id": last_record_id, "new": True, "user_data": sso_data}
        else:
            # Si el usuario ya existe, retorna los datos existentes
            print("ya existe")
            return {"id": existing_user.id, "new": False, "user_data": dict(existing_user)}

    @staticmethod
    async def platform_register_user(client_host: str, user_agent, user_data):
        # Verificar si el usuario ya existe
        query = sqlalchemy.select(user).where(user.c.email == str(user_data["email"]))
        existing_user = await database.fetch_one(query)

        if existing_user:
            return {"id": existing_user.id, "new": False, "user_data": user_data,
                    "oauth_channel": existing_user.oauth_channel}

        # Crear nuevo usuario si no existe
        insert_query = sqlalchemy.insert(user).values(
            email=user_data["email"],
            password_hash=user_data["password"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            username=user_data["username"],
            oauth_channel=user_data["provider"],
            device_type=user_agent.device.family,
            os_name=user_agent.os.family,
            browser_name=user_agent.browser.family,
            client_host=client_host,
        )

        last_record_id = await database.execute(insert_query)
        return {"id": last_record_id, "new": True, "user_data": user_data}

