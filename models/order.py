from sqlalchemy import Column, DateTime, String, Integer, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from linebot.models import *
from database import Base


class Orders(Base):
    __tablename__ = 'orders'

    id = Column(String, primary_key=True)   # 訂單編號

    amount = Column(Integer)    # 訂單金額

    transaction_id = Column(String)     #串接Line pay時會用到
    is_pay = Column(Boolean, default=False)     #記錄訂單是否已付款，預設為未付款

    created_time = Column(DateTime, default=func.now()) #訂單建立時間

    user_id = Column('user_id', ForeignKey('users.id'))  # ForeignKey為外來鍵的意思，訂單由哪個user建立的

    items = relationship('Items', backref='order')  # 建立訂單的關聯性

    def display_receipt(self):
        item_box_component = []

        for item in self.items:#透過self.items取得訂單明細項目
            item_box_component.append(BoxComponent(
                layout='horizontal',
                contents=[#透過TextComponent顯示明細資料 text='{quantity} x {product_name}數量/產品名稱
                    TextComponent(text='{quantity} x {product_name}'.
                                  format(quantity=item.quantity,
                                         product_name=item.product_name),
                                  size='sm',
                                  color='#555555',
                                  flex=0),#text='NT${amount}'金額 
                    TextComponent(text='NT${amount}'.
                                  format(amount=(item.quantity * item.product_price)),
                                  size='sm',
                                  color='#111111',
                                  align='end')]
            ))
        #產生資料後就append到item_box_component等等會用到
        #透過BubbleContainer產生收據格式
        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='RECEIPT',
                                  weight='bold',
                                  color='#1DB446',
                                  size='sm'),
                    TextComponent(text='LSTORE',
                                  weight='bold',
                                  size='xxl',
                                  margin='md'),
                    TextComponent(text='Online Store',
                                  size='xs',
                                  color='#aaaaaa',
                                  wrap=True),
                    SeparatorComponent(margin='xxl'),
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=item_box_component#透過for迴圈產生的訂單明細
                    ),
                    SeparatorComponent(margin='xxl'),#分隔線
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='horizontal',
                                contents=[#顯示總金額
                                    TextComponent(text='TOTAL',
                                                  size='sm',
                                                  color='#555555',
                                                  flex=0),
                                    TextComponent(text='NT${total}'.
                                                  format(total=self.amount),
                                                  size='sm',
                                                  color='#111111',
                                                  align='end')]
                            )

                        ]
                    )
                ],
            )
        )

        message = FlexSendMessage(alt_text='receipt', contents=bubble)

        return message#return回給app.py裡的 confirm()這裡message = order.display_receipt()再push給user