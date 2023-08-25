from study import *
import lightgbm as lgb

lane_size = random.randint(2, 18)
field = Field(200, lane_size)
field.length = random.randint(100, 3000)
field.weather = random.randint(c.CLEAR, c.RAIN)
field.type = random.randint(c.GRASS, c.DURT)
for n in range(lane_size):
    horse = Horse(n, f"{n}")
    horse.set_rider(Rider(n, f"n"))
    horse.fine_type = random.randint(c.GRASS, c.DURT)
    horse.condition = random.randint(c.FINE, c.BAD)
    horse.rider.condition = random.randint(c.FINE, c.BAD)
    horse.skill = random.randint(c.STABLE, c.ANTI_RAIN)
    horse.stats["speed"] = random.randint(10, 100)
    horse.stats["hp"] = random.randint(10, 100)
    horse.stats["power"] = random.randint(10, 100)
    field.add_horse(horse)
#print(ranking)
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
df = pd.DataFrame({"weather": weather, "field_type": field_type, "condition_horse": condition_horse, "condition_rider": condition_rider\
                , "fine_type": fine_type, "skill": skill, "speed": speed, "hp": hp, "power": power})

bst = lgb.Booster(model_file='keiba2_model.txt')
y_pred = bst.predict(df, num_iteration=bst.best_iteration)

print(df)
ai = pd.DataFrame({"id": [n for n in range(field.lane_size)],'predict':y_pred})
ai = ai.sort_values("predict")

rank_ai = [int(n[0]) for n in ai.values.tolist()]
rank = start_race_culc_only(field)

print(rank)
print(rank_ai)
