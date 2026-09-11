#!/usr/bin/env python3
import json
from hashlib import sha256
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

# Portable real-world incident/control pair attached directly to a public GitHub
# issue. The files are ULog binaries with an extra .txt suffix only because of
# GitHub attachment rules. This pair keeps incident validation reproducible in CI
# even when logs.px4.io returns HTTP 403 to cloud runners.
PORTABLE_CASES = (
    (
        "github-indoor-crash-2025",
        "https://github.com/user-attachments/files/23960520/crashed_log_6_2025-11-23-21-01-00.ulg.txt",
    ),
    (
        "github-indoor-control-2025",
        "https://github.com/user-attachments/files/23960519/not_crashed_log_1_2025-11-23-20-26-38.ulg.txt",
    ),
)


def download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 PAMIR-v0.1-benchmark"})
    with urlopen(request, timeout=60) as response:
        return response.read()


PINNED_SHA256 = {
    "github-indoor-crash-2025": "7ea3869991912d9f2e264b53bebf3afc30e8b6595fd9837d76cf8e24cc7b0179",
    "github-indoor-control-2025": "6288e117e86b4e4365f833e55137b5285db12a7f1339063783f7ce76971f26e5",
    "px4-pyulog-sample": "81952e6059bc095717e7911c010e07f85749d6b04d332a5ffc51575a3fd0a558",
}


def validate_ulog(data: bytes, label: str) -> bytes:
    if len(data) < 16 or not data.startswith(b"ULog\x01\x12\x35"):
        raise RuntimeError(f"{label}: response is not a ULog file")
    expected = PINNED_SHA256.get(label)
    if expected and sha256(data).hexdigest() != expected:
        raise RuntimeError(f"{label}: SHA-256 mismatch")
    return data


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    blocked = []

    for case in payload["cases"]:
        destination = OUT / f"{case['id']}.ulg"
        if destination.exists() and destination.stat().st_size > 0:
            validate_ulog(destination.read_bytes(), destination.stem)
            print(f"skip {destination.name} (already verified)")
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

    for case_id, url in PORTABLE_CASES:
        destination = OUT / f"{case_id}.ulg"
        if destination.exists() and destination.stat().st_size > 0:
            validate_ulog(destination.read_bytes(), destination.stem)
            print(f"skip {destination.name} (already verified)")
            continue
        print(f"download {case_id}")
        data = validate_ulog(download(url), case_id)
        destination.write_bytes(data)
        print(f"  -> {destination} ({len(data)} bytes)")

    # Always download a source-pinned public ULog from PX4/pyulog. This is not
    # an incident oracle; it validates real binary ULog transport + parsing.
    fallback = OUT / "px4-pyulog-sample.ulg"
    if not fallback.exists() or fallback.stat().st_size == 0:
        print("download pinned PX4/pyulog sample")
        fallback.write_bytes(validate_ulog(download(PYULOG_SAMPLE), "px4-pyulog-sample"))
        print(f"  -> {fallback} ({fallback.stat().st_size} bytes)")

    validate_ulog(fallback.read_bytes(), "px4-pyulog-sample")

    if blocked:
        print("NOTICE: Flight Review blocked incident downloads for: " + ", ".join(blocked))
        print("CI will still validate the portable public GitHub incident/control pair plus the pinned PX4 ULog sample.")


if __name__ == "__main__":
    main()
