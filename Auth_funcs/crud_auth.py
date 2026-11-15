from sqlalchemy import Column, String
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class users_auths(Base):
    __tablename__ = "users_auths"

    userName = Column(String(100), primary_key=True, unique=True)
    userPassword = Column(String(255), nullable=False, unique=False)
    email = Column(String(255), nullable=False, unique=True)
    userToken = Column(String(255), nullable=False, unique=True)


def regis_user(session: Session, user_name, user_password, user_email, generated_tokens):
    new_user = users_auths(
        userName=user_name,
        userPassword=user_password,
        email=user_email,
        userToken=generated_tokens
    )
    session.add(new_user)
    session.commit()


def check_user_exists(session: Session, user_name, user_email):
    user = (
        session.query(users_auths)
        .filter(
            (users_auths.userName == user_name)
            | (users_auths.email == user_email)
        )
        .first()
    )
    return user is not None


def check_login(session: Session, user_name, user_password):
    user = (
        session.query(users_auths)
        .filter_by(userName=user_name, userPassword=user_password)
        .first()
    )
    return user is not None


# The functions below are for terminal testing purposes.
def delete_user(session: Session, user_name, user_email):
    user = (
        session.query(users_auths)
        .filter_by(userName=user_name, email=user_email)
        .first()
    )
    if user:
        session.delete(user)
        session.commit()


def update_user(session: Session, user_name, user_email, new_password):
    user = (
        session.query(users_auths)
        .filter_by(userName=user_name, email=user_email)
        .first()
    )
    if user:
        user.userPassword = new_password
        session.commit()


def view_user(session: Session, user_name, user_email):
    return (
        session.query(users_auths)
        .filter_by(userName=user_name, email=user_email)
        .first()
    )
