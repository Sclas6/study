from study import Horse, Field, Race
import constant as c

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

def gen_horse_info_json(horse: Horse, odds):
    bubble = {"type": "bubble","hero": 
    {"type": "image","url": "https://1.bp.blogspot.com/-2MR7FHzJskw/UnslOIi0O0I/AAAAAAAAaQo/zKKqefuVF0I/s800/eto_uma.png",
    "aspectMode": "fit"},"body": {"type": "box","layout": "vertical","contents": [{
    "type": "box","layout": "vertical","contents": []}]}}
    if odds is not None:
        bubble["body"]["contents"].append({"type": "box","layout": "baseline","contents": [
        {"type": "text","text": "馬番号:","flex": 1},{"type": "text","text": f"{horse.id}"}]})
    bubble["body"]["contents"].append({"type": "box","layout": "baseline","contents": [
    {"type": "text","text": "馬名:","flex": 1},{"type": "text","text": f"{horse.name}"}]})
    if odds is not None:
        bubble["body"]["contents"].append(    {"type": "box","layout": "baseline","contents": [
        {"type": "text","text": "オッズ","flex": 1},{"type": "text","text": f"{odds}"}]})
    bubble["body"]["contents"].append(    {"type": "separator","color": "#FFFFFFFF","margin": "xxl"})
    bubble["body"]["contents"].append(    {"type": "box","layout": "baseline","contents": [
    {"type": "text","text": "速度:","flex": 1},
    {"type": "icon","url": get_icon(horse.stats['speed']),"offsetTop": "2px","margin": "15px"},
    {"type": "text","text": f"{horse.stats['speed']}"}]})
    bubble["body"]["contents"].append(    {"type": "box","layout": "baseline","contents": [
    {"type": "text","text": "体力:","flex": 1},
    {"type": "icon","url": get_icon(horse.stats['hp']),"offsetTop": "2px","margin": "15px"},
    {"type": "text","text": f"{horse.stats['hp']}"}]})
    bubble["body"]["contents"].append(    {"type": "box","layout": "baseline","contents": [
    {"type": "text","text": "スタミナ:","flex": 1},
    {"type": "icon","url": get_icon(horse.stats['power']),"offsetTop": "2px","margin": "15px"},
    {"type": "text","text": f"{horse.stats['power']}"}]})
    bubble["body"]["contents"].append(    {"type": "box","layout": "baseline","contents": [
    {"type": "text","text": "スキル:","flex": 1},{"type": "text","text": f"{c.SKILLS[horse.skill]}"}
    ]})

    return bubble

def gen_horses_info_json(race: Race):
    contents = {
    "type": "carousel",
    "contents": []}
    for i, horse in enumerate(race.get_horses()):
        contents["contents"].append(gen_horse_info_json(horse, race.get_odds()[i]))
    return contents

def gen_buy_ticket_json(race: Race):
    contents = {
    "type": "carousel",
    "contents": []}
    for i, horse in enumerate(race.get_horses()):
        contents["contents"].append(gen_horse_info_json(horse, race.get_odds()[i]))
        contents["contents"][i]["footer"] = {"type":"box","layout":"vertical","spacing":"sm",
        "contents":[{"type":"box","layout":"horizontal","contents":[{"type":"button","action":{"type":"postback",
        "label":"1枚","data":f"buy_{i + 1}_1"},"style":"primary"},{"type":"separator","margin":"5px"},
        {"type":"button","action":{"type":"postback","label":"10枚","data":f"buy_{i + 1}_10"},"style":"primary"},
        {"type":"separator","margin":"5px"},{"type":"button","action":{"type":"postback","label":"50枚",
        "data":f"buy_{i + 1}_50"},"style":"primary"}],"margin":"sm"},{"type":"box","layout":"vertical",
        "contents":[]},{"type":"button","action":{"type":"postback","data":f"buy_{i + 1}_all","label":"買えるだけ"},
        "style":"primary"}],"flex":0}
    return contents

def gen_create_horse_json():
    contents = {"type": "bubble","header": {"type": "box","layout": "vertical","contents": [{"type": "text",
    "text": "まだ馬を所持していません\n馬を購入しますか?", "wrap": True}]},"hero": {"type": "image",
    "url": "https://1.bp.blogspot.com/-2MR7FHzJskw/UnslOIi0O0I/AAAAAAAAaQo/zKKqefuVF0I/s800/eto_uma.png",
    "aspectMode": "fit"},"footer": {"type": "box","layout": "vertical","contents": [{"type": "button",
    "action": {"type": "postback","data": "create_horse","label": "新規購入"},"style": "primary"}]}}
    return contents

def gen_field_info_json(field: Field):
    contents = {"type":"bubble","hero":{"type":"image","url":"https://sclas.xyz:334/img/field3.jpg","size":"full",
    "aspectRatio":"20:13","aspectMode":"cover","action":{"type":"uri","uri":"http://linecorp.com/"}},"body":
    {"type":"box","layout":"vertical","contents":[{"type":"text","text":"馬場情報","weight":"bold","size":"xl"},
    {"type":"box","layout":"vertical","margin":"lg","spacing":"sm","contents":[{"type":"box","layout":"baseline",
    "spacing":"sm","contents":[{"type":"text","text":"コース","color":"#aaaaaa","size":"sm","flex":2},{"type":"text",
    "text":f"{field.length}m {c.FIELD[field.type]}","wrap":True,"color":"#666666","size":"sm","flex":5}]},{"type":"box","layout":"baseline",
    "spacing":"sm","contents":[{"type":"text","text":"出走頭数","color":"#aaaaaa","size":"sm","flex":2},{"type":"text",
    "text":f"{field.lane_size}頭","wrap":True,"color":"#666666","size":"sm","flex":5}]},{"type":"box","layout":"baseline",
    "spacing":"sm","contents":[{"type":"text","text":"天気","color":"#aaaaaa","size":"sm","flex":2},{"type":"text",
    "text": c.WEATHER[field.weather],"wrap":True,"color":"#666666","size":"sm","flex":5}]},{"type":"text","text":"高低差","size":"sm",
    "color":"#aaaaaa","align":"center"},{"type":"image","aspectMode":"cover","size":"full","aspectRatio":"480:100",
    "url":field.gen_slope_image()}]}]},"footer":{"type":"box","layout":"vertical",
    "spacing":"sm","contents":[{"type":"button","style":"primary","height":"sm",
    "action":{"type":"postback","label":"馬券購入へ(1口100円)","data":"buy_ticket"}}],"flex":0}}
    return contents

def gen_group_battle_start_json():
    pass