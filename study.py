# ライブラリのインポート
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
import random
import time
import warnings
import cv2
import numpy as np
import constant

WIDTH, HEIGHT = [640, 480]

warnings.filterwarnings('ignore')
is_debug = True

class Horse:
    id = None
    name = None
    confition = constant.NORMAL
    rider = None
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def horse_info(self):
        return f"{self.id} {self.name} {self.rider.name}"
    
    def set_condition(self, con):
        self.confition = con
    
    def set_rider(self, rider):
        self.rider = rider
    
class Rider:
    id = None
    name = None
    condition = constant.NORMAL
    
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def set_condition(self, con):
        self.condition = con

class Field:
    length = None
    lane_size = None
    type = constant.GRASS
    slope = {constant.FLAT}
    weather = constant.CLEAR
    
    def __init__(self, length, lane_size):
        self.length = length
        self.lane_size = lane_size
    
    def set_weather(self, weather):
        self.weather = weather

    def set_slope(self, slope):
        self.slope = slope

    def get_type(self, progress):
        progress = self.length - progress
        for i in range(11):
            a = i / 10
            if a in self.slope:
                f_type = self.slope[a]
            if progress < self.length * a: break 
        return f_type

# allからnum分だけランダムに選択する関数
def random_select(all, num):
    list = []
    for a in random.sample(all, num):
        list.append(a)
    return list

#2次元配列allのnum列を1~size行を抽出する関数
def append_2Dlist(all, num, size):
    list = []
    for a in range(size):
        list.append(all[a][num])
    return list

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

def progress(horse, field):
    return random.randrange(1,10)

def gen_image(slope, length):
    test = [key for key in slope]

    slope_area = []
    for i in range(len(test)):
        if i != len(test) - 1:
            slope_area.append((int(test[i] * length), int(test[i + 1] * length), [i for i in slope.values()][i]))
        else: slope_area.append((int(test[i] * length), int(1 * length), [i for i in slope.values()][i]))

    print(slope_area)
    xy = []
    for i, area in enumerate(slope_area):
        x = np.arange(area[0], area[1])
        match area[2]:
            case constant.UP:
                if area[0] != 0:
                    print(xy[i - 1][1][-1])
                    y = x + xy[i - 1][1][-1] - area[0]
                else:
                    y = x - 0.5
            case constant.DOWN:
                if area[0] != 0:
                    print(xy[i - 1][1][-1])
                    print(area[0])
                    y = -1 * x + xy[i - 1][1][-1] + area[0]
                else:
                    y = -1 * x - 0.5
            case constant.FLAT:
                if area[0] != 0:
                    y = np.array([xy[i - 1][1][-1] for _ in range(area[0], area[1])])
                else: 
                    y = np.array([1 for _ in range(area[0], area[1])])
        y = y
        xy.append((x, y))
    fig, ax = plt.subplots()
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    ax.tick_params(left=False, top=False, right = False, bottom = False, labelleft=False, labelbottom = False)
    for i in xy:
        ax.plot(i[0], i[1])
    fig.canvas.draw()
    im = np.array(fig.canvas.renderer.buffer_rgba())
    im = cv2.cvtColor(im, cv2.COLOR_RGBA2BGR)
    im = cv2.resize(im,(WIDTH,100))
    return im

