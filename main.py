from flask import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, JoinEvent, FlexSendMessage, ImageSendMessage, VideoSendMessage
import os
import lightgbm as lgb
from study import *

from sec import *

class Room:
    def __init__(self, id):
        self.id = id
        self.field = create_random_field()

    def set_field(self, field):
        self.field = field

    def get_field(self):
        return self.field

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

rooms = []

def load_rooms():
    global rooms
    if os.path.exists("pkl/rooms.pkl"):
        with open("pkl/rooms.pkl", "rb") as f:
            rooms = pickle.load(f)

def make_pkl(var, name):
    with open(f"{name}.pkl", "wb") as f:
        pickle.dump(var, f)

def serach_room(id):
    for r in rooms:
        if r.id == id: return r
    return None

def get_icon(i):
    if i < 20:
        icon = "capital_g"
    elif i < 40:
        icon = "capital_f"
    elif i < 50:
        icon = "capital_e"
    elif i < 60:
        icon = "capital_d"
    elif i < 70:
        icon = "capital_c"
    elif i < 80:
        icon = "capital_b"
    elif i < 90:
        icon = "capital_a"
    else:
        icon = "capital_s"
    return f"https://sclas.xyz:334/img/icon/{icon}.png"

def create_random_field():
    lane_size = random.randint(2, 12)
    field = Field(4000, lane_size)
    #field.set_slope({0: c.DOWN})
    field.length = random.randint(100, 3000)
    field.weather = random.randint(c.CLEAR, c.RAIN)
    field.type = random.randint(c.GRASS, c.DURT)
    horses = []

    for n in range(lane_size):
        if n == 0:
            horse = load_horse("pkl/horses/sana")
        else:
            horse = Horse(n, f"{n}")
        horse.set_rider(Rider(n, f"n"))
        horse.skill = random.randint(c.STABLE, c.ANTI_RAIN)
        horse.fine_type = random.randint(c.GRASS, c.DURT)
        if horse.has_skill(c.STABLE): horse.set_condition(c.GOOD)
        else: horse.condition = random.randint(c.FINE, c.BAD)
        horse.rider.condition = random.randint(c.FINE, c.BAD)
        horse.stats["speed"] = random.randint(10, 100)
        horse.stats["hp"] = random.randint(10, 100)
        horse.stats["power"] = random.randint(10, 100)
        #field.add_horse(horse)
        horses.append(horse)
    for horse in horses:
        field.add_horse(horse)
    return field

def gen_horse_info_json(field):
    contents = {
    "type": "carousel",
    "contents": []}
    for horse in field.lane_info:
        tmp = {"type": "bubble","hero": {"type": "image","url": "https://1.bp.blogspot.com/-2MR7FHzJskw/UnslOIi0O0I/AAAAAAAAaQo/zKKqefuVF0I/s800/eto_uma.png",
        "aspectMode": "fit"},"body": {"type": "box","layout": "horizontal","contents": [{"type": "box","layout": "vertical","contents": [{"type": "text",
        # Label
        "text": "馬名:\n\n速度:\n体力:\nスタミナ:\nスキル:",
        "wrap": True,"align": "start"}
        
        ]},{"type": "box","layout": "vertical","contents": [
            {"type": "box","layout": "baseline","contents": [{"type": "text",
        # Data
        "text": f"{horse.name}　\n","wrap":True}]},
        {"type": "box","layout": "baseline","contents": [
        # Icon
        {"type": "icon", "url": get_icon(horse.stats['speed']), "offsetTop": "2px"},
        {"type": "text",
        # Data
        "text": f"{horse.stats['speed']}　"},
        ]},{"type": "box","layout": "baseline","contents": [
        # Icon
        {"type": "icon", "url": get_icon(horse.stats['hp']), "offsetTop": "2px"},
        {"type": "text",
        # Data
        "text": f"{horse.stats['hp']}　"},
        ]},{"type": "box","layout": "baseline","contents": [
        # Icon
        {"type": "icon", "url": get_icon(horse.stats['power']), "offsetTop": "2px"},
        {"type": "text",
        # Data
        "text": f"{horse.stats['power']}　"},
        ]},{"type": "box","layout": "baseline","contents": [
        {"type": "text",
        # Data
        "text": f"{c.SKILLS[horse.skill]}　"},
        ]}]}]}}
        contents["contents"].append(tmp)
    return contents

