"""节点运行批次：一次运行一个不可变批次，每份字节只存一次。

用法（节点代码）::

    batch = RunBatch.create(PROJECT_DIR / "artifacts", "dimension-statistics", data_dir=PROJECT_DIR / "data")
    table = batch.input(A0_OUTPUT / "US/全量/全量表.csv")       # 上游已发布且 sha 一致：只记引用
    write_csv(frame, batch.output("尺码宽高统计.csv"))           # → output/尺码宽高统计-YYYYMMDD_NN.csv
    write_csv(atoms, batch.extra("原子事实表_US.csv"))           # → extra/原子事实表_US.csv.gz（大中间表压缩）
    batch.finish({"status": "passed", ...}, publish_to=PROJECT_DIR / "output")

批次目录::

    artifacts/YYYY-MM-DD_NN_<描述>/
      run.json        # 输入引用、规则快照（sha256 + git commit）、输出 sha256、状态
      output/<名称>-YYYYMMDD_NN.<ext>
      extra/          # 中间表（.gz）、问题清单
      input/          # 仅限无法引用的输入（上游未发布或已改动、仓库外文件）
      rules/          # 仅限与 git HEAD 不一致的规则文件（未提交的修改、未跟踪文件）

- **输入**：文件位于某节点 ``output/`` 且与该节点 ``output/manifest.json`` 登记的 sha256 一致时，只记录
  (节点, 版本, 文件, artifact_file, sha256)，字节在上游批次里；否则复制进 ``input/`` 并写明原因，保证可追溯。
- **规则**：``data/`` 全量 sha256 快照（CRLF→LF 归一）+ git commit；已提交的文件凭 ``git show <commit>:<路径>``
  取回，只有未提交的才复制。
- **输出**：``finish`` 写 ``run.json`` 后原子更新节点 ``output/``；``scripts/publish_release.py`` 发布时
  发现 ``output/`` 与 ``run.json`` 登记的输出 sha256 相同，直接引用本批次文件，不再复制。
- 编号以创建目录占位（并发运行不会撞号）；失败时 ``run.json`` 记 ``failed``，不改 ``output/``。
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

from rules_snapshot import rules_snapshot

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_RECORD = "run.json"
MANIFEST = "manifest.json"


class BatchError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def versioned_name(file_name: str, version: str) -> str:
    path = Path(file_name)
    return path.with_name(f"{path.stem}-{version}{path.suffix}").as_posix()


def repo_path(path: Path) -> str:
    """仓库内路径记为相对仓库根的 posix 路径，仓库外保留绝对路径。"""
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _row_count(path: Path) -> int | None:
    suffixes = [suffix.lower() for suffix in path.suffixes]
    if not suffixes or suffixes[-1] not in {".csv", ".tsv"}:
        return None
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return max(sum(1 for _ in csv.reader(handle, delimiter="\t" if suffixes[-1] == ".tsv" else ",")) - 1, 0)


def published_reference(path: Path, digest: str) -> tuple[dict | None, str]:
    """path 是某节点 output/ 下已发布且内容一致的交付物时返回引用，否则 (None, 原因)。"""
    resolved = path.resolve()
    for output_dir in resolved.parents:
        manifest_path = output_dir / MANIFEST
        if output_dir.name != "output" or not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        name = resolved.relative_to(output_dir).as_posix()
        item = next((entry for entry in manifest.get("deliverables", []) if entry["file"] == name), None)
        if item is None:
            return None, f"{repo_path(output_dir)}/manifest.json 未登记 {name}"
        if item["sha256"] != digest:
            return None, f"{repo_path(path)} 与其 manifest 版本 {manifest.get('version')} 不一致（上游改动后未发布）"
        return {
            "node": manifest.get("node"),
            "path": manifest.get("path"),
            "version": manifest.get("version"),
            "file": name,
            "versioned_file": item.get("versioned_file"),
            "artifact_file": item.get("artifact_file"),
            "sha256": digest,
        }, ""
    return None, "不在任何已发布节点的 output/ 中"


def git_state(data_dir: Path) -> tuple[str | None, list[Path]]:
    """返回 (HEAD commit, data_dir 下与 HEAD 不一致或未跟踪的文件)；不在 git 仓库内时 commit 为 None。"""
    if not data_dir.is_dir():
        return None, []
    try:
        commit = subprocess.run(["git", "-C", str(data_dir), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        top = Path(subprocess.run(["git", "-C", str(data_dir), "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
        status = subprocess.run(
            ["git", "-C", str(data_dir), "-c", "core.quotepath=false", "status", "--porcelain", "-z", "--untracked-files=all", "--", "."],
            capture_output=True, text=True, encoding="utf-8", check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None, []
    dirty = []
    entries = [entry for entry in status.split("\0") if entry]
    index = 0
    while index < len(entries):
        entry = entries[index]
        code, name = entry[:2], entry[3:]
        if code[0] in "RC":  # 重命名/复制后面跟着原路径
            index += 1
        if "D" not in code:
            dirty.append((top / name).resolve())
        index += 1
    return commit, dirty


class RunBatch:
    def __init__(self, directory: Path, version: str, description: str, data_dir: Path | None):
        self.directory = directory
        self.version = version
        self.description = description
        self.data_dir = data_dir
        self.created_at = datetime.now().astimezone().isoformat(timespec="seconds")
        self.inputs: list[dict] = []
        self.outputs: dict[str, Path] = {}
        self.extras: list[Path] = []
        self.finished = False

    @classmethod
    def create(cls, artifacts_dir: Path, description: str, data_dir: Path | None = None, day: date | None = None) -> "RunBatch":
        """以 mkdir 占位分配 ``YYYY-MM-DD_NN_<描述>``，与同目录下任何批次（含发布批次）不撞号。"""
        day_text = (day or date.today()).isoformat()
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        pattern = re.compile(rf"^\.?{re.escape(day_text)}_(\d{{2}})_")
        while True:
            used = [int(match.group(1)) for path in artifacts_dir.iterdir() if (match := pattern.match(path.name))]
            number = max(used, default=0) + 1
            if number > 99:
                raise BatchError(f"{artifacts_dir} 当天批次已用尽")
            directory = artifacts_dir / f"{day_text}_{number:02d}_{description}"
            try:
                directory.mkdir()
            except FileExistsError:
                continue
            return cls(directory, f"{day_text.replace('-', '')}_{number:02d}", description, data_dir)

    # ---- 输入 ---------------------------------------------------------------------------------
    def input(self, path: Path, name: str | None = None) -> Path:
        """登记一个输入文件并原样返回 path。已发布的上游交付物只记引用，其余复制进 input/<name>。"""
        path = Path(path)
        if not path.is_file():
            raise BatchError(f"找不到输入文件：{path}")
        digest = sha256(path)
        reference, reason = published_reference(path, digest)
        if reference:
            self.inputs.append(reference)
            return path
        target_name = name or self._default_input_name(path)
        target = self.directory / "input" / target_name
        if target.exists():
            raise BatchError(f"输入快照重名：input/{target_name}，请传入 name")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        self.inputs.append({
            "file": repo_path(path),
            "artifact_file": repo_path(target),
            "sha256": digest,
            "copied_because": reason,
        })
        return path

    @staticmethod
    def _default_input_name(path: Path) -> str:
        parts = path.resolve().parts
        if "output" in parts:
            return Path(*parts[len(parts) - parts[::-1].index("output"):]).as_posix()
        return path.name

    # ---- 输出 ---------------------------------------------------------------------------------
    def output(self, name: str) -> Path:
        """交付物在本批次中的写入路径（带版本后缀）；finish 时发布到节点 output/<name>。"""
        if name in self.outputs:
            raise BatchError(f"交付物重复登记：{name}")
        target = self.directory / "output" / versioned_name(name, self.version)
        target.parent.mkdir(parents=True, exist_ok=True)
        self.outputs[name] = target
        return target

    def extra(self, name: str, compress: bool = True) -> Path:
        """中间表/报告的写入路径；compress 时 .csv/.tsv/.json 加 .gz（pandas 按扩展名自动压缩）。"""
        relative = Path(name)
        if compress and relative.suffix.lower() in {".csv", ".tsv", ".json"}:
            relative = relative.with_name(relative.name + ".gz")
        target = self.directory / "extra" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        self.extras.append(target)
        return target

    # ---- 完成 ---------------------------------------------------------------------------------
    def _rules(self) -> dict:
        if self.data_dir is None or not self.data_dir.is_dir():
            return {"data_dir": None, "files": []}
        if self.data_dir.name != "data":
            raise BatchError(f"规则目录必须是节点 data/：{self.data_dir}")
        commit, dirty = git_state(self.data_dir)
        files = rules_snapshot(self.data_dir.parent)
        copied = []
        dirty_set = set(dirty)
        for item in files:
            source = (self.data_dir.parent / item["file"]).resolve()
            if commit is None or source in dirty_set:
                target = self.directory / "rules" / item["file"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                item["artifact_file"] = repo_path(target)
                copied.append(item["file"])
        return {"data_dir": repo_path(self.data_dir), "git_commit": commit, "copied": copied, "files": files}

    def _record(self, status: dict) -> dict:
        outputs = []
        for name, path in self.outputs.items():
            if not path.is_file():
                raise BatchError(f"交付物未写出：{name}")
            outputs.append({
                "file": name,
                "versioned_file": versioned_name(name, self.version),
                "artifact_file": repo_path(path),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "rows": _row_count(path),
            })
        return {
            "schema_version": 1,
            "batch": repo_path(self.directory),
            "version": self.version,
            "description": self.description,
            "created_at": self.created_at,
            "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "command": [Path(sys.argv[0]).name, *sys.argv[1:]] if sys.argv and sys.argv[0] else [],
            "inputs": self.inputs,
            "rules": self._rules(),
            "outputs": outputs,
            "extras": [repo_path(path) for path in self.extras if path.is_file()],
            "status": status,
        }

    def _write_record(self, record: dict) -> None:
        temporary = self.directory / f".{RUN_RECORD}.tmp"
        temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, self.directory / RUN_RECORD)

    def finish(self, status: dict | None = None, publish_to: Path | None = None) -> dict:
        """写 run.json（状态 passed），再把交付物原子发布到 publish_to/<name>。"""
        if self.finished:
            raise BatchError("批次已完成")
        record = self._record({"status": "passed", **(status or {})})
        self._write_record(record)
        self.finished = True
        if publish_to is not None:
            for name, path in self.outputs.items():
                destination = publish_to / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                temporary = destination.with_name(f".{destination.name}.tmp")
                shutil.copy2(path, temporary)
                os.replace(temporary, destination)
        return record

    def fail(self, error: BaseException | str) -> None:
        """记录失败（不发布）；批次保留以便排查。"""
        if self.finished:
            return
        record = {
            "schema_version": 1,
            "batch": repo_path(self.directory),
            "version": self.version,
            "description": self.description,
            "created_at": self.created_at,
            "inputs": self.inputs,
            "status": {"status": "failed", "error": f"{type(error).__name__}: {error}" if isinstance(error, BaseException) else str(error)},
        }
        self._write_record(record)
        self.finished = True

    def __enter__(self) -> "RunBatch":
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        if exc is not None:
            self.fail(exc)
        elif not self.finished:
            self.fail("运行结束但未调用 finish")
        return False