def main():

    field = Field(200, 3)
    field.set_slope({0: constant.FLAT, 0.2: constant.UP, 0.3: constant.DOWN, 0.5: constant.FLAT, 0.7: constant.DOWN, 0.9: constant.UP})

    # 馬情報を設定する
    horse_number = []
    horse_name = ['horseA','horseB','horseC']
    rider_name = ['riderA','riderB','riderC']
    horses = []
    riders = []
    running_horses = []
    for n in range(len(horse_name)):
        horses.append(Horse(n, horse_name[n]))
        horse_number.append(n)

    for n in range(len(rider_name)):
        riders.append(Rider(n, rider_name[n]))

    for rider in riders:
        rider.set_condition(random.randint(constant.FINE, constant.BAD))
    for horse in horses:
        horse.set_condition(random.randint(constant.FINE, constant.BAD))

    random.shuffle(horses)
    random.shuffle(riders)
    for n in range(field.lane_size):
        horses[n].set_rider(riders[n])
        running_horses.append(horses[n])

    # レーンに配置する
    lane_info = [horse for horse in running_horses]

    # 所持金を入力する
    while True:
        try:
            money = int(input("所持金を入力して下さい\n所持金[円]: "))
            start_money = money
            print("")
            break
        except:
            alart("所持金は整数値である必要があります")

    # 出馬表を出力する
    print("--出馬表を表示します--")
    for i, lane in enumerate(lane_info):
        print(f"lane{i + 1}: {lane.horse_info()}")
    print("----------------------\n")

    # オッズを出力する
    odds = []
    for a in range(field.lane_size):
        odds.append(round(random.uniform(1.01, 5.00), 2))
    print("--オッズを表示します--")
    for a in range(field.lane_size):
        print('lane'+str(a+1)+":",end=" ")
        print(odds[a])
    print("----------------------\n")

    # 予想する
    print("予想した馬番号を入力して下さい")
    while True:
        try:
            predict = int(input("馬番号: "))
            if predict not in horse_number:
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

    # コースを作成する
    length_lest = []
    for a in range(field.lane_size):
        length_lest.append(field.length)

    # レースを開始する
    print("レースを開始します")
    goal_min = 1
    race_graph_df = pd.DataFrame(columns = horse_number[:field.lane_size])
    img = plt.imread("static/plane.jpg")
    fig, ax = plt.subplots()
    plt.gca().spines["left"].set_visible(False)
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_color("red")
    plt.gca().spines["right"].set_linewidth(3) 
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video = cv2.VideoWriter('result/video.mp4',fourcc, 20.0, (WIDTH, HEIGHT))

    im_slope = gen_image(field.slope, field.length)

    race_finish = False
    rank = []
    # 1位が決まるまで繰り返す
    while(race_finish == False):
        ax.cla()
        ax.tick_params(left=False, top=False)
        ax.set_xlim([0, field.length])
        ax.set_ylim([0 - 0.5, field.lane_size - 0.5])
        ax.set_yticks(horse_number)
        ax.set_yticklabels(horse_name)
        for a in range(field.lane_size):
            # ゴールしているレーンはスキップ
            length_lest[a] = length_lest[a] - progress(lane_info[a], field)
            #print(field.get_type(length_lest[a]))
            #グラフ用にデータフレームとして保存しておく
            df_race = pd.DataFrame(data=[length_lest], columns=horse_number[:field.lane_size])
            race_graph_df = pd.concat([race_graph_df, df_race], ignore_index = True)
            
            # ゴールした時
            if (length_lest[a] <= 0):
                #win_lane = a
                if a not in rank :rank.append(a)
                #race_finish = True
        print(length_lest)
        if np.all(np.array(length_lest) <= 0) == True: race_finish = True
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ax.imshow(img, alpha=0.6,extent=[*xlim, *ylim], aspect='auto')
        imscatter([field.length - n for n in length_lest], [n for n in range(field.lane_size)], "static/horse.png", ax, 0.08)
        fig.canvas.draw()
        im = np.array(fig.canvas.renderer.buffer_rgba())
        im = cv2.cvtColor(im, cv2.COLOR_RGBA2BGR)
        im = cv2.copyMakeBorder(im, 80, 0, 0, 0, cv2.BORDER_CONSTANT, value=[255,255,255])
        im[50:150, 0:640] = im_slope
        cv2.imshow("test", im)
        cv2.waitKey(1)
        #video.write(im)
    # レース結果を表示する
    print("--レース結果--")
    print(rank)
    for n in range(len(rank)):
        print(f"{n + 1}着: {lane_info[rank[n]].id} {lane_info[rank[n]].name}")
    #print("1着: "+str(lane_info[rank[0]].id))
    print("--------------")

    # レースのグラフを表示する
    '''
    _ = plt.get_cmap('tab10')
    plt.figure(figsize=[9,5])
    plt.plot(race_graph_df)
    plt.title("Race Result")
    plt.xlabel("Time")
    plt.ylabel("Length Lest")
    plt.show()
    '''
    # 金額変動を判定する
    if predict == lane_info[rank[0]].id:
        money = int(money + stakes*odds[rank[0]])
    print("結果: "+str(start_money)+" → "+str(money))

    # 終了処理
    print("3秒後に終了します")
    time.sleep(3)
    #os.system('cls') if os.name in ('nt', 'dos') else os.system('clear')

if __name__ == "__main__":
    main()