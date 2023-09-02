from sqlalchemy import Column,DateTime,String,func
from sqlalchemy.orm import relationship
from database import Base


class Users(Base):
    __tablename__ ='users'

    id = Column(String, primary_key = True) #line用戶id
    nick_name = Column(String) #line用戶name
    image_url = Column(String(length=256)) #line用戶頭貼
    created_time = Column(DateTime,default=func.now()) #line用戶被建立

    orders = relationship('Orders', backref='user') #加上這行建立訂單關聯性

    # user.orders 未來只要用這個指令就可以知道user所有的訂單
    # [<Order1> , <Order 2>]

    # order.user 透過訂單就可以知道是哪個user的
    # <User 1>