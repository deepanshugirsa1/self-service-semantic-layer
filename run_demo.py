import yaml
from pathlib import Path
m = yaml.safe_load((Path(__file__).parent / "semantic_layer" / "metrics.yaml").read_text())
print(f"Semantic layer defines {len(m['metrics'])} metrics")
