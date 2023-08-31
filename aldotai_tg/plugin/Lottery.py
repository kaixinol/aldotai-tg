from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func

engine = create_engine("sqlite:///furryData.db", echo=True)
Base = declarative_base()


class Table(Base):
    __tablename__: str = "info"
    id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=True)
    time = Column(Integer)


def get_row_count_by_id(id_value):
    row_count = session.query(Table).filter(Table.id == id_value).count()
    return row_count == 0


def get_count():
    return session.query(Table).count()


def get_random_records(n):
    return session.query(Table).order_by(func.random()).limit(n).all()


# 定义函数插入数据
def insert_info(id_value, user_name_value, time_value):
    new_info = Table(id=id_value, user_name=user_name_value, time=time_value)
    session.add(new_info)
    session.commit()


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
session.autocommit = True
