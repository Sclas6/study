import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import random
import time
import warnings
import cv2
import japanize_matplotlib
import numpy as np
import constant as c
import lightgbm as lgb
import os
import shutil

WIDTH, HEIGHT = [640, 480]

warnings.filterwarnings('ignore')
is_debug = True

class Horse:
    def __init__(self, name):
        self.id = None
        self.name = name
        self.stats = {"speed": 35, "hp": 35, "power": 35}
        self.stats_now = dict.copy(self.stats)
        self.condition = c.NORMAL
        self.rider = None
        self.fine_type = c.GRASS
        self.skill = c.NONE
        self.status = c.RUN

    def horse_info(self):
        return {"id":self.id, "name":self.name, "rider":self.rider, "condition":self.condition ,"skill":self.skill, "goodat":self.fine_type}

    def set_condition(self, con):
        self.condition = con
    
    def set_id(self, id):
        self.id = id

    def set_rider(self, rider):
        self.rider = rider

    def set_status(self, status):
        self.status = status

    def set_skill(self, skill):
        self.skill = skill

    def has_skill(self, skill):
        return True if self.skill == skill else False

    def get_rider(self):
        return self.rider

    def reset_condition(self):
        if self.has_skill(c.STABLE): self.set_condition(c.GOOD)
        else: self.set_condition(random.randint(c.FINE, c.BAD))

class Rider:
    def __init__(self, name):
        self.name = name
        self.condition = c.NORMAL

    def set_condition(self, con):
        self.condition = con

    def reset_condition(self):
        self.set_condition(random.randint(c.FINE, c.BAD))

class Field:
    def __init__(self, length, lane_size):
        self.length = length
        self.lane_size = lane_size
        self.type = c.GRASS
        self.slope = {0: c.FLAT}
        self.weather = c.CLEAR

    def set_weather(self, weather):
        self.weather = weather

    def set_slope(self, slope):
        self.slope = slope

    def get_slope(self, progress):
        progress = self.length - progress
        for i in range(11):
            a = i / 10
            if a in self.slope:
                f_type = self.slope[a]
            if progress < self.length * a: break
        return f_type

    def gen_slope_image(self):
        im = gen_image(self.slope, self.length)
        dir = 'result/slope/'
        im_name = str(time.time()).replace('.', '').ljust(17, '0')
        path = f"{dir}{im_name}.jpg"
        cv2.imwrite(path, im)
        files = os.listdir("result/slope")
        for i, file in enumerate(sorted(files, reverse = True)):
            if i >= 10: os.remove(f"{dir}{file}")
        url = f"https://sclas.xyz:334/img/slope/{im_name}.jpg"
        return url

