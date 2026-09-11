#!/usr/bin/env python3
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmarks" / "px4_public_incidents.json"
OUT = ROOT / "benchmarks" / "data"

# Flight Review blocks some cloud CI ranges. Keep a pinned, public PX4 ULog
# as a transport/parser fallback so CI still proves end-to-end ULog ingestion.
PYULOG_SAMPLE = (
    "https://raw.githubusercontent.com/PX4/pyulog/"
    "ffbe3755d903e93797a89fb4fce26e0c0420a42f/test/sample.ulg"
)


def download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 PAMIR-v0.1-benchmark"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def validate_ulog(data: bytes, label: str) -> bytes:
    if not data.startswith(b"ULog"):
        raise RuntimeError(f"{label}: response is not a ULog file")
    return data


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    blocked = []

    for case in payload["cases"]:
        destination = OUT / f"{case['id']}.ulg"
        if destination.exists() and destination.stat().st_size > 0:
            print(f"skip {destination.name} (already present)")
            continue

        print(f"download {case['id']}")
        try:
            data = validate_ulog(download(case["download_url"]), case["id"])
        except (HTTPError, URLError) as exc:
            blocked.append(case["id"])
            print(f"  Flight Review unavailable from runner: {exc}")
            continue
        destination.write_bytes(data)
        print(f"  -> {destination} ({len(data)} bytes)")

    # Always download a source-pinned public ULog from PX4/pyulog. This is not
    # an incident oracle; it validates real binary ULog transport + parsing.
    fallback = OUT / "px4-pyulog-sample.ulg"
    if not fallback.exists() or fallback.stat().st_size == 0:
        print("download pinned PX4/pyulog sample")
        fallback.write_bytes(validate_ulog(download(PYULOG_SAMPLE), "px4-pyulog-sample"))
        print(f"  -> {fallback} ({fallback.stat().st_size} bytes)")

    if blocked:
        print("NOTICE: Flight Review blocked incident downloads for: " + ", ".join(blocked))
        print("CI will validate the pinned public PX4 ULog; incident narrative validation remains gated until source access is available.")


if __name__ == "__main__":
    main()
