import sqlalchemy
import sqlalchemy.orm as orm
import os

DB_DATA_PATH = (os.path.dirname(__file__) + '\\db_data').replace('\\', '/')
DBsession = None
engine = None

class Base(orm.DeclarativeBase):
    pass


def connect():
    global DBsession
    global engine

    engine = sqlalchemy.create_engine(f'sqlite:////{DB_DATA_PATH}/db1')

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine

    DBsession = orm.sessionmaker(engine)

def get_db():
    if DBsession is None:
        connect()
    
    db = DBsession()

    try:
        yield db
    finally:
        db.close()