def make_df(field):
    rank = start_race_culc_only(field)
    weather = [field.weather for _ in range(field.lane_size)]
    field_type = [field.type for _ in range(field.lane_size)]
    condition_horse = [n.condition for n in field.lane_info]
    condition_rider = [n.rider.condition for n in field.lane_info]
    fine_type = [n.fine_type for n in field.lane_info]
    skill = [n.skill for n in field.lane_info]
    speed = [n.stats["speed"] for n in field.lane_info]
    hp = [n.stats["hp"] for n in field.lane_info]
    power = [n.stats["power"] for n in field.lane_info]
    lane = [n for n in range(len(field.lane_info))]

    df = pd.DataFrame({"condition_horse": condition_horse, "condition_rider": condition_rider, \
                       "fine_type": fine_type, "skill": skill, "speed": speed, "hp": hp, "power": power})
    bst = lgb.Booster(model_file='keiba_model.txt')
    y_pred = bst.predict(df, num_iteration=bst.best_iteration)
    ai = pd.DataFrame({"id": [n for n in range(field.lane_size)],'predict':y_pred})
    ai = ai.sort_values("predict")
    rank_ai = [int(n[0]) for n in ai.values.tolist()]

    ranking = [-1 for _ in range(field.lane_size)]
    ranking_ai = [-1 for _ in range(field.lane_size)]
    for i, n in enumerate(rank):
        ranking[n] = i
    for i, n in enumerate(rank_ai):
        ranking_ai[n] = i
    df = pd.DataFrame({"Weather": weather, "Field": field_type, "Horse Condition": condition_horse, "Rider Condition": condition_rider\
                    , "Type": fine_type, "Skill": skill, "Speed": speed, "Health": hp, "Power": power, "Rank": ranking, "Predict": ranking_ai})
    return df

@app.route("/")
def hello():
    return "Sinulist Server Status: ONLINE"

@app.route("/img/<string:path>")
def send_image(path):
    dir = "static/"
    path = os.path.relpath(f"{os.getcwd()}/{dir}{path}")
    print(path)
    if os.path.commonprefix([dir, path]) == dir:
        if os.path.isfile(path):
            print("OK")
            return send_file(path)
        else: return "File not exists"
    else: return "Operation not allowed"

@app.route("/img/icon/<string:path>")
def send_icon(path):
    dir = "static/icons/"
    path = os.path.relpath(f"{os.getcwd()}/{dir}{path}")
    print(path)
    if os.path.commonprefix([dir, path]) == dir:
        if os.path.isfile(path):
            print("OK")
            return send_file(path)
        else: return "File not exists"
    else: return "Operation not allowed"

@app.route("/video/<string:path>")
def send_video(path):
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
    global rooms
    load_rooms()
    linelist = event.message.text
    try:
        command, token = linelist.split()
        print(f"{command}, {token}")
    except: command, token = [linelist, None]
    try :
        id = event.source.group_id
    except:
        id = event.source.user_id
    room = serach_room(id)
    if room is not None:
        field = room.field
        print("Room Exists")
    else:
        room = Room(id)
        rooms.append(room)
        make_pkl(rooms, "pkl/rooms")
        print(rooms)
        field = room.field

    df = make_df(field)
    df = df.sort_values("Rank")
    #field = create_random_field()

    if command == "h":
        #print(gen_horse_info_json(field))
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text='馬情報',
                contents=gen_horse_info_json(field)
            )
        )
    elif command == "c":
        field = create_random_field()
        room.set_field(field)
        make_pkl(rooms, "pkl/rooms")
        df = make_df(room.field)
        df = df.sort_values("Rank")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(f"{df}\n{field.get_horses()}")
        )
    elif command == "v":
        url = "https://sclas.xyz:334/img/video.mp4"
        line_bot_api.push_message(id, VideoSendMessage(
            preview_image_url = "https://3.bp.blogspot.com/-DVHqPcbR9fA/VkxMAs3sgsI/AAAAAAAA0ss/ofdmv2PEXWo/s450/sports_keiba.png",
            original_content_url = url
        ))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(f"{df}\n{field.get_horses()}")
        )