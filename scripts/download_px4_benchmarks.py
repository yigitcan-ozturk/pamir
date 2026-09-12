#!/usr/bin/env python3
import io
import json
import zipfile
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
LEGACY_MANIFEST = ROOT / "benchmarks" / "px4_public_incidents.json"
REPRO_MANIFEST = ROOT / "benchmarks" / "px4_reproducible_incidents.json"
OUT = ROOT / "benchmarks" / "data"

PYULOG_SAMPLE = (
    "https://raw.githubusercontent.com/PX4/pyulog/"
    "ffbe3755d903e93797a89fb4fce26e0c0420a42f/test/sample.ulg"
)
PYULOG_SAMPLE_SHA256 = "81952e6059bc095717e7911c010e07f85749d6b04d332a5ffc51575a3fd0a558"

# Backward-compatible pins are intentionally retained here as a defense-in-depth
# layer for callers/tests that validate a known benchmark by label alone. Manifest
# pins remain authoritative for the expanded reproducible corpus.
PINNED_SHA256 = {
    "github-indoor-crash-2025": "7ea3869991912d9f2e264b53bebf3afc30e8b6595fd9837d76cf8e24cc7b0179",
    "github-indoor-control-2025": "6288e117e86b4e4365f833e55137b5285db12a7f1339063783f7ce76971f26e5",
    "px4-pyulog-sample": PYULOG_SAMPLE_SHA256,
}


def download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 PAMIR-v0.1-benchmark"})
    with urlopen(request, timeout=90) as response:
        return response.read()


def validate_ulog(data: bytes, label: str, expected_sha256: str | None = None) -> bytes:
    if len(data) < 16 or not data.startswith(b"ULog\x01\x12\x35"):
        raise RuntimeError(f"{label}: response is not a ULog file")
    digest = sha256(data).hexdigest()
    expected = expected_sha256 or PINNED_SHA256.get(label)
    if expected and digest != expected:
        raise RuntimeError(f"{label}: SHA-256 mismatch: expected {expected}, got {digest}")
    return data


def extract_ulog(payload: bytes, case: dict) -> bytes:
    transport = case.get("transport", "raw")
    if transport == "raw":
        return payload
    if transport != "zip":
        raise RuntimeError(f"{case['id']}: unsupported transport {transport!r}")

    try:
        archive = zipfile.ZipFile(io.BytesIO(payload))
    except zipfile.BadZipFile as exc:
        raise RuntimeError(f"{case['id']}: response is not a valid ZIP archive") from exc

    configured = case.get("archive_member")
    if configured:
        candidates = [configured]
    else:
        candidates = [
            name for name in archive.namelist()
            if not name.endswith("/") and name.lower().endswith((".ulg", ".ulg.txt"))
        ]
    if len(candidates) != 1:
        raise RuntimeError(
            f"{case['id']}: expected exactly one ULog in ZIP, found {len(candidates)}: {candidates}"
        )
    try:
        return archive.read(candidates[0])
    except KeyError as exc:
        raise RuntimeError(f"{case['id']}: ZIP member not found: {candidates[0]}") from exc


def store_required_case(case: dict) -> None:
    destination = OUT / f"{case['id']}.ulg"
    expected_sha = case.get("sha256")
    if destination.exists() and destination.stat().st_size > 0:
        data = validate_ulog(destination.read_bytes(), case["id"], expected_sha)
        print(f"skip {destination.name} (verified sha256={sha256(data).hexdigest()})")
        return

    print(f"download required {case['kind']} {case['id']}")
    payload = download(case["download_url"])
    data = extract_ulog(payload, case)
    validate_ulog(data, case["id"], expected_sha)
    destination.write_bytes(data)
    print(
        f"  -> {destination} ({len(data)} bytes, sha256={sha256(data).hexdigest()})"
    )


def download_legacy_flight_review() -> list[str]:
    payload = json.loads(LEGACY_MANIFEST.read_text(encoding="utf-8"))
    blocked = []
    for case in payload["cases"]:
        destination = OUT / f"{case['id']}.ulg"
        if destination.exists() and destination.stat().st_size > 0:
            validate_ulog(destination.read_bytes(), case["id"])
            print(f"skip optional {destination.name} (already verified)")
            continue
        print(f"download optional Flight Review {case['id']}")
        try:
            data = validate_ulog(download(case["download_url"]), case["id"])
        except (HTTPError, URLError) as exc:
            blocked.append(case["id"])
            print(f"  optional source unavailable: {exc}")
            continue
        destination.write_bytes(data)
        print(f"  -> {destination} ({len(data)} bytes, sha256={sha256(data).hexdigest()})")
    return blocked


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    reproducible = json.loads(REPRO_MANIFEST.read_text(encoding="utf-8"))

    for case in reproducible["cases"]:
        store_required_case(case)

    fallback = OUT / "px4-pyulog-sample.ulg"
    if not fallback.exists() or fallback.stat().st_size == 0:
        print("download pinned PX4/pyulog parser sample")
        data = validate_ulog(download(PYULOG_SAMPLE), "px4-pyulog-sample", PYULOG_SAMPLE_SHA256)
        fallback.write_bytes(data)
    data = validate_ulog(fallback.read_bytes(), "px4-pyulog-sample", PYULOG_SAMPLE_SHA256)
    print(f"verified px4-pyulog-sample sha256={sha256(data).hexdigest()}")

    blocked = download_legacy_flight_review()
    if blocked:
        print("OPTIONAL Flight Review corpus unavailable from runner: " + ", ".join(blocked))


if __name__ == "__main__":
    main()