class Race:
    def __init__(self, horses, field:Field):
        self.field = field
        self.lane_info = horses[:field.lane_size]
        self.odds = self.get_odds()
        self.url = None
        for i, horse in enumerate(self.lane_info, 1): 
            horse.set_id(i)
            horse.reset_condition()
            horse.get_rider().reset_condition()

    def ai_culc(self):
        condition_horse = [n.condition for n in self.get_horses()]
        condition_rider = [n.rider.condition for n in self.get_horses()]
        fine_type = [n.fine_type for n in self.get_horses()]
        skill = [n.skill for n in self.get_horses()]
        speed = [n.stats["speed"] for n in self.get_horses()]
        hp = [n.stats["hp"] for n in self.get_horses()]
        power = [n.stats["power"] for n in self.get_horses()]

        df = pd.DataFrame({"condition_horse": condition_horse, "condition_rider": condition_rider, \
                        "fine_type": fine_type, "skill": skill, "speed": speed, "hp": hp, "power": power})
        bst = lgb.Booster(model_file='keiba_model.txt')
        y_pred = bst.predict(df, num_iteration=bst.best_iteration)
        ai = pd.DataFrame({"id": [n for n in range(self.get_field().lane_size)],'predict':y_pred})
        #print(ai)
        odds = [n[1] for n in ai.values.tolist()]
        ai = ai.sort_values("predict")
        rank_ai = [int(n[0]) for n in ai.values.tolist()]
        #print(odds)
        return rank_ai, odds

    def get_pred(self):
        pred, _ = self.ai_culc()
        ranking = [-1 for _ in range(self.get_field().lane_size)]
        for i, n in enumerate(pred):
            ranking[n] = i
        return ranking

    def get_odds(self):
        _, tmp = self.ai_culc()
        odds = np.array(tmp)
        odds -= np.amin(odds) - random.uniform(1.0, 1.5)
        return [round(n, 2) for n in odds.tolist()]

    def get_field(self):
        return self.field

    def get_horses(self):
        return self.lane_info

    def start(self):
        field = self.get_field()
        img = plt.imread("static/plane.jpg")
        fig, ax = plt.subplots()
        plt.gca().spines["left"].set_visible(False)
        plt.gca().spines["top"].set_visible(False)
        plt.gca().spines["right"].set_color("red")
        plt.gca().spines["right"].set_linewidth(3)
        dir = 'result/'
        v_name = str(time.time()).replace('.', '').ljust(17, '0')
        files = os.listdir("result/")
        for i, file in enumerate(sorted(files, reverse = True)):
            if i >= 10: os.remove(f"{dir}{file}")
        url = f"https://sclas.xyz:334/video/{v_name}.mp4"
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        video = cv2.VideoWriter(f"result/{v_name}.mp4",fourcc, 10.0, (WIDTH, HEIGHT + 80))
        im_slope = gen_image(field.slope, field.length)
        race_finish = False
        rank = []
        length_lest = [field.length for _ in range(field.lane_size)]
        fix = [1.0 for _ in range(field.lane_size)]
        past_type = [None for _ in range(field.lane_size)]
        while(race_finish == False):
            for a in range(field.lane_size):
                # ゴールしているレーンはスキップ
                if a not in rank:
                    if self.get_horses()[a].has_skill(c.ACCELERATION) and past_type[a] == field.get_slope(length_lest[a] + 50):
                        fix[a] += 0.04
                        length_lest[a] = int(length_lest[a] - progress(self.get_horses()[a], field, length_lest[a]) * fix[a])
                    else:
                        fix[a] = 1.0
                        length_lest[a] = length_lest[a] - progress(self.get_horses()[a], field, length_lest[a])
                    past_type[a] = field.get_slope(length_lest[a])
                # ゴールした時
                if (length_lest[a] < 0):
                    if a not in rank :rank.append(a)
            if np.all(np.array(length_lest) < 0) == True: race_finish = True
            ax.cla()
            ax.tick_params(left=False, top=False)
            ax.set_xlim([0, field.length])
            ax.set_ylim([0 - 0.5, field.lane_size - 0.5])
            ax.set_yticks([n for n in range(len(self.get_horses()))])
            ax.set_yticklabels([n.name for n in self.get_horses()], rotation = 45)
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            ax.imshow(img, alpha=0.6,extent=[*xlim, *ylim], aspect='auto')
            imscatter([field.length - n for n in length_lest], [n for n in range(field.lane_size)], "static/horse.png", ax, 0.08)
            fig.canvas.draw()
            im = np.array(fig.canvas.renderer.buffer_rgba())
            im = cv2.cvtColor(im, cv2.COLOR_RGBA2BGR)
            im = cv2.copyMakeBorder(im, 80, 0, 0, 0, cv2.BORDER_CONSTANT, value=[255,255,255])
            im[50:150, 0:640] = im_slope
            video.write(im)
            #print(f"{length_lest}/{field.length}")
        ranking = [-1 for _ in range(field.lane_size)]
        for i, n in enumerate(rank):
            ranking[n] = i
        self.result = ranking
        self.url = url

    def get_rank(self):
        field = self.get_field()
        race_finish = False
        rank = []
        length_lest = [field.length for _ in range(field.lane_size)]
        fix = [1.0 for _ in range(field.lane_size)]
        past_type = [None for _ in range(field.lane_size)]
        while(race_finish == False):
            for a in range(field.lane_size):
                if a not in rank:
                    if self.get_horses()[a].has_skill(c.ACCELERATION) and past_type[a] == field.get_slope(length_lest[a] + 50):
                        fix[a] += 0.04
                        length_lest[a] = int(length_lest[a] - progress(self.get_horses()[a], field, length_lest[a]) * fix[a])
                    else:
                        fix[a] = 1.0
                        length_lest[a] = length_lest[a] - progress(self.get_horses()[a], field, length_lest[a])
                    past_type[a] = field.get_slope(length_lest[a])
                if (length_lest[a] < 0):
                    if a not in rank :rank.append(a)
            if np.all(np.array(length_lest) < 0) == True: race_finish = True
        ranking = [-1 for _ in range(field.lane_size)]
        for i, n in enumerate(rank):
            ranking[n] = i
        return ranking

