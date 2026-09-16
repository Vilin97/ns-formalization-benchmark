#!/usr/bin/env python3
"""Run `lake env lean --profile` sequentially on every Lean file in a directory."""
import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
import re
import subprocess
import sys
import time


NUMBER = r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
DURATION = rf"({NUMBER})\s*(ns|us|µs|μs|ms|s)"
SCALE = {"ns": 1e-9, "us": 1e-6, "µs": 1e-6, "μs": 1e-6, "ms": 1e-3, "s": 1}
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def parse_profile(text):
    """Keep cumulative phases separate from individual, potentially nested events."""
    phases, events = {}, []
    cumulative = False
    for line in ANSI.sub("", text).splitlines():
        if line.strip() == "cumulative profiling times:":
            cumulative = True
            continue
        if cumulative:
            match = re.fullmatch(rf"\s+(.+?)\s+{DURATION}\s*", line)
            if match:
                phases[match[1]] = float(match[2]) * SCALE[match[3]]
                continue
            if line.strip():
                cumulative = False
        match = re.fullmatch(rf"\s*(.+?) took {DURATION}\s*", line)
        if match:
            events.append({"event": match[1], "seconds": float(match[2]) * SCALE[match[3]]})
    return phases, events


def find_project(path):
    directory = path if path.is_dir() else path.parent
    for parent in (directory, *directory.parents):
        if any((parent / f).is_file() for f in ("lakefile.toml", "lakefile.lean")):
            return parent
    return None


def discover(path, recursive=True):
    if path.is_file():
        return [path] if path.suffix == ".lean" else []
    files = path.rglob("*.lean") if recursive else path.glob("*.lean")
    return sorted(p for p in files if p.is_file()
                  and not {".lake", ".git"}.intersection(p.relative_to(path).parts))


def write_reports(output, rows):
    ordered = sorted(rows, key=lambda row: row["wall_seconds"], reverse=True)
    phase_names = sorted({name for row in rows for name in row["phases"]})
    with (output / "summary.csv").open("w", newline="") as stream:
        fields = ["file", "wall_seconds", "exit_code", "timed_out", "log"]
        writer = csv.DictWriter(stream, fieldnames=fields + [f"{name}_seconds" for name in phase_names], lineterminator="\n")
        writer.writeheader()
        for row in ordered:
            writer.writerow({**{name: row[name] for name in fields},
                             **{f"{name}_seconds": value for name, value in row["phases"].items()}})
    with (output / "events.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["file", "event", "seconds"], lineterminator="\n")
        writer.writeheader()
        for row in ordered:
            for event in row["events"]:
                writer.writerow({"file": row["file"], **event})
    (output / "results.json").write_text(json.dumps(ordered, indent=2) + "\n")
    lines = ["# Lean directory profile", "",
             "Times in seconds; sorted by wall time, slowest first. Files run sequentially.",
             "Wall time includes Lake startup. Phase times can overlap; do not sum them.",
             "A dash means Lean did not report that phase. Full phase data is in `summary.csv`.", "",
             "| File | Wall | Import | Elaboration | Type checking | Tactics | Status |",
             "|---|---:|---:|---:|---:|---:|---|"]
    for row in ordered:
        cells = [f"{row['phases'][name]:.3f}" if name in row["phases"] else "—"
                 for name in ("import", "elaboration", "type checking", "tactic execution")]
        status = "timeout" if row["timed_out"] else ("ok" if row["exit_code"] == 0 else f"exit {row['exit_code']}")
        filename = row["file"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {filename} | {row['wall_seconds']:.3f} | {' | '.join(cells)} | {status} |")
    lines += ["", f"Files completed: {len(rows)}. Sum of per-file wall times: {sum(r['wall_seconds'] for r in rows):.3f} s.",
              "This profiles existing source files using already-built imports; it does not rebuild dependencies.", ""]
    report = "\n".join(lines)
    (output / "REPORT.md").write_text(report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory (recursive by default), or a single .lean file")
    parser.add_argument("--project", type=Path, help="Lake project root; inferred from the input's nearest lakefile by default")
    parser.add_argument("--output", type=Path, help="New output directory; default: profile-results/<timestamp> in the current directory")
    parser.add_argument("--no-recursive", action="store_true", help="Only profile files directly inside the directory")
    parser.add_argument("--timeout", type=float, help="Optional timeout in seconds per file; continue to the next file on timeout")
    args = parser.parse_args()
    source = args.directory.expanduser().resolve()
    if not source.exists():
        parser.error(f"Input does not exist: {source}")
    if args.timeout is not None and args.timeout <= 0:
        parser.error("--timeout must be positive")
    project = args.project.expanduser().resolve() if args.project else find_project(source)
    if project is None or not any((project / f).is_file() for f in ("lakefile.toml", "lakefile.lean")):
        parser.error("No Lake project found; supply --project /path/to/project")
    if not source.is_relative_to(project):
        parser.error("Input must be inside the selected Lake project")
    files = discover(source, not args.no_recursive)
    if not files:
        parser.error("No .lean files found")
    output = (args.output or Path("profile-results") / datetime.now().strftime("%Y%m%d-%H%M%S-%f")).expanduser().resolve()
    try:
        output.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        parser.error(f"Output directory already exists: {output}; choose a new directory")
    metadata = {"project": str(project), "input": str(source),
                "started_at": datetime.now().astimezone().isoformat(),
                "files": [str(p.relative_to(project)) for p in files],
                "command_template": ["lake", "env", "lean", "--profile", "<file>"],
                "recursive": not args.no_recursive, "timeout_seconds": args.timeout}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    rows = []
    try:
        for index, file in enumerate(files, 1):
            relative = file.relative_to(project)
            log_path = Path("logs") / relative.with_suffix(".log")
            (output / log_path).parent.mkdir(parents=True, exist_ok=True)
            command = ["lake", "env", "lean", "--profile", str(relative)]
            print(f"[{index}/{len(files)}] {relative}", file=sys.stderr, flush=True)
            started = time.perf_counter()
            timed_out = False
            with (output / log_path).open("w") as log:
                try:
                    completed = subprocess.run(command, cwd=project, stdout=log,
                                               stderr=subprocess.STDOUT, timeout=args.timeout)
                    exit_code = completed.returncode
                except subprocess.TimeoutExpired:
                    timed_out, exit_code = True, None
                except OSError as error:
                    print(error, file=log)
                    exit_code = 127
            elapsed = time.perf_counter() - started
            phases, events = parse_profile((output / log_path).read_text(errors="replace"))
            rows.append({"file": str(relative), "wall_seconds": elapsed, "exit_code": exit_code,
                         "timed_out": timed_out, "command": command, "log": str(log_path),
                         "phases": phases, "events": events})
            write_reports(output, rows)
    except KeyboardInterrupt:
        write_reports(output, rows)
        print(f"\nInterrupted; completed results saved in {output}", file=sys.stderr)
        return 130
    print(write_reports(output, rows))
    print(f"Reports and raw logs: {output}", file=sys.stderr)
    return int(any(row["exit_code"] != 0 for row in rows))


if __name__ == "__main__":
    raise SystemExit(main())
