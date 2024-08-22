from typing import List, Union
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi_mail import FastMail, MessageSchema, MessageType
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.domain.repositories.authentication_repository import (AuthenticationRepository, AuthenticationModelOut,
                                                               AuthenticationModelIn, ActivateAccountModel,
                                                               AuthenticationModelOutToken)
from src.infrastructure.adapters.data_sources.db_config import session, algorithm, secret_key
from src.infrastructure.adapters.data_sources.email_config import conf
from src.infrastructure.adapters.data_sources.entities.agro_web_entity import (AuthenticationEntity, UserEntity)

oauth2_scheme = OAuth2PasswordBearer("/token")


class AuthenticationRepositoryAdapter(AuthenticationRepository):

    @staticmethod
    async def add_auth(auth: AuthenticationModelIn) -> AuthenticationModelOut:
        new_auth = AuthenticationEntity(email_user_auth=auth.auth_email_user, password_auth=auth.auth_password,
                                        disabled_auth=auth.auth_disabled, user_id=auth.auth_user_id,
                                        code_valid=auth.code_valid)
        session.add(new_auth)
        session.commit()
        session.refresh(new_auth)
        auth_model_out = AuthenticationModelOut(
            id_auth=new_auth.id_auth,
            auth_email_user=new_auth.email_user_auth,
            auth_password=new_auth.password_auth,
            auth_disabled=new_auth.disabled_auth,
            auth_user_id=new_auth.user_id,
            code_valid=new_auth.code_valid
        )
        return auth_model_out

    @staticmethod
    async def get_auth_by_email(email_user: str) -> AuthenticationModelOutToken:
        query = session.query(AuthenticationEntity).join(UserEntity).filter(
            AuthenticationEntity.email_user_auth == email_user).first()
        stmt = (
            select(AuthenticationEntity, UserEntity.name_user)
            .join(UserEntity, AuthenticationEntity.user_id == UserEntity.id_user)
            .where(AuthenticationEntity.email_user_auth == email_user)
        )
        query = session.execute(stmt).first()
        if not query:
            session.commit()
            raise HTTPException(status_code=401, detail="Could not validate credentials",
                                headers={"WWW-Authenticate": "Bearer"})
        else:
            auth_model_out = AuthenticationModelOutToken(
                id_auth=query[0].id_auth,
                auth_password=query[0].password_auth,
                auth_email_user=query[0].email_user_auth,
                auth_user_id=query[0].user_id,
                auth_disabled=query[0].disabled_auth,
                code_valid=query[0].code_valid,
                name_user=query.name_user
            )
            session.commit()
            return auth_model_out

    @staticmethod
    async def update_auth(id_user: int, auth_email: str) -> AuthenticationModelOut:
        query = session.query(AuthenticationEntity).where(AuthenticationEntity.user_id == id_user).first()
        if not query:
            session.commit()
            raise HTTPException(status_code=404, detail="Authentication not found")
        else:
            if hasattr(query, 'email_user_auth'):
                setattr(query, 'email_user_auth', auth_email)

        auth_model_out = AuthenticationModelOut(
            id_auth=query.id_auth,
            auth_password=query.password_auth,
            auth_email_user=auth_email,
            auth_user_id=query.user_id,
            auth_disabled=query.disabled_auth,
            code_valid=query.code_valid
        )
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=400,
                                detail=f"There is already a authentication with the email: {auth_email}")
        return auth_model_out

    @staticmethod
    async def get_all_auths() -> List[AuthenticationModelOut]:
        pass

    @staticmethod
    async def delete_auth(id_auth: int) -> None:
        pass

    @staticmethod
    async def create_token(data: dict, time_expire: Union[timedelta, None] = None) -> str:
        data_copy = data.copy()
        if time_expire is None:
            expires = datetime.utcnow() + timedelta(minutes=20)
        else:
            expires = datetime.utcnow() + time_expire
        data_copy.update({"exp": expires})
        token_jwt = jwt.encode(data_copy, key=secret_key, algorithm=algorithm)
        return token_jwt

    @staticmethod
    async def get_user_current(token: str) -> bool:
        try:
            token_decode = jwt.decode(token, key=secret_key, algorithms=[algorithm])
            user_email = token_decode.get("sub")
            if user_email is None:
                raise HTTPException(status_code=401, detail="Could not validate credentials",
                                    headers={"WWW-Authenticate": "Bearer"})
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials",
                                headers={"WWW-Authenticate": "Bearer"})
        auth = await AuthenticationRepositoryAdapter.get_auth_by_email(user_email)
        if not auth:
            raise HTTPException(status_code=400, detail="User not found",
                                headers={"WWW-Authenticate": "Bearer"})
        return True

    @staticmethod
    async def activate_account(activate_data: ActivateAccountModel) -> None:
        query = session.query(AuthenticationEntity).where(AuthenticationEntity.id_auth == activate_data.auth_id
                                                          and AuthenticationEntity.code_valid == activate_data.code
                                                          ).first()
        if not query:
            session.commit()

            raise HTTPException(status_code=404, detail="Code error")
        else:
            if hasattr(query, 'disabled_auth'):
                setattr(query, 'disabled_auth', False)
                raise HTTPException(status_code=200, detail="Account active")

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=400,
                                detail=f"Error in activating the account")

    @staticmethod
    async def send_email(data_user: AuthenticationModelOut, name_user: str) -> None:
        html = f"""<div style="width: 100%; text-align: center;">
          <div style="margin: 5%;">
            <h1>¡Bienvenido<br />a<br /><span style="color: rgba(1,125,63,1);">AGRO</span>-<span
                style="color: rgb(241, 207, 105);">WEB</span>!</h1>
            <p style="color: black;">Querido <span style="text-transform: uppercase; font-weight: 700;">{name_user}</span>, 
            Estamos deseando que empieces. Primero tienes que confirmar tu cuenta. Haz clic en el botón de
              abajo.</p>
          </div>
          <a href="http://localhost:4200/activate/{data_user.id_auth}+{data_user.code_valid}" class="btn"
            style="text-decoration: none; color: #fff; background-color: rgba(1,125,63,1); padding: 20px; cursor: pointer; border-radius: 10px;">Click
            para activar</a>
          <div style="margin: 5%;">
            <p style="color: black;">Si no puedes hacer clic en el enlace, cópialo y pégalo en la barra de direcciones de tu
              navegador.</p>
            <a href="http://localhost:4200/activate/{data_user.id_auth}+{data_user.code_valid}">http://localhost:4200/activate/{data_user.id_auth}+{data_user.code_valid}</a>
          </div>
          <p>Una vez que hayas completado estos pasos, tu registro estará confirmado y podrás acceder a todos los servicios de
            <span style="color: rgba(1,125,63,1);">AGRO</span>-<span style="color: rgb(241, 207, 105);">WEB</span></p>
          <div style="margin: 5%;">
            <h3>¡Gracias por unirte a nosotros!</h3>
          </div>
        </div>"""

        message = MessageSchema(
            subject="Activar cuenta de AGRO-WEB",
            recipients=[data_user.auth_email_user],
            body=html,
            subtype=MessageType.html)

        fm = FastMail(conf)
        await fm.send_message(message)