def alart(message):
    print("\033[31m" + message + "\033[0m")

def imscatter(x, y, image, ax=None, zoom=1):
    if ax is None:
        ax = plt.gca()
    try:
        image = plt.imread(image)
    except:
        pass
    im = OffsetImage(image, zoom=zoom)
    artists = []
    for x0, y0 in zip(x, y):
        ab = AnnotationBbox(im, (x0, y0 + random.uniform(-0.025, 0.025)), xycoords='data', frameon=False)
        artists.append(ax.add_artist(ab))
    return artists

def gen_image(slope, length):
    test = [key for key in slope]

    slope_area = []
    for i in range(len(test)):
        if i != len(test) - 1:
            slope_area.append((int(test[i] * length), int(test[i + 1] * length), [i for i in slope.values()][i]))
        else: slope_area.append((int(test[i] * length), int(1 * length), [i for i in slope.values()][i]))

    xy = []
    for i, area in enumerate(slope_area):
        x = np.arange(area[0], area[1])
        if area[2] == c.UP:
            if area[0] != 0:
                y = x + xy[i - 1][1][-1] - area[0]
            else:
                y = x - 0.5
        elif area[2] == c.DOWN:
            if area[0] != 0:
                y = -1 * x + xy[i - 1][1][-1] + area[0]
            else:
                y = -1 * x - 0.5
        elif area[2] == c.FLAT:
            if area[0] != 0:
                y = np.array([xy[i - 1][1][-1] for _ in range(area[0], area[1])])
            else:
                y = np.array([1 for _ in range(area[0], area[1])])
        xy.append((x, y))
    fig, ax = plt.subplots()
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    ax.tick_params(left=False, top=False, right = False, bottom = False, labelleft=False, labelbottom = False)
    for i in xy:
        ax.plot(i[0], i[1], color = "saddlebrown", linewidth = 6)
    fig.canvas.draw()
    im = np.array(fig.canvas.renderer.buffer_rgba())
    im = cv2.cvtColor(im, cv2.COLOR_RGBA2BGR)
    im = cv2.resize(im,(WIDTH,100))
    return im

def progress(horse, field, lest):
    fix = 0.85 if horse.has_skill(c.ACCELERATION) else 1.0
    condition = int((horse.condition + horse.rider.condition)/2)
    if condition == c.FINE: fix += 0.25
    elif condition == c.GOOD: fix += 0.125
    elif condition == c.NORMAL: fix += 0
    elif condition == c.NOT_GOOD: fix += -0.125
    elif condition == c.BAD: fix += -0.25
    if horse.fine_type == field.type: fix += 0.2
    field_type = field.get_slope(lest)
    if field_type == c.FLAT: fix += 0
    elif field_type == c.UP:
        if horse.has_skill(c.ANTI_UP): fix *= 0.8
        fix *= 0.6
    elif field_type == c.DOWN:
        if horse.has_skill(c.ANTI_DOWN): fix *= 1.4
        fix *= 1.2
    if not horse.has_skill(c.ANTI_RAIN):
        if field.weather == c.CLOUDY: fix += -0.1
        elif field.weather == c.RAIN: fix += -0.2
    speed = horse.stats["speed"]
    if lest > field.length / 2:
        if horse.stats_now["hp"] > 0 and horse.status != c.REST:
            horse.stats_now["hp"] -= 1
            prog = int(random.randint(speed - 5, speed + 5) * fix)
        else:
            horse.status = c.REST
            horse.stats_now["hp"] += 1
            if horse.stats_now["hp"] >= horse.stats["hp"]: horse.status = c.RUN
            prog = int(random.randint(int(speed/2) - 5, int(speed/2) + 5) * fix)
    else:
        if horse.stats_now["power"] > 0 and horse.status != c.REST:
            horse.stats_now["power"] -= 1
            prog = int(random.randint(speed - 5, speed + 5) * fix)
        else:
            horse.status = c.REST
            horse.stats_now["power"] += 1
            if horse.stats_now["power"] >= horse.stats["power"]: horse.status = c.RUN
            prog = int(random.randint(int(speed/2) - 5, int(speed/2) + 0) * fix)
    return prog

