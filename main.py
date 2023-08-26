from flask import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage, JoinEvent, FlexSendMessage, ImageSendMessage, VideoSendMessage
import os
import re
from study import *

from sec import *

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def create_random_field():
    lane_size = random.randint(2, 18)
    field = Field(1000, lane_size)
    #field.set_slope({0: c.DOWN})
    field.length = random.randint(100, 3000)
    field.weather = random.randint(c.CLEAR, c.RAIN)
    field.type = random.randint(c.GRASS, c.DURT)
    horses = []

    for n in range(lane_size):
        if n == 0:
            horse = load_horse("sana")
        else:
            horse = Horse(n, f"{n}")
        horse.set_rider(Rider(n, f"n"))
        horse.fine_type = random.randint(c.GRASS, c.DURT)
        horse.condition = random.randint(c.FINE, c.BAD)
        horse.rider.condition = random.randint(c.FINE, c.BAD)
        horse.skill = random.randint(c.STABLE, c.ANTI_RAIN)
        horse.stats["speed"] = random.randint(10, 100)
        horse.stats["hp"] = random.randint(10, 100)
        horse.stats["power"] = random.randint(10, 100)
        #field.add_horse(horse)
        horses.append(horse)
    for horse in horses:
        field.add_horse(horse)
    return field, start_race_culc_only(field)

@app.route("/")
def hello():
    return "Sinulist Server Status: ONLINE"

@app.route("/img/<string:path>")
def send_image(path):
    dir = "result/"
    path = os.path.relpath(f"{os.getcwd()}/{dir}{path}")
    print(path)
    if os.path.commonprefix([dir, path]) == dir:
        if os.path.isfile(path):
            print("OK")
            return send_file(path)
        else: return "File not exists"
    else: return "Operation not allowed"

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

@handler.add(JoinEvent)
def join_event(event):
    str_join = 'keiba bot desu'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(str_join))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    linelist = event.message.text
    try:
        command, token = linelist.split()
        print(f"{command}, {token}")
    except: command, token = [None, None]
    try :
        to = event.source.group_id
    except:
        to = event.source.user_id
    if command is not None:
        url = "https://sclas.xyz:334/img/video.mp4"
        line_bot_api.push_message(to, VideoSendMessage(
            preview_image_url = "https://3.bp.blogspot.com/-DVHqPcbR9fA/VkxMAs3sgsI/AAAAAAAA0ss/ofdmv2PEXWo/s450/sports_keiba.png",
            original_content_url = url
        ))
    field, rank = create_random_field()
    rank_text = f"{rank}"
    info = [f"{n.name}" for n in field.lane_info]
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(f"{info}\n{rank_text}")
    )