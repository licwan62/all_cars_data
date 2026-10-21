"""CPU 背景分割、双轮检测及轮廓特征；不以车型/结构名称决定标签。"""
from __future__ import annotations

import hashlib
import io
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


class GeometryError(ValueError):
    pass


class Segmenter:
    def __init__(self, model_path: Path, expected_sha256: str):
        import onnxruntime as ort
        if hashlib.sha256(model_path.read_bytes()).hexdigest() != expected_sha256:
            raise GeometryError("SEGMENTATION_MODEL_HASH_MISMATCH")
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(str(model_path), sess_options=options, providers=["CPUExecutionProvider"])
        self.model_sha256 = expected_sha256

    def mask(self, rgb: np.ndarray) -> np.ndarray:
        image = Image.fromarray(rgb).resize((320, 320), Image.Resampling.LANCZOS)
        tensor = np.asarray(image, dtype=np.float32)
        tensor /= max(float(tensor.max()), 1e-6)
        tensor = (tensor - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array([0.229, 0.224, 0.225], dtype=np.float32)
        tensor = tensor.transpose(2, 0, 1)[None].astype(np.float32)
        prediction = self.session.run(None, {self.session.get_inputs()[0].name: tensor})[0][0, 0]
        span = float(prediction.max() - prediction.min())
        if span < 1e-6:
            raise GeometryError("EMPTY_SEGMENTATION")
        prediction = (prediction - prediction.min()) / span
        return cv2.resize(prediction, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_LINEAR)


def load_image(body: bytes, max_pixels=20_000_000) -> np.ndarray:
    try:
        with Image.open(io.BytesIO(body)) as image:
            if image.width * image.height > max_pixels or image.width < 200 or image.height < 100:
                raise GeometryError("IMAGE_SIZE_REJECTED")
            image = ImageOps.exif_transpose(image).convert("RGB")
            image.thumbnail((960, 960))
            return np.asarray(image)
    except (OSError, Image.DecompressionBombError) as e:
        raise GeometryError("IMAGE_DECODE_FAILED") from e


def wheel_pair(rgb: np.ndarray, bbox, policy: dict, component=None) -> tuple[list[list[float]], list[float], dict]:
    x, y, w, h = bbox
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 1)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=max(w * .04, 10),
                               param1=100, param2=policy["wheel_hough_threshold"],
                               minRadius=max(8, int(w * .035)), maxRadius=max(10, int(w * .105)))
    candidates = []
    if circles is not None:
        for cx, cy, r in circles[0]:
            if x + .07 * w < cx < x + .93 * w and y + .65 * h < cy < y + .95 * h:
                cx, cy, r = float(cx), float(cy), float(r)
                if component is not None:
                    if not component[round(cy), round(cx)]:
                        continue
                    bottom = np.flatnonzero(component[:, round(cx)])[-1]
                    r = float(bottom - cy)
                    if not .035 * w <= r <= .12 * w:
                        continue
                radius = max(4, round(r * .38))
                inner = gray[max(0, round(cy)-radius):round(cy)+radius+1,
                             max(0, round(cx)-radius):round(cx)+radius+1]
                if inner.size == 0 or np.mean(inner <= policy["wheel_dark_max"]) < policy["wheel_dark_fraction"]:
                    continue
                # 大椭圆的轴比限制；小轮毂装饰/车灯圆不能替代整个轮胎。
                patch_radius = round(r * 1.18)
                px, py = max(0, round(cx)-patch_radius), max(0, round(cy)-patch_radius)
                patch = gray[py:round(cy)+patch_radius+1, px:round(cx)+patch_radius+1]
                edges = cv2.Canny(patch, 45, 110)
                contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                ellipse_found = False
                for contour in contours:
                    if len(contour) < 20:
                        continue
                    (ex, ey), (ea, eb), _ = cv2.fitEllipse(contour)
                    if math.hypot(ex+px-cx, ey+py-cy) > r * .28 or max(ea, eb) < r * 1.3 or max(ea, eb) > r * 2.5:
                        continue
                    if min(ea, eb) / max(ea, eb) >= policy["min_wheel_ellipse_ratio"]:
                        ellipse_found = True
                        break
                if ellipse_found:
                    candidates.append((cx, cy, r))
    pairs = []
    for a in candidates:
        for b in candidates:
            if a[0] >= b[0]:
                continue
            spacing = (b[0] - a[0]) / w
            radius_delta = abs(a[2] - b[2]) / max(a[2], b[2])
            level_delta = abs(a[1] - b[1]) / w
            if policy["min_wheelbase_image_ratio"] <= spacing <= policy["max_wheelbase_image_ratio"] and radius_delta <= policy["max_wheel_radius_delta"] and level_delta <= policy["max_wheel_level_delta"]:
                score = radius_delta * 3 + level_delta * 10 + abs(spacing - .62)
                pairs.append((score, a, b))
    if not pairs:
        raise GeometryError("NO_VALID_SIDE_WHEEL_PAIR")
    _, a, b = min(pairs)
    diagnostics = {"wheel_level_delta": abs(a[1] - b[1]) / w,
                   "wheel_radius_delta": abs(a[2] - b[2]) / max(a[2], b[2]),
                   "wb_image_ratio": (b[0] - a[0]) / w, "circle_candidates": len(candidates)}
    return [[a[0], a[1]], [b[0], b[1]]], [a[2], b[2]], diagnostics


