import datetime
from study import Horse, Field, Race
import constant as c
from sec import *

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
    return f"{URL}/img/icon/{icon}.png"

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
    bubble["body"]["contents"].append(    {"type": "separator","color": "#FFFFFF00","margin": "xxl"})
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
        "label":"1枚","data":f"buy_{i + 1}_1"},"style":"primary"},{"type":"separator","margin":"5px", "color": "#FFFFFF00"},
        {"type":"button","action":{"type":"postback","label":"10枚","data":f"buy_{i + 1}_10"},"style":"primary"},
        {"type":"separator","margin":"5px", "color": "#FFFFFF00"},{"type":"button","action":{"type":"postback","label":"50枚",
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
    contents = {"type":"bubble","hero":{"type":"image","url":f"{URL}/img/field3.jpg","size":"full",
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
    "action":{"type":"postback","label":"馬券購入へ(1口100G)","data":"buy_ticket"}}],"flex":0}}
    return contents

def gen_receipt(tickets: dict, gold):
    gold_sum = sum([100 * n for n in tickets.values()])
    now = datetime.datetime.now()
    contents ={
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "◆◇◆ご来場いただきありがとうございます◆◇◆\n最後のレースまでお楽しみください",
        "align": "center",
        "size": "xxs",
        "wrap": True
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "box",
            "layout": "baseline",
            "contents": [
              {
                "type": "text",
                "text": "■",
                "gravity": "center",
                "size": "sm",
                "align": "end"
              },
              {
                "type": "text",
                "text": "□",
                "gravity": "center",
                "size": "xl",
                "offsetTop": "3px"
              },
              {
                "type": "text",
                "text": "■",
                "gravity": "center",
                "size": "sm",
                "align": "start"
              }
            ],
            "offsetTop": "7px",
            "width": "65px"
          },
          {
            "type": "text",
            "text": "ご利用明細",
            "align": "center",
            "gravity": "center",
            "size": "xl",
            "weight": "bold",
            "offsetTop": "1px"
          },
          {
            "type": "box",
            "layout": "baseline",
            "contents": [
              {
                "type": "text",
                "text": "■",
                "gravity": "center",
                "size": "sm",
                "align": "end"
              },
              {
                "type": "text",
                "text": "□",
                "gravity": "center",
                "size": "xl",
                "offsetTop": "3px"
              },
              {
                "type": "text",
                "text": "■",
                "gravity": "center",
                "size": "sm",
                "align": "start"
              }
            ],
            "offsetTop": "7px",
            "width": "65px"
          }
        ],
        "height": "50px"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": f"{now.strftime('%Y年%m月%d日')}",
                "size": "xs"
              },
              {
                "type": "separator",
                "color": "#FFFFFF00",
                "margin": "lg"
              },
              {
                "type": "text",
                "text": "京都",
                "size": "md",
                "weight": "bold"
              },
              {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                  {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                      {
                        "type": "text",
                        "text": "11",
                        "align": "center",
                        "weight": "bold",
                        "color": "#FFFFFF"
                      }
                    ],
                    "backgroundColor": "#000000",
                    "width": "35px",
                    "justifyContent": "center"
                  },
                  {
                    "type": "text",
                    "text": "レース",
                    "align": "start"
                  }
                ]
              }
            ],
            "width": "100px"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                      {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                          {
                            "type": "text",
                            "text": "WIN",
                            "align": "center",
                            "size": "xxs"
                          },
                          {
                            "type": "text",
                            "text": "単\n　\n勝",
                            "wrap": True,
                            "align": "center",
                            "size": "xl",
                            "margin": "md"
                          },
                          {
                            "type": "text",
                            "text": "WIN",
                            "align": "center",
                            "size": "xxs",
                            "margin": "md"
                          }
                        ],
                        "borderColor": "#000000",
                        "borderWidth": "normal",
                        "width": "35px"
                      }
                    ],
                    "width": "35px",
                    "justifyContent": "center",
                    "alignItems": "center"
                  },
                  {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        # Tickets
                    ],
                    "justifyContent": "center"
                  }
                ]
              },
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                      {
                        "type": "text",
                        "text": "合計",
                        "size": "xs"
                      },
                      {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                          {
                            "type": "text",
                            "size": "xxs",
                            "margin": "none",
                            "text": "★"
                          }
                        ],
                        "width": "12px"
                      },
                      {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                          {
                            "type": "text",
                            "size": "xxs",
                            "margin": "none",
                            "text": "★"
                          }
                        ],
                        "width": "12px"
                      },
                      {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                          {
                            "type": "text",
                            "size": "xxs",
                            "margin": "none",
                            "text": "★"
                          }
                        ],
                        "width": "12px"
                      },
                      {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                          {
                            "type": "text",
                            "size": "xxs",
                            "margin": "none",
                            "text": "★"
                          }
                        ],
                        "width": "12px"
                      },
                      {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                          {
                            "type": "text",
                            "text": f"{gold_sum}G",
                            "size": "xs"
                          }
                        ],
                        "width": "65px",
                        "alignItems": "flex-end",
                        "justifyContent": "flex-end"
                      }
                    ],
                    "alignItems": "center",
                    "justifyContent": "flex-end",
                    "offsetTop": "4px"
                  },
                  {
                    "type": "separator",
                    "color": "#FFFFFF00",
                    "margin": "md"
                  },
                  {
                    "type": "text",
                    "text": f"{now.strftime('%Y/%m/%d %H:%M:%S')}",
                    "size": "xs"
                  }
                ],
                "alignItems": "flex-end"
              }
            ]
          }
        ]
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "残高:",
            "flex": 1,
            "size": "xs",
            "align": "center"
          },
          {
            "type": "text",
            "text": f"{gold}G",
            "size": "xs",
            "align": "center"
          }
        ],
        "borderWidth": "normal",
        "borderColor": "#000000",
        "width": "180px",
        "offsetTop": "8px",
        "alignItems": "center"
      }
    ],
    "alignItems": "center"
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "separator",
        "margin": "xxl",
        "color": "#FFFFFF00"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "postback",
              "label": "確定",
              "data": "buy_end"
            },
            "style": "primary"
          },
          {
            "type": "separator",
            "margin": "md",
            "color": "#FFFFFF00"
          },
          {
            "type": "button",
            "action": {
              "type": "postback",
              "label": "追加購入",
              "data": "buy_ticket"
            },
            "style": "secondary"
          }
        ]
      }
    ]
  }
}
    for horse_id in tickets:
        contents["body"]["contents"][2]["contents"][1]["contents"][0]["contents"][1]["contents"].append(
{
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                          {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                              {
                                "type": "text",
                                "text": f"{horse_id}",
                                "weight": "bold",
                                "size": "lg",
                                "gravity": "center",
                                "align": "center",
                                "offsetBottom": "3px"
                              }
                            ],
                            "borderColor": "#000000",
                            "borderWidth": "normal",
                            "width": "30px",
                            "height": "22px",
                            "offsetStart": "3px",
                            "justifyContent": "center"
                          },
                          {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                              {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                  {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                      {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                          {
                                            "type": "text",
                                            "size": "xxs",
                                            "margin": "none",
                                            "text": f"{''.join(['☆' for _ in range(6 - len(str(tickets[horse_id] * 100)))]) if len(str(tickets[horse_id] * 100)) <= 5 else ' '}"
                                          }
                                        ],
                                        "width": f"{12 * (6 - len(str(tickets[horse_id] * 100))) if len(str(tickets[horse_id] * 100)) <= 5 else 0}px"
                                      },
                                      {
                                        "type": "text",
                                        "text": f"{tickets[horse_id] * 100}",
                                        "size": "xl",
                                        "align": "start",
                                        "gravity": "center",
                                        "offsetEnd": "2px"
                                      }
                                    ],
                                    "alignItems": "center",
                                    "offsetStart": "12px"
                                  }
                                ]
                              },
                              {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": "G",
                                    "gravity": "bottom",
                                    "size": "xs",
                                    "align": "start",
                                    "offsetTop": "2px"
                                  }
                                ],
                                "width": "10px",
                                "justifyContent": "center"
                              }
                            ],
                            "justifyContent": "flex-start",
                            "alignItems": "center"
                          }
                        ],
                        "justifyContent": "center",
                        "alignItems": "center"
                      }
    )
    return contents

def gen_retry_json():
    return {"type":"bubble","body":{"type":"box","layout":"vertical","contents":[{"type":"text","text":"レース中です。\n暫くお待ちください。","wrap":True}]},"footer":{"type":"box","layout":"vertical","contents":[{"type":"button","action":{"type":"postback","label":"リトライ","data":"buy_end"},"style":"secondary"}]}}
    

def gen_group_battle_start_json():
    pass