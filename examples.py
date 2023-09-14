from study import Horse, Field
import csv
import random
from constant import *

def horse():
    horses = []
    with open("Horses.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            horse = Horse(row[0])
            horse.stats = {"speed": int(row[1]), "hp": int(row[2]), "power": int(row[3])}
            horse.stats_now = horse.stats
            horses.append(horse)
    random.shuffle(horses)
    return horses

def field():
    fields = []
    tokyo = Field(random.randint(500, 2000), random.randint(4, 12))
    tokyo.name = "東京"
    tokyo.slope = {0: FLAT, 0.1: DOWN, 0.4:UP, 0.5: DOWN, 0.6: FLAT, 0.7: UP, 0.8: FLAT}
    fields.append(tokyo)
    sapporo = Field(random.randint(500, 2000), random.randint(4, 12))
    sapporo.name = "札幌"
    sapporo.slope = {0: FLAT}
    fields.append(sapporo)
    hakodate = Field(random.randint(500, 2000), random.randint(4, 12))
    hakodate.name = "函館"
    hakodate.slope = {0: FLAT, 0.1: UP, 0.3: DOWN, 0.7: UP, 0.9: FLAT}
    fields.append(hakodate)
    hukushima = Field(random.randint(500, 2000), random.randint(4, 12))
    hukushima.name = "福島"
    hukushima.slope = {0: DOWN, 0.1: UP, 0.2: FLAT, 0.6: DOWN, 0.7:FLAT, 0.8: UP}
    fields.append(hukushima)
    niigata = Field(random.randint(500, 2000), random.randint(4, 12))
    niigata.name = "新潟"
    niigata.slope = {0: FLAT, 0.4: UP, 0.5: DOWN, 0.6: FLAT}
    fields.append(niigata)
    nakayama = Field(random.randint(500, 2000), random.randint(4, 12))
    nakayama.name = "中山"
    nakayama.slope = {0: DOWN, 0.1: FLAT, 0.5:UP, 0.8: DOWN}
    fields.append(nakayama)
    chukyo = Field(random.randint(500, 2000), random.randint(4, 12))
    chukyo.name = "中京"
    chukyo.slope = {0: FLAT, 0.1: UP, 0.3:DOWN, 0.8: UP, 0.9: FLAT}
    fields.append(chukyo)
    kyoto = Field(random.randint(500, 2000), random.randint(4, 12))
    kyoto.name = "京都"
    kyoto.slope = {0: FLAT, 0.4: UP, 0.5: DOWN, 0.6: FLAT}
    fields.append(kyoto)
    hanshin = Field(random.randint(500, 2000), random.randint(4, 12))
    hanshin.name = "阪神"
    hanshin.slope = {0: DOWN, 0.1: UP, 0.5: FLAT}
    fields.append(hanshin)
    ogura = Field(random.randint(500, 2000), random.randint(4, 12))
    ogura.name = "小倉"
    ogura.slope = {0: FLAT, 0.2: UP, 0.3:FLAT, 0.6: UP, 0.8: DOWN}
    fields.append(ogura)
    random.shuffle(fields)
    return fields