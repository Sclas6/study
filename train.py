from study import *
import math
import lightgbm as lgb

def train_test_split(df):
    columns=['rank', 'query_id']
    feature = list(df.drop(columns, axis=1).columns)

    group = df['query_id'].value_counts()
    df = df.set_index(['query_id'])
    group = group.sort_index()

    df.sort_index(inplace=True)
    x = df[feature]
    y = df['rank']
    return x, y, group

df = pd.DataFrame()
for index in range(10):
    lane_size = random.randint(2, 18)
    length = random.randint(200, 5000)
    field = Field(length, lane_size)
    #field.set_slope({0: c.DOWN})
    field.length = random.randint(100, 3000)
    field.weather = random.randint(c.CLEAR, c.RAIN)
    field.type = random.randint(c.GRASS, c.DURT)

    horses = []
    for n in range(lane_size):
        horse = Horse(f"{n}")
        horse.set_id(n)
        horse.set_rider(Rider(f"n"))
        horse.fine_type = random.randint(c.GRASS, c.DURT)
        horse.skill = random.randint(c.STABLE, c.ANTI_RAIN)
        horse.stats["speed"] = random.randint(10, 100)
        horse.stats["hp"] = random.randint(10, 100)
        horse.stats["power"] = random.randint(10, 100)
        horses.append(horse)
    race = Race(horses, field)
    ranking = race.get_rank()
    print(ranking)

    weather = [field.weather for _ in range(field.lane_size)]
    field_type = [field.type for _ in range(field.lane_size)]
    condition_horse = [n.condition for n in race.get_horses()]
    condition_rider = [n.rider.condition for n in race.get_horses()]
    fine_type = [n.fine_type for n in race.get_horses()]
    skill = [n.skill for n in race.get_horses()]
    speed = [n.stats["speed"] for n in race.get_horses()]
    hp = [n.stats["hp"] for n in race.get_horses()]
    power = [n.stats["power"] for n in race.get_horses()]
    lane = [n for n in range(len(race.get_horses()))]
    query_id = [index for _ in range(field.lane_size)]

    df = pd.concat([df, pd.DataFrame({"condition_horse": condition_horse, "condition_rider": condition_rider, "fine_type": fine_type, \
                                      "skill": skill, "speed": speed, "hp": hp, "power": power, "rank": ranking, "query_id": query_id})])
    target = df["rank"]
    feature = df.drop("rank", axis=1)

test_size = 0.2
point = max(df['query_id']) * test_size
point = math.trunc(point)
train = df[df['query_id'] > point]
test = df[df['query_id'] <= point]
x_train, y_train, group = train_test_split(train)
x_test, y_test, eval_group = train_test_split(test)

model = lgb.LGBMRanker(random_state=0)
model.fit(x_train, y_train, group=group, eval_set=[(x_test, y_test)], eval_group=[list(eval_group)])
model.booster_.save_model('keiba4_model.txt')

feature = list(df.drop(columns=['rank', 'query_id']).columns)
importance = np.array(model.feature_importances_)
df = pd.DataFrame({'feature':feature, 'importance':importance})
df = df.sort_values('importance', ascending=True)

n = len(df) # 説明変数の項目数を取得
values = df['importance'].values
plt.barh(range(n), values)
values = df['feature'].values
plt.yticks(np.arange(n), values)
plt.show()
print(df)