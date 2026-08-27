import pandas as pd
from pathlib import Path
import random
OUT = Path(__file__).parent / "raw"
OUT.mkdir(parents=True, exist_ok=True)
pd.DataFrame([{"user_id": f"u{i}", "plan": random.choice(["basic","pro"]), "mrr": round(random.uniform(9,99),2)} for i in range(300)]).to_csv(OUT / "subscriptions.csv", index=False)
print("Generated subscriptions data")
