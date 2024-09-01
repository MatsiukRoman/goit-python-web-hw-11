from sqlalchemy import Column, Integer, String,  Date
from db import Base, engine

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150),  nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    phone_number = Column(String(50), nullable=True)
    birthday = Column(Date, nullable=False)
    additional_info = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)