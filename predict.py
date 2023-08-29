from study import *
import lightgbm as lgb

lane_size = random.randint(2, 18)
field = Field(200, lane_size)
field.length = random.randint(100, 3000)
field.weather = random.randint(c.CLEAR, c.RAIN)
field.type = random.randint(c.GRASS, c.DURT)
horses = []
for n in range(lane_size):
    horse = Horse(f"{n}")
    horse.set_id(n)
    horse.set_rider(Rider(n, f"n"))
    horse.fine_type = random.randint(c.GRASS, c.DURT)
    horse.skill = random.randint(c.STABLE, c.ANTI_RAIN)
    horse.stats["speed"] = random.randint(10, 100)
    horse.stats["hp"] = random.randint(10, 100)
    horse.stats["power"] = random.randint(10, 100)
    horses.append(horse)

race = Race(horses, field)
#print(ranking)
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
                    , "Type": fine_type, "Skill": skill, "Speed": speed, "Health": hp, "Power": power})

bst = lgb.Booster(model_file='keiba2_model.txt')
y_pred = bst.predict(df, num_iteration=bst.best_iteration)

print(df)
ai = pd.DataFrame({"id": [n for n in range(field.lane_size)],'predict':y_pred})
ai = ai.sort_values("predict")

rank_ai = [int(n[0]) for n in ai.values.tolist()]
rank = race.get_rank()

print(rank)
print(rank_ai)
