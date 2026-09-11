import json
from pathlib import Path
from .model import Sample

DEFAULT_TOPICS = {
    "battery_status",
    "vehicle_gps_position",
    "vehicle_status",
    "estimator_status",
    "sensor_combined",
}


def load_json(path: str | Path) -> list[Sample]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload["samples"] if isinstance(payload, dict) else payload
    return [Sample(int(r["timestamp_us"]), str(r["signal"]), float(r["value"])) for r in rows]


def load_ulog(path: str | Path) -> list[Sample]:
    try:
        from pyulog import ULog
    except ImportError as exc:
        raise RuntimeError("ULog support requires pyulog. Install with: pip install pyulog==1.2.4") from exc

    ulog = ULog(str(path))
    out: list[Sample] = []
    for dataset in ulog.data_list:
        if dataset.name not in DEFAULT_TOPICS:
            continue
        timestamps = dataset.data.get("timestamp")
        if timestamps is None:
            continue
        for field, values in dataset.data.items():
            if field == "timestamp":
                continue
            try:
                if len(values) != len(timestamps):
                    continue
            except TypeError:
                continue
            signal = f"{dataset.name}.{field}"
            for ts, value in zip(timestamps, values):
                try:
                    out.append(Sample(int(ts), signal, float(value)))
                except (TypeError, ValueError):
                    continue
    return out


def load(path: str | Path) -> list[Sample]:
    suffix = Path(path).suffix.lower()
    if suffix == ".ulg":
        return load_ulog(path)
    if suffix == ".json":
        return load_json(path)
    raise ValueError("Supported inputs: .ulg, .json")
