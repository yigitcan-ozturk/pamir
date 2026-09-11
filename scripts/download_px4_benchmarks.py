#!/usr/bin/env python3
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmarks" / "px4_public_incidents.json"
OUT = ROOT / "benchmarks" / "data"


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    for case in payload["cases"]:
        destination = OUT / f"{case['id']}.ulg"
        if destination.exists() and destination.stat().st_size > 0:
            print(f"skip {destination.name} (already present)")
            continue

        print(f"download {case['id']}")
        request = Request(case["download_url"], headers={"User-Agent": "PAMIR-v0.1-benchmark"})
        with urlopen(request, timeout=60) as response:
            data = response.read()
        if not data.startswith(b"ULog"):
            raise RuntimeError(f"{case['id']}: response is not a ULog file")
        destination.write_bytes(data)
        print(f"  -> {destination} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