def main():

    field = Field(2000, 3)
    #field.set_slope({0: c.FLAT, 0.2: c.UP, 0.3: c.DOWN, 0.5: c.FLAT, 0.7: c.DOWN, 0.9: c.UP})
    #field.set_slope({0: c.UP})
    # 馬情報を設定する
    horse_name = ['horseA','horseB','horseC']
    rider_name = ['riderA','riderB','riderC', "NATORI"]
    horses = []
    riders = []
    #running_horses = []
    for n in range(len(horse_name)):
        horses.append(Horse(horse_name[n]))

    for n in range(len(rider_name)):
        riders.append(Rider(rider_name[n]))

    horses = horses[:field.lane_size]

    for rider in riders:
        rider.set_condition(random.randint(c.FINE, c.BAD))
    horses[0].set_skill(c.ACCELERATION)
    for horse in horses:
        horse.set_id(0)
        if horse.skill == None: horse.set_skill(c.STABLE)
        if horse.has_skill(c.STABLE): horse.set_condition(c.GOOD)
        else: horse.set_condition(random.randint(c.FINE, c.BAD))

    random.shuffle(horses)
    random.shuffle(riders)
    for n in range(field.lane_size):
        horses[n].set_rider(riders[n])

    race = Race(horses, field)

    while True:
        try:
            money = int(input("所持金を入力して下さい\n所持金[円]: "))
            start_money = money
            print("")
            break
        except:
            alart("所持金は整数値である必要があります")

    print("--出馬表を表示します--")
    for i, horse in enumerate(race.get_horses()):
        info = horse.horse_info()
        print(f"lane{i + 1}: {info.get('id')} {info.get('name')}, Condition: {c.CONDITIONS[info.get('condition')]}, Skill: {c.SKILLS[info.get('skill')]} ")
    print("----------------------\n")

    odds = []
    for a in range(field.lane_size):
        odds.append(round(random.uniform(1.01, 5.00), 2))
    print("--オッズを表示します--")
    for a in range(field.lane_size):
        print('lane'+str(a+1)+":",end=" ")
        print(odds[a])
    print("----------------------\n")

    print("予想した馬番号を入力して下さい")
    while True:
        try:
            predict = int(input("馬番号: "))
            if predict not in [n.id for n in race.get_horses()]:
                alart("入力された馬番号は存在しません")
            else: break
        except:
            alart("馬番号は整数値である必要があります")

    print("賭ける金額を入力して下さい")
    while True:
        try:
            stakes = int(input("賭け金[円]: "))
            if stakes > money:
                alart("掛け金が所持金を超えています")
            else: break
        except:
            alart("掛け金は整数値である必要があります")
    money = money - stakes
    print("")

    print("レースを開始します")
    rank = race.get_rank()
    #rank = start_race_culc_only(field)
    print("--レース結果--")
    print(rank)
    for i, n in enumerate(rank, 1):
        print(f"{i}着: {race.get_horses()[n].id} {race.get_horses()[n].name}")
    print("--------------")

    # 金額変動を判定する
    if predict == race.get_horses()[rank[0]].id:
        money = int(money + stakes*odds[rank[0]])
    print("結果: "+str(start_money)+" → "+str(money))

    # 終了処理
    print("3秒後に終了します")
    time.sleep(3)
    #os.system('cls') if os.name in ('nt', 'dos') else os.system('clear')