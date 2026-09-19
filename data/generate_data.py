"""Generate synthetic subscription data + a load manifest for freshness checks."""
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

OUT = Path(__file__).parent / "raw"
OUT.mkdir(parents=True, exist_ok=True)

RNG = random.Random(42)
PLANS = ["basic", "pro", "enterprise"]
REGIONS = ["US", "EU", "APAC"]


def generate(n: int = 300) -> pd.DataFrame:
    base = datetime(2026, 1, 1)
    rows = []
    for i in range(n):
        plan = RNG.choice(PLANS)
        mrr = {"basic": 9, "pro": 49, "enterprise": 99}[plan] + RNG.uniform(0, 10)
        rows.append(
            {
                "user_id": f"u{i}",
                "plan": plan,
                "mrr": round(mrr, 2),
                "region": RNG.choice(REGIONS),
                "signup_date": (base + timedelta(days=RNG.randint(0, 240))).strftime("%Y-%m-%d"),
                "is_active": RNG.random() > 0.12,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    df = generate()
    df.to_csv(OUT / "subscriptions.csv", index=False)
    manifest = {
        "dataset": "subscriptions",
        "rows": int(df.shape[0]),
        "loaded_at": datetime.now(timezone.utc).isoformat(),
        "source": "generate_data.py",
    }
    (OUT / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(df)} subscriptions + load manifest")


if __name__ == "__main__":
    main()
