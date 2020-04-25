import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext import declarative as dec

SqlAlchemyBase = dec.declarative_base()
__factory = None


def global_init(db_path):
    global __factory
    if __factory:
        return
    if not db_path.strip():
        raise ValueError('Путь неуказан')
    con_str = f'sqlite:///{db_path}?check_same_thread=False'
    print(f'Подключаюсь к {con_str}')
    engine = sa.create_engine(con_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    from . import __all_models
    SqlAlchemyBase.metadata.create_all(engine)


def create_session():
    global __factory
    return __factory()
