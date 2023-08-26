from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from models.database import Base, db_session


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    description = Column(String)
    product_image_url = Column(String)

    @staticmethod
    def list_all():
        products = db_session.query(Products).all()

        bubbles = []

        for product in products:
            pass