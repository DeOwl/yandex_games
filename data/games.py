from .db_session import SqlAlchemyBase
import sqlalchemy


class Game(SqlAlchemyBase):
    __tablename__ = 'games'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=False)
    description = sqlalchemy.Column(sqlalchemy.String, unique=True)
    cost = sqlalchemy.Column(sqlalchemy.Integer, unique=False)
    rating = sqlalchemy.Column(sqlalchemy.String, unique=True)
    image = sqlalchemy.Column(sqlalchemy.String, unique=True)
