"""Build field-level research tasks offline; never promote dimension evidence."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

NODE = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build_queue(rules, workflow, attempts):
    pending = {(r["make"], r["model"], r["year"]): r
               for r in rules["resolutions"] if r["status"] == "pending"}
    definitions = {}
    for task in workflow["tasks"]:
        key = task["make"], task["model"], task["year"]
        if key in definitions:
            raise ValueError(f"Duplicate research task: {key}")
        definitions[key] = task
    if set(definitions) != set(pending):
        raise ValueError("Research task inventory differs from current pending resolutions")
    allowed = set(workflow["blocker_definitions"])
    cached = {}
    for attempt in attempts["attempts"]:
        url = attempt["url"]
        if urlsplit(url).scheme != "https" or not urlsplit(url).netloc:
            raise ValueError("Invalid attempt URL")
        cached.setdefault(url, []).append(attempt)
    tasks = []
    for key, task in definitions.items():
        if not task["blockers"] or set(task["blockers"]) - allowed or not task["next_evidence"]:
            raise ValueError(f"Incomplete research gate: {key}")
        resolution = pending[key]
        sources = []
        for source in resolution.get("sources", []):
            observations = cached.get(source["url"], [])
            sources.append({
                "url": source["url"],
                "evidence_type": source.get("evidence_type", "unspecified"),
                "market": source.get("market", "unspecified"),
                "year": source.get("year"),
                "observations": observations,
                "retry_policy": "review_existing_observations_before_retry" if observations else "not_in_attempt_log",
            })
        tasks.append({**task, "task_id": f"{key[0]}|{key[1]}|{key[2]}",
                      "status": "pending", "reason": resolution["reason"], "sources": sources,
                      "acceptance": [workflow["blocker_definitions"][b] for b in task["blockers"]]})
    tasks.sort(key=lambda t: (t["priority"], t["make"], t["model"], t["year"]))
    groups = {}
    for task in tasks:
        group = groups.setdefault(task["research_group"], {"task_ids": [], "years": []})
        group["task_ids"].append(task["task_id"])
        group["years"].append(task["year"])
    return {"schema_version": 1, "tasks": tasks, "groups": groups,
            "pending_model_years": len(tasks), "source_attempts": len(attempts["attempts"]),
            "policy": workflow["policy"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=NODE / "work/us_research/queue.json")
    args = parser.parse_args()
    inputs = [NODE / "data/us" / name for name in
              ("year_gap_resolutions.json", "research_workflow.json", "source_attempts.json")]
    result = build_queue(*(read_json(p) for p in inputs))
    result["input_sha256"] = {p.relative_to(NODE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in inputs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pending_model_years": result["pending_model_years"],
                      "research_groups": len(result["groups"]), "source_attempts": result["source_attempts"],
                      "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