def analyze_mask(rgb: np.ndarray, probability: np.ndarray, policy: dict, wheels=None) -> tuple[dict, bytes]:
    mask = (probability >= policy["mask_threshold"]).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if count <= 1:
        raise GeometryError("EMPTY_SEGMENTATION")
    i = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    x, y, w, h, area = [int(v) for v in stats[i]]
    component = (labels == i).astype(np.uint8)
    if w / h < policy["min_side_aspect_ratio"] or area / (w * h) < policy["min_mask_fill"]:
        raise GeometryError("NON_SIDE_OR_FRAGMENTED_SEGMENTATION")
    if x <= 1 or y <= 1 or x + w >= rgb.shape[1] - 1 or y + h >= rgb.shape[0] - 1:
        raise GeometryError("VEHICLE_CLIPPED")
    if wheels is None:
        centers, radii, diagnostics = wheel_pair(rgb, (x, y, w, h), policy, component)
    else:
        centers, radii = wheels
        diagnostics = {"test_fixture_wheels": True}
    ground = float(np.median([p[1] + r for p, r in zip(centers, radii)]))
    if not y + .7 * h <= ground <= y + 1.15 * h:
        raise GeometryError("GROUND_BASELINE_INCONSISTENT")
    raw = np.array([np.flatnonzero(component[:, column])[0] if component[:, column].any() else np.nan
                    for column in range(x, x + w)], dtype=float)
    if np.isnan(raw).any():
        raise GeometryError("PROFILE_GAPS")
    # 小尺度开运算抑制镜子/天线；不填补大缺失、不把不同来源做均值。
    smooth = cv2.medianBlur(raw.astype(np.float32).reshape(1, -1), 5).ravel().astype(float)
    roof_level = np.percentile(smooth[int(.15 * w):int(.85 * w)], 5)
    normalized = (ground - smooth) / max(ground - roof_level, 1)
    high = np.flatnonzero(normalized >= policy["roof_band_height"])
    if len(high) < .12 * w:
        raise GeometryError("ROOF_TOO_SMALL")
    start, end = int(high[0]), int(high[-1])
    # 车头方向的可审计启发式；仅推断，不伪装为视觉身份验证。
    flipped = (start + end) / 2 < (w - 1) / 2
    if flipped:
        normalized = normalized[::-1].copy()
        smooth = smooth[::-1].copy()
        centers = [[x + w - 1 - (p[0] - x), p[1]] for p in centers[::-1]]
        start, end = w - 1 - end, w - 1 - start
    # 尾部下降到 70% 高度后，检查是否形成独立水平尾箱台阶。
    rear_indexes = np.arange(end, w)
    drops = rear_indexes[normalized[rear_indexes] <= policy["deck_height"]]
    deck_start = int(drops[0]) if len(drops) else w - 1
    derivative = np.gradient(normalized)
    flat_tail = np.abs(derivative[deck_start:]) * (w - 1) <= policy["flat_slope_max"]
    deck_fraction = float(flat_tail.mean()) if len(flat_tail) else 0
    rear_deck_ratio = (w - 1 - deck_start) / (w - 1) if deck_fraction >= .55 else 0.0
    samples = np.interp(np.linspace(0, w - 1, 64), np.arange(w), normalized)
    feature = {"usable": True, "feature_version": "auto-segmentation-v1", "measurement_units": "relative_shape",
               "top_profile_64": [round(float(v), 8) for v in samples],
               "roof_start_x": start / (w - 1), "roof_end_x": end / (w - 1),
               "roof_plateau_ratio": (end - start) / (w - 1), "rear_deck_ratio": rear_deck_ratio,
               "rear_drop_run": (deck_start - end) / (w - 1),
               "rear_slope_index": float((normalized[end] - normalized[deck_start]) / max((deck_start-end)/(w-1), .01)),
               "hood_ratio": None, "height_length_ratio": None, "wb_length_ratio": None,
               "image_quality": {"geometry_gate_passed": True, **diagnostics, "bbox": [x, y, w, h],
                                 "mask_fill": area / (w * h), "orientation_method": "roof_position_heuristic",
                                 "flipped": flipped, "stock_vehicle_confirmed": False, "identity_confirmed": False},
               "uncertainty": "自动背景分割/轮心/方向/试验阈值；相对几何，不是毫米量测或正确概率"}
    canvas = rgb.copy()
    contour, _ = cv2.findContours(component, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(canvas, contour, -1, (0, 220, 80), 2)
    for center, radius in zip(centers, radii):
        # 叠加保持原图坐标，翻转前轮心用其逆变换还原。
        cx = x + w - 1 - (center[0] - x) if flipped else center[0]
        cv2.circle(canvas, (round(cx), round(center[1])), round(radius), (255, 60, 30), 2)
    buffer = io.BytesIO()
    Image.fromarray(canvas).save(buffer, format="PNG")
    return feature, buffer.getvalue()


def analyze_image(body: bytes, segmenter: Segmenter, policy: dict) -> tuple[dict, bytes]:
    rgb = load_image(body)
    return analyze_mask(rgb, segmenter.mask(rgb), policy)


def candidate_from_features(features: dict, dimensions: dict, policy: dict) -> dict:
    """几何试验规则只读取测量特征/实际尺寸；不读取品牌、车型、BODY_TYPE。"""
    length, height = dimensions.get("length_mm"), dimensions.get("height_mm")
    if not features.get("usable") or not length or not height or not math.isfinite(length) or not math.isfinite(height):
        return {"label": "UNKNOWN", "alternates": [], "rule": "MISSING_GEOMETRY_OR_DIMENSIONS"}
    ratio = height / length
    roof_end, plateau = features["roof_end_x"], features["roof_plateau_ratio"]
    deck, run = features["rear_deck_ratio"], features["rear_drop_run"]
    low = height <= policy["low_height_mm"] and ratio <= policy["low_height_length_ratio"]
    if roof_end >= policy["box_roof_end_x"] and plateau >= policy["box_roof_plateau"]:
        if ratio >= policy["tall_height_length_ratio"]:
            return {"label": "TALL_BOX" if length <= policy["compact_length_mm"] else "BOXY_SUV", "alternates": [], "rule": "LONG_HIGH_ROOF_UPRIGHT_REAR"}
        return {"label": "WAGON", "alternates": ["BOXY_SUV"] if height >= policy["crossover_height_mm"] else [], "rule": "EXTENDED_ROOF_WITH_LOW_PROPORTIONS"}
    if deck >= policy["notchback_deck_ratio"]:
        return {"label": "LOW_NOTCHBACK" if low else "STANDARD_SEDAN", "alternates": [], "rule": "DISTINCT_REAR_DECK_STEP"}
    if run >= policy["sloped_rear_run"] or roof_end < policy["sloped_roof_end_x"]:
        if low:
            return {"label": "LOW_FASTBACK", "alternates": [], "rule": "LOW_BODY_CONTINUOUS_REAR_SLOPE"}
        if height >= policy["crossover_height_mm"]:
            return {"label": "SLOPED_CROSSOVER", "alternates": ["SPORT_LIFTBACK"] if height < policy["crossover_height_mm"] + 80 else [], "rule": "TALL_BODY_SLOPED_REAR"}
        if length <= policy["compact_length_mm"] and ratio >= policy["compact_height_length_ratio"]:
            return {"label": "COMPACT_HATCH", "alternates": [], "rule": "SHORT_BODY_HIGH_CABIN_SHORT_REAR"}
        return {"label": "SPORT_LIFTBACK", "alternates": [], "rule": "LOW_CABIN_SLOPED_REAR_WITHOUT_DECK"}
    return {"label": "UNKNOWN", "alternates": [], "rule": "NO_UNAMBIGUOUS_GEOMETRIC_RULE"}
