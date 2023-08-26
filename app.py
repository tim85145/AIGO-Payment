from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from models.user import Users
from models.database import db_session,init_db
from models.product import Products
from models.cart import Cart
app = Flask(__name__)


line_bot_api = LineBotApi('+I2ixntMnrSn8RwTRc6fOJv0v202vEDE0GXYM5Jzz8WLOoztnhibUy3REAMdNFuEqB/ZbM5uNC4yUY5KHAQbpV0nLTlVQn8ywh1nDY3mlfID2/dlJ1HAPqyNPDBKXgZPsMR/od0r56fbu3gMN6/K+wdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('24a8203d84fa58b823140d6b5f1ec727')


app = Flask(__name__)

#建立或取得user
def get_or_create_user(user_id):
    user = db_session.query(Users).filter_by(id=user_id).first()

    if not user:
        profile = line_bot_api.get_profile(user_id)

        user = Users(id=user_id,nick_name=profile.display_name, image_url=profile.picture_url)
        db_session.add(user)
        db_session.commit()
    return user


def about_us_event(event):
    emoji = [
            {
                "index": 0,
                "productId": "5ac21184040ab15980c9b43a",
                "emojiId": "225"
            },
            {
                "index": 17,
                "productId": "5ac21184040ab15980c9b43a",
                "emojiId": "225"
            }
        ]

    text_message = TextSendMessage(text='''$ Master RenderP $
Hello! 您好，歡迎您成為 Master RenderP 的好友！

我是Master 支付小幫手 

-這裡有商城，還可以購物喔~
-直接點選下方【圖中】選單功能

-期待您的光臨！''', emojis=emoji)

    sticker_message = StickerSendMessage(
        package_id='8522',
        sticker_id='16581271'
    )
    line_bot_api.reply_message(
        event.reply_token,
        [text_message, sticker_message])
    
# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_or_create_user(event.source.user_id)
    profile = line_bot_api.get_profile(event.source.user_id)
    uid = profile.user_id
    message_text = str(event.message.text).lower()
    cart = Cart(user_id=event.source.user_id)
    message = None
    if message_text == '@使用說明':
        about_us_event
    elif message_text == '我想訂購商品':
        message = Products.list_all()
    #當user要訂購時就會執行這段程式
    elif "i'd like to have" in message_text:

            product_name = message_text.split(',')[0]#利用split(',')拆解並取得第[0]個位置的值
            # 例如 Coffee,i'd like to have經過split(',')拆解並取得第[0]個位置後就是 Coffee
            num_item = message_text.rsplit(':')[1]#同理產品就用(':')拆解取得第[1]個位置的值
            #資料庫搜尋是否有這個產品名稱
            product = db_session.query(Products).filter(Products.name.ilike(product_name)).first()
            #如果有這個產品名稱就會加入
            if product:

                cart.add(product=product_name, num=num_item)
                #然後利用confirm_template的格式詢問用戶是否還要加入？
                confirm_template = ConfirmTemplate(
                    text='Sure, {} {}, anything else?'.format(num_item, product_name),
                    actions=[
                        MessageAction(label='Add', text='add'),
                        MessageAction(label="That's it", text="That's it")
                    ])

                message = TemplateSendMessage(alt_text='anything else?', template=confirm_template)

            else:
                #如果沒有找到產品名稱就會回給用戶沒有這個產品
                message = TextSendMessage(text="Sorry, We don't have {}.".format(product_name))

            print(cart.bucket())
    elif message_text in ['my cart', 'cart', "that's it"]:#當出現'my cart', 'cart', "that's it"時

        if cart.bucket():#當購物車裡面有東西時
            message = cart.display()#就會使用 display()顯示購物車內容
        else:
            message = TextSendMessage(text='Your cart is empty now.')
    if message:
        line_bot_api.reply_message(
        event.reply_token,
        message
    )
#初始化產品資訊
@app.before_first_request
def init_products():
    # init db
    result = init_db()#先判斷資料庫有沒有建立，如果還沒建立就會進行下面的動作初始化產品
    if result:
        init_data = [Products(name='Coffee',
                              product_image_url='https://i.imgur.com/DKzbk3l.jpg',
                              price=150,
                              description='nascetur ridiculus mus. Donec quam felis, ultricies'),
                     Products(name='Tea',
                              product_image_url='https://i.imgur.com/PRTxyhq.jpg',
                              price=120,
                              description='adipiscing elit. Aenean commodo ligula eget dolor'),
                     Products(name='Cake',
                              price=180,
                              product_image_url='https://i.imgur.com/PRm22i8.jpg',
                              description='Aenean massa. Cum sociis natoque penatibus')]
        db_session.bulk_save_objects(init_data)#透過這個方法一次儲存list中的產品
        db_session.commit()#最後commit()才會存進資料庫
        #記得要from models.product import Products在app.py
        

if __name__ == "__main__":
    init_products()
    app.run()