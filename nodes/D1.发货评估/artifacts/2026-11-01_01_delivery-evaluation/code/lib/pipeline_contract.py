"""Shared node lifecycle policy. Containment never implies a data dependency."""
from pathlib import PurePosixPath


def publishable(node):
    return node.get("kind", "node") != "container" and node.get("lifecycle", "active") == "active"


def lifecycle_state(node):
    if node.get("kind") == "container":
        return "业务容器"
    return {"planned": "待接入", "legacy": "历史保留"}.get(node.get("lifecycle"))


def relative_file(value):
    p = PurePosixPath(value)
    return bool(value) and not p.is_absolute() and ".." not in p.parts and "\\" not in value and ":" not in value


def validate_contract(nodes):
    errors = []
    by_id = {n["id"]: n for n in nodes}
    for n in nodes:
        if n.get("kind", "node") not in {"node", "container"} or n.get("lifecycle", "active") not in {"active", "planned", "legacy"}:
            errors.append(f"{n['id']}: 无效节点类型或生命周期")
        parent = n.get("parent")
        if parent and (parent not in by_id or by_id[parent].get("kind") != "container" or not n["path"].startswith(by_id[parent]["path"] + "/nodes/")):
            errors.append(f"{n['id']}: parent 必须是实际包含本节点的业务容器")
        seen = {n["id"]}
        while parent in by_id:
            if parent in seen:
                errors.append(f"{n['id']}: 容器关系存在环")
                break
            seen.add(parent)
            parent = by_id[parent].get("parent")
        if n.get("kind") == "container" and (n.get("outputs") or n.get("run") or n.get("upstream")):
            errors.append(f"{n['id']}: 容器不得声明生产依赖、运行或交付")
        if "inputs" in n:
            declared = set(n.get("upstream", []))
            recorded = set()
            for item in n["inputs"]:
                upstream = item.get("node")
                recorded.add(upstream)
                if upstream not in declared or upstream not in by_id or not relative_file(item.get("file", "")):
                    errors.append(f"{n['id']}: 非法输入登记 {item}")
                elif publishable(n) and item.get("required", True) and item["file"] not in by_id[upstream].get("outputs", []):
                    errors.append(f"{n['id']}: 输入 {upstream}/{item['file']} 未登记为正式交付")
            if recorded != declared:
                errors.append(f"{n['id']}: inputs 必须覆盖声明的每条上游依赖")
    return errors
