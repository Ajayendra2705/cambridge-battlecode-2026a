import gzip, json
from pathlib import Path
from vis_gaps import pair_gaps


path = (
    Path(__file__).resolve().parent.parent
    / "data/fights/ranked/1f103d13-37f0-48a0-8d08-d797c4bcd426.jsonl.gz"
)

with gzip.open(path, "rt") as f:
    lines = [json.loads(l) for l in f]
metadata, rounds = lines[0], lines[1:]
print(rounds[0])
print(rounds[1])
print(rounds[20])

pair_gaps(rounds)
