from sqlalchemy.engine import create_engine
from .contacts import models
from sqlalchemy.orm import sessionmaker


DBsession = None


def connect():
    global DBsession
    engine = create_engine("postgresql://postgres:1111@localhost:5432/web_hw_12")

    for base in [models.Base]:
        base.metadata.bind = engine
        base.metadata.create_all(engine)

    DBsession = sessionmaker(bind=engine)


def get_database():
    if DBsession is None:
        connect()

    db = DBsession()

    try:
        yield db
    finally:
        db.close()
