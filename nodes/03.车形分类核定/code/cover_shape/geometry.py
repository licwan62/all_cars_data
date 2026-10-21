"""人工关键点回退；像素坐标 x 向后、y 向下。禁止外推缺失轮廓。"""
from __future__ import annotations

import bisect
import math

FEATURE_NAMES = ("hood_ratio", "roof_start_x", "roof_end_x", "roof_plateau_ratio", "rear_slope_index",
                 "rear_deck_ratio", "height_length_ratio", "wb_length_ratio")


def profile_features(payload: dict, gate: dict) -> dict:
    flags = []
    quality = payload.get("quality", {})
    for key in ("identity_confirmed", "full_vehicle", "unoccluded", "low_perspective", "stock_vehicle", "real_image"):
        if quality.get(key) is not True:
            flags.append("IMAGE_" + key.upper() + "_FAILED")
    annotation = payload.get("annotation", {})
    try:
        front, rear, ground = [float(annotation[k]) for k in ("front_x", "rear_x", "ground_y")]
        wheels = annotation["wheel_centers"]
        radii = [float(r) for r in annotation["wheel_radii"]]
        points = [(float(x), float(y)) for x, y in annotation["top_points"]]
        span = rear - front
        flat = [front, rear, ground, *radii, *[v for point in points for v in point],
                *[float(v) for point in wheels for v in point]]
        if not all(math.isfinite(v) for v in flat) or span <= 0 or len(wheels) != 2 or len(radii) != 2 or min(radii) <= 0:
            raise ValueError("关键点/轮半径无效")
        if len(points) < 3 or any(a[0] >= b[0] for a, b in zip(points, points[1:])):
            raise ValueError("轮廓关键点必须按 x 严格递增")
        if any(x < front or x > rear or y >= ground for x, y in points):
            raise ValueError("关键点超出车长/地面")
        if abs(float(wheels[0][1]) - float(wheels[1][1])) / span > gate["max_wheel_level_delta"]:
            flags.append("WHEEL_LEVEL_FAILED")
        if abs(radii[0] - radii[1]) / max(radii) > gate["max_wheel_radius_delta"]:
            flags.append("WHEEL_RADIUS_FAILED")
        for x, y in wheels:
            if not front < float(x) < rear or not float(y) < ground:
                raise ValueError("轮心超出车体")
        peak_y = min(y for _, y in points)
        height = ground - peak_y
        xs = [(x - front) / span for x, _ in points]
        ys = [(ground - y) / height for _, y in points]
        landmarks = [float(annotation[k]) for k in ("hood_end_x", "roof_start_x", "roof_end_x", "rear_deck_start_x")]
        if not front <= landmarks[0] <= landmarks[1] < landmarks[2] <= landmarks[3] <= rear:
            raise ValueError("车头/车顶/尾箱关键点顺序错误")
        normalized = [(x - front) / span for x in landmarks]
    except (KeyError, TypeError, ValueError, IndexError) as e:
        return {"usable": False, "flags": flags + ["INVALID_ANNOTATION"], "error": str(e), "top_profile_64": []}
    if flags:
        return {"usable": False, "flags": flags, "top_profile_64": []}
    missing = payload.get("missing_intervals", [])
    for interval in missing:
        if len(interval) != 2 or not 0 <= interval[0] < interval[1] <= 1:
            raise ValueError("轮廓缺失区间无效")

    def interpolate(x):
        if x < xs[0] or x > xs[-1] or any(a <= x <= b for a, b in missing):
            return None
        i = min(max(bisect.bisect_right(xs, x) - 1, 0), len(xs) - 2)
        return ys[i] + (ys[i + 1] - ys[i]) * (x - xs[i]) / (xs[i + 1] - xs[i])

    samples = [None if (v := interpolate(i / 63)) is None else round(v, 8) for i in range(64)]
    hood, roof_start, roof_end, deck = normalized
    roof_height, rear_height = interpolate(roof_end), interpolate(deck)
    features = {"hood_ratio": hood, "roof_start_x": roof_start, "roof_end_x": roof_end,
                "roof_plateau_ratio": roof_end - roof_start, "rear_deck_ratio": 1 - deck,
                "rear_slope_index": None if roof_height is None or rear_height is None or deck == roof_end else
                                    (roof_height - rear_height) / (deck - roof_end)}
    complete = all(v is not None for v in samples)
    return {"usable": complete, "flags": [] if complete else ["INCOMPLETE_PROFILE"],
            **{k: round(v, 8) if v is not None else None for k, v in features.items()},
            "top_profile_64": samples, "measurement_units": "relative_shape",
            "missing_intervals": missing, "image_quality": {"gate_passed": True, "checks": quality},
            "uncertainty": "人工关键点；无绝对毫米测量；质量阈值仅为试验配置"}


def annotation_svg(payload: dict) -> str:
    """仅绘制关键点/折线；不再分发来源照片。"""
    a = payload["annotation"]
    points = [(float(x), float(y)) for x, y in a["top_points"]]
    width = float(a["rear_x"]) - float(a["front_x"])
    top = min(y for _, y in points)
    height = float(a["ground_y"]) - top
    shift = lambda x, y: (x - float(a["front_x"]) + 10, y - top + 10)
    line = " ".join(f"{x:.3f},{y:.3f}" for x, y in [shift(x, y) for x, y in points])
    dots = "".join(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="3" fill="#d22"/>' for x, y in
                   [shift(float(x), float(y)) for x, y in a["wheel_centers"]])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width+20:.3f} {height+20:.3f}">'
            f'<polyline points="{line}" fill="none" stroke="#157" stroke-width="2"/>{dots}</svg>')
