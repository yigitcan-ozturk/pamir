import json
from math import isfinite
from pathlib import Path
from .model import Sample

# v0.1 keeps a focused topic set, but it must include the telemetry families
# needed to reconstruct actuator -> attitude -> motion failure chains.
DEFAULT_TOPICS = {
    "battery_status",
    "vehicle_gps_position",
    "vehicle_global_position",
    "vehicle_local_position",
    "vehicle_status",
    "vehicle_attitude",
    "vehicle_attitude_setpoint",
    "vehicle_angular_velocity",
    "vehicle_rates_setpoint",
    "actuator_outputs",
    "actuator_motors",
    "estimator_status",
    "estimator_innovations",
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
            topic = dataset.name if dataset.multi_id == 0 else f"{dataset.name}[{dataset.multi_id}]"
            signal = f"{topic}.{field}"
            for ts, value in zip(timestamps, values):
                try:
                    number = float(value)
                    if isfinite(number) and int(ts) >= 0:
                        out.append(Sample(int(ts), signal, number))
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
