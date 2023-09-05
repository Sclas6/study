from flask import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextMessage, TextSendMessage, FlexSendMessage, ImageSendMessage, VideoSendMessage
from linebot.models import RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize
from linebot.models import MessageEvent, JoinEvent, PostbackEvent, LeaveEvent, FollowEvent, UnfollowEvent
from linebot.models import MessageAction, PostbackAction
import os
import pandas as pd
import pickle
import random
import re
import unicodedata
from study import Horse, Rider, Field, Race
from gen_json import *
from sec import *

class User:
    def __init__(self, id):
        self.id = id
        self.race: Race = create_random_race(None)
        self.horse: Horse = None
        self.status = None
        self.gold = 100000
        self.tickets = {}

    def set_race(self, race: Race):
        self.race = race

    def set_gold(self, gold):
        self.gold = gold

    def set_ticket(self, tickets: dict):
        self.tickets = tickets

    def get_gold(self):
        return self.gold

    def get_race(self):
        return self.race

    def set_status(self, status):
        self.status = status
    
    def get_status(self):
        return self.status

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

users = []

def check_herf(str):
    for i, a in enumerate(str):
        if unicodedata.east_asian_width(a) not in ["Na", "H"]:
            return False
        if i > 11: return False
    return True

def load_users():
    global users
    if os.path.exists("pkl/users.pkl"):
        with open("pkl/users.pkl", "rb") as f:
            users = pickle.load(f)
    return users

def save_pkl(var, name):
    with open(f"{name}.pkl", "wb") as f:
        pickle.dump(var, f)

def serach_room(id):
    for r in users:
        if r.id == id: return r
    return None

def create_random_field():
    lane_size = random.randint(4, 12)
    field = Field(random.randint(500, 2000), lane_size)
    #field.set_slope({0: c.DOWN})
    field.weather = random.randint(c.CLEAR, c.RAIN)
    field.type = random.randint(c.GRASS, c.DURT)
    return field

def create_random_race(user_horse):
    field = create_random_field()
    horses = []
    for n in range(field.lane_size):
        if n == 0 and user_horse is not None: horse = user_horse
        else:
            horse = Horse(f"{n}")
            horse.skill = random.randint(c.STABLE, c.NONE)
            #horse.skill = c.NONE
            horse.stats["speed"] = random.randint(10, 100)
            horse.stats["hp"] = random.randint(10, 100)
            horse.stats["power"] = random.randint(10, 100)
            horse.fine_type = random.randint(c.GRASS, c.DURT)
        horse.set_rider(Rider(f"n"))
        #field.add_horse(horse)
        horse.set_id(n)
        horses.append(horse)
    race = Race(horses, field)
    return race

def make_df(race: Race):
    ranking = race.get_rank()
    rank_ai = race.get_pred()
    odds = race.get_odds()
    '''
    ranking_ai = [-1 for _ in range(race.get_field().lane_size)]
    for i, n in enumerate(rank_ai):
        ranking_ai[n] = i
    '''
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
                    , "Type": fine_type, "Skill": skill, "Speed": speed, "Health": hp, "Power": power, "Rank": ranking, "Predict": rank_ai, "Odds": odds})
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

@app.route("/img/slope/<string:path>")
def send_slope(path):
    dir = "result/slope/"
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
    group_id = event.source.group_id
    global users
    load_users()
    room = User(group_id)
    users.append(room)
    save_pkl(users, "pkl/users")
    print(users)
    str_join = 'keiba bot desu'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(str_join))

@handler.add(FollowEvent)
def leave_event(event):
    user_id = event.source.user_id
    global users
    load_users()
    room = User(user_id)
    users.append(room)
    save_pkl(users, "pkl/users")
    print(users)

@handler.add(LeaveEvent)
def leave_event(event):
    group_id = event.source.group_id
    global users
    load_users()
    for n in users:
        if n.id == group_id:
            users.remove(n)
    save_pkl(users, "pkl/users")
    print(users)

@handler.add(UnfollowEvent)
def leave_event(event):
    user_id = event.source.user_id
    global users
    load_users()
    for n in users:
        if n.id == user_id:
            users.remove(n)
    save_pkl(users, "pkl/users")
    print(users)

@handler.add(PostbackEvent)
def on_postback(event):
    global users
    load_users()
    command = event.postback.data
    print(command)
    user_id = event.source.user_id
    user: User = serach_room(user_id)
    if user == None:
        user = User(id)
        users.append(user)
        save_pkl(users, "pkl/users")
    user_horse: Horse = user.horse
    if command == "ikusei":
        pass
    elif command == "umajouhou":
        horse = user.horse
        if horse == None:
            line_bot_api.push_message(to = user_id, messages = FlexSendMessage("馬作成", gen_create_horse_json()))
        else:
            line_bot_api.push_message(user_id, FlexSendMessage("馬情報", gen_horse_info_json(horse, None)))
    elif command == "create_horse":
        # TODO ERROR HANDRING if User Already has player Horse
        line_bot_api.push_message(user_id, TextSendMessage("名前を送信してください"))
        user.set_status("Create_Room")
        save_pkl(users, "pkl/users")
    elif command == "race":
        user.race = create_random_race(user_horse)
        save_pkl(users, "pkl/users")
        line_bot_api.push_message(to = user_id, messages = FlexSendMessage("馬場情報", gen_field_info_json(user.race.field)))
    elif command == "buy_ticket":
        line_bot_api.push_message(to = user_id, messages = FlexSendMessage("馬券購入", gen_buy_ticket_json(user.race)))
    elif re.match("^buy_\d_", command) is not None:
        result = re.findall("\d+", command)
        if len(result) == 2: horse_id, n = [int(n) for n in result]
        else:
            horse_id = int(result[0])
            n = int(user.gold / 100)
        print((horse_id, n))
        if user.gold < n * 100 or n == 0:
            line_bot_api.push_message(user_id, TextSendMessage(f"所持金{user.gold}Gを上回っています!"))
        else:
            if horse_id in user.tickets: user.tickets[horse_id] += n
            else: user.tickets[horse_id] = n
            print(user.tickets)
            print(user.gold)
            user.gold -= n * 100
            line_bot_api.push_message(to = user_id, messages = FlexSendMessage("購入馬券", gen_receipt(user.tickets, user.gold)))
            save_pkl(users, "pkl/users")

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global users
    load_users()
    print(users)
    linelist = event.message.text
    try:
        command, token = linelist.split()
        print(f"{command}, {token}")
    except: command, token = [linelist, None]
    try:
        id = event.source.group_id
    except:
        id = event.source.user_id
    room = serach_room(id)
    if room == None:
        room = User(id)
        users.append(room)
        save_pkl(users, "pkl/users")
    print(room)
    print(room.status)
    race = room.race
    #print(room.get_status())

    df = make_df(race)
    df = df.sort_values("Rank")
    #field = create_random_field()
    if room.get_status() == "Create_Room":
        if check_herf(command):
            horse = Horse(command)
            horse.set_skill(c.NONE)
            room.horse = horse
            room.set_status(None)
            save_pkl(users, "pkl/users")
            line_bot_api.push_message(id, TextSendMessage("馬を作成しました!"))
            line_bot_api.push_message(id, FlexSendMessage("馬情報", gen_horse_info_json(horse, None)))
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
        race = create_random_race(room.horse)
        room.set_race(race)
        save_pkl(users, "pkl/users")
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
    elif command == "battle":
        pass
    elif command == "reset":
        room.tickets = {}
        room.gold = 100000
        save_pkl(users, "pkl/users")
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(f"{df}")
        )