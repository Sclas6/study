from flask import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, JoinEvent, FlexSendMessage, ImageSendMessage, VideoSendMessage
from linebot.models import RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize, MessageAction, PostbackAction, PostbackEvent
import os
import pickle
import unicodedata
from study import *

from sec import *

class Room:
    def __init__(self, id):
        self.id = id
        self.race = create_random_race(None)
        self.status = None

    def set_race(self, race: Race):
        self.race = race

    def get_race(self):
        return self.race

    def set_status(self, status):
        self.status = status
    
    def get_status(self):
        return self.status

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

rooms = []

def check_herf(str):
    for i, a in enumerate(str):
        if unicodedata.east_asian_width(a) not in ["Na", "H"]:
            return False
        if i > 11: return False
    return True

def load_rooms():
    global rooms
    if os.path.exists("pkl/rooms.pkl"):
        with open("pkl/rooms.pkl", "rb") as f:
            rooms = pickle.load(f)

def load_horse(name):
    ans = None
    if os.path.exists(f"pkl/horses/{name}.pkl"):
        with open(f"pkl/horses/{name}.pkl", "rb") as f:
            ans = pickle.load(f)
    return ans

def create_horse(name, horse: Horse):
    with open(f"pkl/horses/{name}.pkl", "wb") as f:
        pickle.dump(horse, f)

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

def create_random_race(user_horse):
    lane_size = random.randint(2, 12)
    field = Field(4000, lane_size)
    #field.set_slope({0: c.DOWN})
    field.length = random.randint(100, 3000)
    field.weather = random.randint(c.CLEAR, c.RAIN)
    field.type = random.randint(c.GRASS, c.DURT)
    horses = []
    for n in range(lane_size):
        if n == 0 and user_horse is not None: horse = user_horse
        else:
            horse = Horse(f"{n}")
            horse.skill = random.randint(c.STABLE, c.NONE)
            horse.stats["speed"] = random.randint(10, 100)
            horse.stats["hp"] = random.randint(10, 100)
            horse.stats["power"] = random.randint(10, 100)
            horse.fine_type = random.randint(c.GRASS, c.DURT)
        horse.set_rider(Rider(f"n"))
        horse.reset_condition()
        horse.rider.condition = random.randint(c.FINE, c.BAD)
        #field.add_horse(horse)
        horse.set_id(n)
        horses.append(horse)
    race = Race(horses, field)
    return race

