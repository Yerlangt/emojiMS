import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Dialog(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'dialog'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    first_user = sqlalchemy.Column(sqlalchemy.Integer)
    second_user = sqlalchemy.Column(sqlalchemy.Integer)
    messages = sqlalchemy.Column(sqlalchemy.String)
