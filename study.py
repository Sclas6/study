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

WIDTH, HEIGHT = [480, 640]

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
    weather = constant.CLEAR
    
    def __init__(self, length, lane_size):
        self.length = length
        self.lane_size = lane_size
    
    def set_weather(self, weather):
        self.weather = weather

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
        ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False) 
        artists.append(ax.add_artist(ab)) 
    return artists 

def main():

    field = Field(200, 3)

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
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video = cv2.VideoWriter('result/video.mp4',fourcc, 20.0, (HEIGHT, WIDTH))

    race_finish = False
    # 1位が決まるまで繰り返す
    while(race_finish == False):
        ax.cla()
        ax.set_title("Race Result")
        ax.set_xlabel("Time")
        ax.tick_params(left=False, top=False)
        ax.set_xlim([0, field.length])
        ax.set_ylim([0 - 0.5, field.lane_size - 0.5])
        ax.set_yticks(horse_number)
        ax.set_yticklabels(horse_name)
        for a in range(field.lane_size):
            # ゴールしているレーンはスキップ
            length_lest[a] = length_lest[a] - random.randrange(1,10)
            #グラフ用にデータフレームとして保存しておく
            df_race = pd.DataFrame(data=[length_lest], columns=horse_number[:field.lane_size])
            race_graph_df = pd.concat([race_graph_df, df_race], ignore_index = True)
            
            # ゴールした時
            if (length_lest[a] <= 0) and (goal_min > length_lest[a]):
                win_lane = a
                goal_min = length_lest[a]
                race_finish = True
                print(win_lane)
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ax.imshow(img, alpha=0.6,extent=[*xlim, *ylim], aspect='auto')
        imscatter([field.length - n for n in length_lest], [n for n in range(field.lane_size)], "static/horse.png", ax, 0.08)
        #plt.pause(0.001)
        #'''
        fig.canvas.draw()
        im = np.array(fig.canvas.renderer.buffer_rgba())
        im = cv2.cvtColor(im, cv2.COLOR_RGBA2BGR)
        video.write(im)
        #'''
        plt.pause(0.001)
        #print(length_lest[0])
    # レース結果を表示する
    print("--レース結果--")
    print("1着: "+str(lane_info[win_lane].id))
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
    if predict == lane_info[win_lane].id:
        money = int(money + stakes*odds[win_lane])
    print("結果: "+str(start_money)+" → "+str(money))

    # 終了処理
    print("3秒後に終了します")
    time.sleep(3)
    #os.system('cls') if os.name in ('nt', 'dos') else os.system('clear')

if __name__ == "__main__":
    main()