def gen_horse_info_json(horse):
    bubble = {"type": "bubble","hero": {"type": "image","url": "https://1.bp.blogspot.com/-2MR7FHzJskw/UnslOIi0O0I/AAAAAAAAaQo/zKKqefuVF0I/s800/eto_uma.png",
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
    '''
    bubble["footer"] =  {"type": "box","layout": "vertical","contents": [{"type": "button","action": {
    "type": "postback","data": "create_horse","label": "新規作成"},"style": "primary"}]}
    '''
    return bubble

def gen_horses_info_json(race: Race):
    contents = {
    "type": "carousel",
    "contents": []}
    for horse in race.get_horses():
        contents["contents"].append(gen_horse_info_json(horse))
    return contents

def gen_create_horse_json():
    contents = {"type": "bubble","header": {"type": "box","layout": "vertical","contents": [{"type": "text",
    "text": "まだ馬を所持していません\n馬を購入しますか?", "wrap": True}]},"hero": {"type": "image",
    "url": "https://1.bp.blogspot.com/-2MR7FHzJskw/UnslOIi0O0I/AAAAAAAAaQo/zKKqefuVF0I/s800/eto_uma.png",
    "aspectMode": "fit"},"footer": {"type": "box","layout": "vertical","contents": [{"type": "button",
    "action": {"type": "postback","data": "create_horse","label": "新規購入"},"style": "primary"}]}}
    return contents

def make_df(race: Race):
    ranking = race.get_rank()
    ranking_ai = race.get_pred()
    print(ranking)
    field = race.get_field()
    weather = [field.weather for _ in range(field.lane_size)]
    field_type = [field.type for _ in range(field.lane_size)]
    condition_horse = [n.condition for n in race.get_horses()]
    condition_rider = [n.rider.condition for n in race.get_horses()]
    fine_type = [n.fine_type for n in race.get_horses()]
    skill = [n.skill for n in race.get_horses()]
    speed = [n.stats["speed"] for n in race.get_horses()]
    hp = [n.stats["hp"] for n in race.get_horses()]
    power = [n.stats["power"] for n in race.get_horses()]
    df = pd.DataFrame({"Weather": weather, "Field": field_type, "Horse Condition": condition_horse, "Rider Condition": condition_rider\
                    , "Type": fine_type, "Skill": skill, "Speed": speed, "Health": hp, "Power": power, "Rank": ranking, "Predict": ranking_ai})
    return df

def createRichmenu():
    result = False
    try:
        # define a new richmenu
        rich_menu_to_create = RichMenu(
            size = RichMenuSize(width=1200, height=405),
            selected = True,
            name = 'richmenu for randomchat',
            chat_bar_text = 'TAP HERE',
            areas=[
                RichMenuArea(
                    bounds = RichMenuBounds(x=0, y=0, width=400, height=405),
                    action = PostbackAction(type = "postback", data = "ikusei")
                ),
                RichMenuArea(
                    bounds = RichMenuBounds(x=400, y=0, width=400, height=405),
                    action = PostbackAction(type = "postback", data = "umajouhou")
                ),
                RichMenuArea(
                    bounds = RichMenuBounds(x=800, y=0, width=400, height=405),
                    action = PostbackAction(type = "postback", data = "race")
                )
            ]
        )
        richMenuId = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

        # upload an image for rich menu
        path = 'static/menu.jpg'

        with open(path, 'rb') as f:
            line_bot_api.set_rich_menu_image(richMenuId, "image/jpeg", f)

        # set the default rich menu
        line_bot_api.set_default_rich_menu(richMenuId)

        result = True

    except Exception as e:
        print(e)
        result = False


    return result

print(createRichmenu())

@app.route("/")
def hello():
    return "Keiba Server Status: ONLINE"

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

@handler.add(PostbackEvent)
def on_postback(event):
    global rooms
    load_rooms()
    command = event.postback.data
    user_id = event.source.user_id
    room = serach_room(user_id)
    print(event.postback.data)
    if command == "ikusei":
        pass
    elif command == "umajouhou":
        horse = load_horse(user_id)
        if horse == None:
            line_bot_api.push_message(to = user_id, messages = FlexSendMessage("馬作成", gen_create_horse_json()))
        else:
            line_bot_api.push_message(user_id, FlexSendMessage("馬情報", gen_horse_info_json(horse)))
    elif command == "create_horse":
        # TODO ERROR HANDRING if User Already has player Horse
        line_bot_api.push_message(user_id, TextSendMessage("名前を送信してください"))
        room.set_status("Create_Room")
        make_pkl(rooms, "pkl/rooms")

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
    user_horse = load_horse(id)
    #print(room.get_status())
    if room is not None:
        race = room.race
        print("Room Exists")
    else:
        room = Room(id)
        rooms.append(room)
        make_pkl(rooms, "pkl/rooms")
        print(rooms)
        race = room.race

    df = make_df(race)
    df = df.sort_values("Rank")
    #field = create_random_field()
    if room.get_status() == "Create_Room":
        if check_herf(command):
            horse = Horse(command)
            horse.set_skill(c.NONE)
            create_horse(id, horse)
            room.set_status(None)
            make_pkl(rooms, "pkl/rooms")
            line_bot_api.push_message(id, TextSendMessage("馬を作成しました!"))
            line_bot_api.push_message(id, FlexSendMessage("馬情報", gen_horse_info_json(horse)))
        else: line_bot_api.push_message(id, TextSendMessage("名前は半角文字の12字以内である必要があります"))
    elif command == "h":
        #print(gen_horse_info_json(field))
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text='馬情報',
                contents=gen_horses_info_json(race)
            )
        )
    elif command == "c":
        race = create_random_race(user_horse)
        room.set_race(race)
        make_pkl(rooms, "pkl/rooms")
        df = make_df(room.race)
        df = df.sort_values("Rank")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(f"{df}")
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
            TextSendMessage(f"{df}")
        )