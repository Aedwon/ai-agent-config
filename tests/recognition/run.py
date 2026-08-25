"""Opt-in provider recognition against fresh temporary projects."""

import argparse
import json
import os
import secrets
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from tooling.config.catalog import load_adapter
from tooling.config.paths import ConfigError
from tooling.config.render import render


INFRASTRUCTURE_PATTERNS = (
    "authentication",
    "not logged in",
    "login required",
    "unauthorized",
    "rate limit",
    "quota",
    "network",
    "connection",
    "timed out",
    "timeout",
    "unavailable",
    "not available",
)
AMBIGUITY_PATTERNS = (
    "ambiguous",
    "cannot determine",
    "not sure",
    "uncertain",
)


@dataclass(frozen=True)
class RecognitionResult:
    adapter: str
    status: str
    reason: str
    marker_value: str = ""
    positive_output: str = ""
    negative_output: str = ""
    staged_files: Tuple[str, ...] = ()
    command: Tuple[str, ...] = ()


def _find_pattern(text: str, patterns: Sequence[str]) -> Optional[str]:
    lowered = text.lower()
    return next((pattern for pattern in patterns if pattern in lowered), None)


def _resolve_executable(value: Optional[Path]) -> Optional[Path]:
    if value is None:
        return None
    raw = str(value)
    if "/" not in raw and "\\" not in raw:
        discovered = shutil.which(raw)
        return Path(discovered) if discovered else None
    candidate = Path(raw)
    if candidate.is_file() and os.access(str(candidate), os.X_OK):
        return candidate.resolve()
    return None


def _run(command: List[str], cwd: Path, timeout: int) -> Tuple[int, str]:
    environment = dict(os.environ)
    environment["NO_COLOR"] = "1"
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            env=environment,
            check=False,
            capture_output=True,
            encoding="utf-8",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        output = "{}\n{}".format(error.stdout or "", error.stderr or "").strip()
        return 124, "timeout\n{}".format(output).strip()
    output = "{}\n{}".format(completed.stdout, completed.stderr).strip()
    return completed.returncode, output


def _result(
    adapter_id: str,
    status: str,
    reason: str,
    marker: str = "",
    positive: str = "",
    negative: str = "",
    staged: Tuple[str, ...] = (),
    command: Tuple[str, ...] = (),
) -> RecognitionResult:
    return RecognitionResult(
        adapter=adapter_id,
        status=status,
        reason=reason,
        marker_value=marker,
        positive_output=positive,
        negative_output=negative,
        staged_files=staged,
        command=command,
    )


def probe(
    root: Path,
    adapter_id: str,
    executable: Optional[Path] = None,
    timeout: int = 90,
) -> RecognitionResult:
    """Run positive and negative recognition controls for one adapter."""

    source_root = Path(root).resolve(strict=True)
    adapter = load_adapter(source_root, adapter_id)
    recognition = adapter.recognition
    if recognition.get("mode") != "command":
        return _result(adapter_id, "UNPROVEN", "adapter requires manual recognition")

    configured = executable
    if configured is None:
        environment_value = os.environ.get(recognition["executable_env"])
        configured = Path(environment_value) if environment_value else None
    resolved_executable = _resolve_executable(configured)
    if resolved_executable is None:
        return _result(adapter_id, "UNPROVEN", "provider executable is unavailable")

    marker = secrets.token_hex(16)
    arguments = [str(value) for value in recognition["arguments"]]
    command = [str(resolved_executable), *arguments]
    with tempfile.TemporaryDirectory(prefix="ai-agent-config-recognition-") as directory:
        base = Path(directory)
        positive_project = base / "positive"
        negative_project = base / "negative"
        negative_project.mkdir()
        rendered = render(source_root, adapter_id, positive_project)[0]
        with rendered.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write("\n{}: {}\n".format(recognition["marker_label"], marker))
        staged = tuple(
            sorted(
                path.relative_to(positive_project).as_posix()
                for path in positive_project.rglob("*")
                if path.is_file()
            )
        )

        positive_code, positive_output = _run(command, positive_project, timeout)
        infrastructure = _find_pattern(positive_output, INFRASTRUCTURE_PATTERNS)
        if positive_code != 0:
            if infrastructure:
                return _result(
                    adapter_id,
                    "UNPROVEN",
                    "provider infrastructure or authentication failed: {}".format(infrastructure),
                    marker,
                    positive_output,
                    staged=staged,
                    command=tuple(command),
                )
            return _result(
                adapter_id,
                "FAIL",
                "positive probe command exited with status {}".format(positive_code),
                marker,
                positive_output,
                staged=staged,
                command=tuple(command),
            )
        if marker not in positive_output:
            ambiguity = _find_pattern(positive_output, AMBIGUITY_PATTERNS)
            if ambiguity:
                return _result(
                    adapter_id,
                    "UNPROVEN",
                    "positive probe output is ambiguous: {}".format(ambiguity),
                    marker,
                    positive_output,
                    staged=staged,
                    command=tuple(command),
                )
            return _result(
                adapter_id,
                "FAIL",
                "provider did not recognize the staged project instructions",
                marker,
                positive_output,
                staged=staged,
                command=tuple(command),
            )

        negative_code, negative_output = _run(command, negative_project, timeout)
        infrastructure = _find_pattern(negative_output, INFRASTRUCTURE_PATTERNS)
        if negative_code != 0:
            if infrastructure:
                return _result(
                    adapter_id,
                    "UNPROVEN",
                    "negative control infrastructure failed: {}".format(infrastructure),
                    marker,
                    positive_output,
                    negative_output,
                    staged,
                    tuple(command),
                )
            return _result(
                adapter_id,
                "FAIL",
                "negative control command exited with status {}".format(negative_code),
                marker,
                positive_output,
                negative_output,
                staged,
                tuple(command),
            )
        if marker in negative_output:
            return _result(
                adapter_id,
                "FAIL",
                "negative control produced the positive recognition marker",
                marker,
                positive_output,
                negative_output,
                staged,
                tuple(command),
            )
        if "UNRECOGNIZED" not in negative_output.upper():
            return _result(
                adapter_id,
                "UNPROVEN",
                "negative control output is ambiguous",
                marker,
                positive_output,
                negative_output,
                staged,
                tuple(command),
            )
    return _result(
        adapter_id,
        "PASS",
        "positive marker loaded and negative control remained unrelated",
        marker,
        positive_output,
        negative_output,
        staged,
        tuple(command),
    )


def main(arguments: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tests.recognition.run")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args(arguments)
    try:
        result = probe(args.root, args.adapter, args.executable, args.timeout)
    except (ConfigError, OSError, UnicodeError, ValueError) as error:
        result = RecognitionResult(args.adapter, "FAIL", str(error))
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return {"PASS": 0, "FAIL": 1, "UNPROVEN": 2}[result.status]


if __name__ == "__main__":
    raise SystemExit(main())
