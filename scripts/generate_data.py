import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta
import random

NUM_ROWS = 1_000_000

event_types = ["page_view", "click", "purchase"]
products = [f"product_{i}" for i in range(1, 51)]

start_date = datetime.now() - timedelta(days=1)

data = []

for _ in range(NUM_ROWS):
    event_time = start_date + timedelta(
        seconds=random.randint(0, 86400)
    )

    data.append({
        "event_id": str(uuid.uuid4()),
        "user_id": random.randint(1, 10000),
        "event_type": random.choice(event_types),
        "product_id": random.choice(products),
        "amount": round(random.uniform(10, 500), 2),
        "event_time": event_time
    })

df = pd.DataFrame(data)

df.to_csv("events.csv", index=False)

print("Generated 1M events successfully.")
