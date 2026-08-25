"""Repository validation for portable policy, adapters, and provenance."""

import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

from tooling.config.catalog import load_json_file
from tooling.config.paths import ConfigError, resolve_beneath, safe_relative_path


REQUIRED_FILES = (
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "core/agent-contract.md",
    "core/precedence.md",
    "skills/catalog.yaml",
    "adapters/catalog.schema.json",
    "docs/migration-map.json",
    "examples/level-1-minimal/example.json",
    "tests/fixtures/authorization-cases.json",
)
REQUIRED_ADAPTERS = {"generic", "codex", "claude", "gemini", "antigravity"}
CORE_FORBIDDEN_TERMS = (
    "Aedwon",
    "ChatGPT",
    "Claude",
    "Gemini",
    "Antigravity",
    "Codex",
    "GPT",
    "provider",
    "model",
    "subscription",
    "quota",
)
MANAGED_DIRECTORIES = (
    "core",
    "profiles",
    "workflows",
    "project-types",
    "skills",
    "adapters",
    "templates",
    "examples",
    "docs",
)
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".tmpl"}
PLACEHOLDER_PATTERN = re.compile(r"\{\{[^{}\n]+\}\}")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
TOKEN_PATTERNS = (
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
)
MUTATING_ACTIONS = {
    "edit source files",
    "commit changes",
    "push commits",
    "merge a branch",
    "deploy",
}
NON_MUTATING_REQUESTS = {
    "write an implementation plan",
    "run the test suite",
    "prepare a handoff",
    "invoke the review workflow",
}
ADAPTER_REQUIRED = {
    "schema_version",
    "id",
    "label",
    "discovery",
    "template",
    "output",
    "global",
    "recognition",
}
GLOBAL_OUTPUT_PATHS = {
    "generic": "AGENT_RULES.md",
    "codex": ".codex/AGENTS.md",
    "claude": ".claude/CLAUDE.md",
    "gemini": ".gemini/GEMINI.md",
    "antigravity": ".gemini/GEMINI.md",
}
FORBIDDEN_DESTINATION_PREFIXES = (
    ".cache/",
    ".ssh/",
    ".codex/plugins/",
    ".claude/plugins/",
    ".gemini/cache/",
    ".gemini/plugins/",
)
FORBIDDEN_DESTINATION_PARTS = {
    "auth.json",
    "credentials",
    "credentials.json",
    "secrets",
    "id_rsa",
    "id_ed25519",
}
LEGACY_SOURCES = {
    "CLAUDE.base.md",
    "CLAUDE.session.md",
    "CLAUDE.stack.template.md",
    "PATTERNS.template.md",
    "NEW_PROJECT_SETUP.md",
    "SYSTEM_GUIDE.md",
}
MIGRATION_DISPOSITIONS = {"KEEP", "REWRITE", "REFERENCE", "DROP"}
LEVEL_ONE_COMPONENTS = {
    "core/precedence.md",
    "core/agent-contract.md",
    "templates/minimal/AGENT_RULES.md",
}


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _read_json(root: Path, relative: str, errors: List[str]) -> Dict[str, Any]:
    try:
        return load_json_file(root, relative)
    except ConfigError as error:
        errors.append(str(error))
        return {}


def _validate_required_files(root: Path, errors: List[str]) -> None:
    for relative in REQUIRED_FILES:
        try:
            path = resolve_beneath(root, relative, must_exist=True, label=relative)
        except ConfigError as error:
            errors.append(str(error))
            continue
        if not path.is_file():
            errors.append("{}: required file is not a regular file".format(relative))


def _iter_managed_text(root: Path) -> Iterable[Path]:
    for directory in MANAGED_DIRECTORIES:
        base = root / directory
        if not base.is_dir() or base.is_symlink():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix in TEXT_SUFFIXES:
                yield path


def _validate_managed_text(root: Path, errors: List[str]) -> None:
    for path in _iter_managed_text(root):
        relative = _relative(root, path)
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(root)
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError, ValueError) as error:
            errors.append("{}: cannot read safely: {}".format(relative, error))
            continue

        placeholders = PLACEHOLDER_PATTERN.findall(text)
        if path.suffix == ".tmpl":
            invalid = [placeholder for placeholder in placeholders if placeholder != "{{CONTENT}}"]
        else:
            invalid = placeholders
        for placeholder in sorted(set(invalid)):
            errors.append("{}: unresolved placeholder '{}'".format(relative, placeholder))

        if "/Users/" in text or re.search(r"[A-Za-z]:\\\\Users\\\\", text):
            errors.append("{}: machine-private absolute path".format(relative))
        if EMAIL_PATTERN.search(text):
            errors.append("{}: personal email address".format(relative))
        if any(pattern.search(text) for pattern in TOKEN_PATTERNS):
            errors.append("{}: possible credential or token".format(relative))


def _validate_core(root: Path, errors: List[str]) -> None:
    for relative in ("core/agent-contract.md", "core/precedence.md"):
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for term in CORE_FORBIDDEN_TERMS:
            if re.search(r"\b{}\b".format(re.escape(term)), text, flags=re.IGNORECASE):
                errors.append("{}: forbidden universal term '{}'".format(relative, term))


def _validate_package(package_id: str, package: Any, errors: List[str]) -> None:
    prefix = "skills/catalog.yaml: package '{}'".format(package_id)
    if not isinstance(package, dict):
        errors.append("{} must be an object".format(prefix))
        return
    revision = package.get("revision")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        errors.append("{} revision must be an immutable 40-character SHA".format(prefix))
    repository = package.get("repository")
    if not isinstance(repository, str) or not repository.startswith("https://"):
        errors.append("{} repository must be an HTTPS URL".format(prefix))
    if package.get("license") != "MIT":
        errors.append("{} license must be MIT".format(prefix))
    if package.get("required") is not False:
        errors.append("{} must remain optional".format(prefix))


def _validate_skill_catalog(root: Path, errors: List[str]) -> None:
    catalog = _read_json(root, "skills/catalog.yaml", errors)
    if not catalog:
        return
    if catalog.get("format") != "yaml-json-subset":
        errors.append("skills/catalog.yaml: format must be 'yaml-json-subset'")
    packages = catalog.get("packages")
    entries = catalog.get("entries")
    if not isinstance(packages, dict):
        errors.append("skills/catalog.yaml: packages must be an object")
        return
    for package_id, package in sorted(packages.items()):
        _validate_package(package_id, package, errors)
    if not isinstance(entries, list):
        errors.append("skills/catalog.yaml: entries must be an array")
        return

    seen_ids: Set[str] = set()
    automatic_owners: Dict[str, str] = {}
    automatic_capabilities: Dict[str, str] = {}
    for index, entry in enumerate(entries):
        prefix = "skills/catalog.yaml: entries[{}]".format(index)
        if not isinstance(entry, dict):
            errors.append("{} must be an object".format(prefix))
            continue
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not entry_id:
            errors.append("{} id must be a non-empty string".format(prefix))
            continue
        if entry_id in seen_ids:
            errors.append("{} duplicate id '{}'".format(prefix, entry_id))
        seen_ids.add(entry_id)

        strategy = entry.get("strategy")
        if strategy not in {"local_adaptation", "external_reference"}:
            errors.append("{} strategy must be exactly one of local_adaptation or external_reference".format(prefix))
        if "local_adaptation" in entry or "external_reference" in entry:
            errors.append("{} must use only the single strategy field".format(prefix))
        package_id = entry.get("package")
        if package_id not in packages:
            errors.append("{} references unknown package '{}'".format(prefix, package_id))
        try:
            safe_relative_path(entry.get("source_path"), "{} source_path".format(prefix))
        except ConfigError as error:
            errors.append(str(error))

        trigger = entry.get("trigger")
        if not isinstance(trigger, dict):
            errors.append("{} trigger must be an object".format(prefix))
            continue
        mode = trigger.get("mode")
        owner = trigger.get("owner")
        if mode not in {"explicit", "package-managed"}:
            errors.append("{} trigger mode is invalid".format(prefix))
        if not isinstance(owner, str) or not owner:
            errors.append("{} trigger owner must be a non-empty string".format(prefix))
        if mode == "package-managed" and isinstance(owner, str):
            prior = automatic_owners.get(owner)
            if prior is not None:
                errors.append("{} duplicate automatic trigger owner '{}' also used by '{}'".format(prefix, owner, prior))
            automatic_owners[owner] = entry_id
            capability = entry.get("capability")
            if isinstance(capability, str):
                prior_capability = automatic_capabilities.get(capability)
                if prior_capability is not None:
                    errors.append("{} capability '{}' has multiple automatic owners".format(prefix, capability))
                automatic_capabilities[capability] = entry_id

        if strategy == "local_adaptation":
            if mode != "explicit":
                errors.append("{} local adaptation must be explicit-only".format(prefix))
            local_path = entry.get("local_path")
            license_file = entry.get("license_file")
            try:
                local = resolve_beneath(root, local_path, must_exist=True, label="{} local_path".format(prefix))
                for filename in ("SKILL.md", "ORIGIN.md"):
                    if not (local / filename).is_file():
                        errors.append("{} local adaptation is missing {}".format(prefix, filename))
            except (ConfigError, TypeError) as error:
                errors.append(str(error))
            try:
                license_path = resolve_beneath(root, license_file, must_exist=True, label="{} license_file".format(prefix))
                if not license_path.is_file():
                    errors.append("{} adapted license file does not exist".format(prefix))
            except (ConfigError, TypeError):
                errors.append("{} adapted license file does not exist".format(prefix))
        elif strategy == "external_reference" and "local_path" in entry:
            errors.append("{} external reference cannot declare local_path".format(prefix))


def _validate_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _validate_destination(relative: str, category: Any, prefix: str, errors: List[str]) -> None:
    lowered = relative.lower()
    parts = {part.lower() for part in relative.split("/")}
    if lowered.startswith(FORBIDDEN_DESTINATION_PREFIXES) or parts.intersection(FORBIDDEN_DESTINATION_PARTS):
        errors.append("{} forbidden destination category: {}".format(prefix, relative))
    if category == "workspace-rule":
        if not lowered.startswith(".agents/rules/") or not lowered.endswith(".md"):
            errors.append("{} workspace-rule destination must be below .agents/rules".format(prefix))
    elif category == "project-instructions":
        if "/" in relative or not relative.endswith(".md"):
            errors.append("{} project-instructions destination must be a root Markdown file".format(prefix))
    elif category == "global-instructions":
        if not relative.endswith(".md"):
            errors.append("{} global-instructions destination must be a Markdown file".format(prefix))
    else:
        errors.append("{} output category is invalid".format(prefix))


def _validate_official_sources(
    sources: Any,
    kind: Any,
    prefix: str,
    errors: List[str],
) -> None:
    if not isinstance(sources, list):
        errors.append("{}: official_sources must be an array".format(prefix))
        return
    if kind == "automatic" and not sources:
        errors.append("{}: automatic discovery requires an official source".format(prefix))
    for index, source in enumerate(sources):
        source_prefix = "{}: official_sources[{}]".format(prefix, index)
        if not isinstance(source, dict):
            errors.append("{} must be an object".format(source_prefix))
            continue
        if not isinstance(source.get("title"), str) or not source.get("title"):
            errors.append("{} title must be a non-empty string".format(source_prefix))
        if not isinstance(source.get("url"), str) or not source["url"].startswith("https://"):
            errors.append("{} URL must use HTTPS".format(source_prefix))
        if not _validate_date(source.get("accessed")):
            errors.append("{} accessed must be an ISO date".format(source_prefix))
        if "documentation_date" in source and not _validate_date(source["documentation_date"]):
            errors.append("{} documentation_date must be an ISO date".format(source_prefix))


def _validate_adapter(root: Path, adapter_id: str, errors: List[str]) -> bytes:
    relative = "adapters/{}/adapter.json".format(adapter_id)
    data = _read_json(root, relative, errors)
    if not data:
        return b""
    for field in sorted(ADAPTER_REQUIRED - set(data)):
        errors.append("{}: missing required field '{}'".format(relative, field))
    for field in sorted(set(data) - ADAPTER_REQUIRED):
        errors.append("{}: unsupported field '{}'".format(relative, field))
    if data.get("schema_version") != 1:
        errors.append("{}: schema_version must be 1".format(relative))
    if data.get("id") != adapter_id:
        errors.append("{}: id must match its directory".format(relative))
    if not isinstance(data.get("label"), str) or not data.get("label"):
        errors.append("{}: label must be a non-empty string".format(relative))

    discovery = data.get("discovery")
    template = data.get("template")
    output = data.get("output")
    global_target = data.get("global")
    recognition = data.get("recognition")
    if not all(
        isinstance(value, dict)
        for value in (discovery, template, output, global_target, recognition)
    ):
        errors.append(
            "{}: discovery, template, output, global, and recognition must be objects".format(
                relative
            )
        )
        return b""

    output_path = output.get("path")
    discovery_path = discovery.get("project_path")
    for value, label in ((output_path, "output path"), (discovery_path, "discovery project_path")):
        try:
            safe_relative_path(value, "{}: {}".format(relative, label))
        except (ConfigError, TypeError) as error:
            errors.append(str(error))
    if isinstance(output_path, str):
        _validate_destination(output_path, output.get("category"), relative, errors)
    if output_path != discovery_path:
        errors.append("{}: output path must equal discovery project_path".format(relative))

    if discovery.get("kind") not in {"automatic", "manual"}:
        errors.append("{}: discovery kind is invalid".format(relative))
    if discovery.get("scope") != "project":
        errors.append("{}: discovery scope must be project".format(relative))
    _validate_official_sources(
        discovery.get("official_sources"), discovery.get("kind"), relative, errors
    )

    global_discovery = global_target.get("discovery")
    global_output = global_target.get("output")
    if not isinstance(global_discovery, dict) or not isinstance(global_output, dict):
        errors.append("{}: global discovery and output must be objects".format(relative))
    else:
        global_path = global_output.get("path")
        global_discovery_path = global_discovery.get("path")
        for value, label in (
            (global_path, "global output path"),
            (global_discovery_path, "global discovery path"),
        ):
            try:
                safe_relative_path(value, "{}: {}".format(relative, label))
            except (ConfigError, TypeError) as error:
                errors.append(str(error))
        if isinstance(global_path, str):
            _validate_destination(
                global_path, global_output.get("category"), relative, errors
            )
            expected_global_path = GLOBAL_OUTPUT_PATHS.get(adapter_id)
            if global_path != expected_global_path:
                errors.append(
                    "{}: global output path must be '{}'".format(
                        relative, expected_global_path
                    )
                )
        if global_path != global_discovery_path:
            errors.append("{}: global output path must equal discovery path".format(relative))
        if global_discovery.get("kind") not in {"automatic", "manual"}:
            errors.append("{}: global discovery kind is invalid".format(relative))
        if global_discovery.get("scope") != "global":
            errors.append("{}: global discovery scope must be global".format(relative))
        _validate_official_sources(
            global_discovery.get("official_sources"),
            global_discovery.get("kind"),
            "{}: global".format(relative),
            errors,
        )

    if template.get("content_mode") != "canonical-bundle":
        errors.append("{}: template content_mode must be canonical-bundle".format(relative))
    template_path = template.get("path")
    try:
        path = resolve_beneath(root, template_path, must_exist=True, label="{}: template path".format(relative))
        template_bytes = path.read_bytes()
        if template_bytes.count(b"{{CONTENT}}") != 1:
            errors.append("{}: template must contain {{CONTENT}} exactly once".format(relative))
        remaining = template_bytes.replace(b"{{CONTENT}}", b"")
        if PLACEHOLDER_PATTERN.search(remaining.decode("utf-8")):
            errors.append("{}: template contains an unsupported placeholder".format(relative))
    except (ConfigError, OSError, UnicodeError, TypeError) as error:
        errors.append(str(error))
        template_bytes = b""

    mode = recognition.get("mode")
    if mode == "command":
        executable_env = recognition.get("executable_env")
        if not isinstance(executable_env, str) or not re.fullmatch(r"AI_AGENT_CONFIG_[A-Z0-9_]+_EXECUTABLE", executable_env):
            errors.append("{}: recognition executable_env is invalid".format(relative))
        arguments = recognition.get("arguments")
        if not isinstance(arguments, list) or not all(isinstance(value, str) for value in arguments or []):
            errors.append("{}: recognition arguments must be strings".format(relative))
        elif any(
            value in {"--model", "-m", "--subscription"}
            or value.startswith("--model=")
            or "subscription" in value.lower()
            for value in arguments
        ):
            errors.append("{}: recognition cannot fix a model or subscription".format(relative))
        if not isinstance(recognition.get("marker_label"), str) or not re.fullmatch(r"[A-Z][A-Z0-9_]+", recognition.get("marker_label", "")):
            errors.append("{}: recognition marker_label is invalid".format(relative))
    elif mode == "manual":
        if not isinstance(recognition.get("instructions"), str) or not recognition.get("instructions"):
            errors.append("{}: manual recognition requires instructions".format(relative))
    else:
        errors.append("{}: recognition mode is invalid".format(relative))
    return template_bytes


def _validate_adapters(root: Path, errors: List[str]) -> None:
    schema = _read_json(root, "adapters/catalog.schema.json", errors)
    if schema and schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("adapters/catalog.schema.json: unsupported schema dialect")
    adapters_root = root / "adapters"
    found = {
        path.parent.name
        for path in adapters_root.glob("*/adapter.json")
        if path.is_file() and not path.is_symlink()
    }
    for missing in sorted(REQUIRED_ADAPTERS - found):
        errors.append("adapters: missing required adapter '{}'".format(missing))
    templates = []
    for adapter_id in sorted(found):
        body = _validate_adapter(root, adapter_id, errors)
        if body:
            templates.append((adapter_id, body))
    if templates:
        canonical = templates[0][1]
        for adapter_id, body in templates[1:]:
            if body != canonical:
                errors.append("adapters/{}: template changes canonical policy semantics".format(adapter_id))


def _validate_authorization_cases(root: Path, errors: List[str]) -> None:
    relative = "tests/fixtures/authorization-cases.json"
    data = _read_json(root, relative, errors)
    cases = data.get("cases") if data else None
    if not isinstance(cases, list):
        errors.append("{}: cases must be an array".format(relative))
        return
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append("{}: cases[{}] must be an object".format(relative, index))
            continue
        request = case.get("request")
        action = case.get("action")
        authorized = case.get("authorized")
        if not isinstance(request, str) or not isinstance(action, str) or not isinstance(authorized, bool):
            errors.append("{}: cases[{}] has invalid field types".format(relative, index))
            continue
        if request in NON_MUTATING_REQUESTS and action in MUTATING_ACTIONS and authorized:
            errors.append("{}: cases[{}] non-mutating request grants mutation".format(relative, index))


def _validate_migration_map(root: Path, errors: List[str]) -> None:
    relative = "docs/migration-map.json"
    data = _read_json(root, relative, errors)
    sources = data.get("sources") if data else None
    if not isinstance(sources, list):
        errors.append("{}: sources must be an array".format(relative))
        sources = []
    seen: Set[str] = set()
    dispositions: Set[str] = set()
    for index, source in enumerate(sources):
        prefix = "{}: sources[{}]".format(relative, index)
        if not isinstance(source, dict):
            errors.append("{} must be an object".format(prefix))
            continue
        path = source.get("path")
        if path not in LEGACY_SOURCES:
            errors.append("{} has unknown legacy path '{}'".format(prefix, path))
        elif path in seen:
            errors.append("{} duplicates legacy source '{}'".format(prefix, path))
        else:
            seen.add(path)
        concepts = source.get("concepts")
        if not isinstance(concepts, list) or not concepts:
            errors.append("{} concepts must be a non-empty array".format(prefix))
            continue
        for concept_index, concept in enumerate(concepts):
            concept_prefix = "{} concepts[{}]".format(prefix, concept_index)
            if not isinstance(concept, dict):
                errors.append("{} must be an object".format(concept_prefix))
                continue
            if not isinstance(concept.get("name"), str) or not concept.get("name"):
                errors.append("{} name must be a non-empty string".format(concept_prefix))
            disposition = concept.get("disposition")
            if disposition not in MIGRATION_DISPOSITIONS:
                errors.append("{} disposition is invalid".format(concept_prefix))
            else:
                dispositions.add(disposition)
            destination = concept.get("destination")
            if disposition == "DROP":
                if destination is not None:
                    errors.append("{} DROP destination must be null".format(concept_prefix))
            else:
                try:
                    safe_relative_path(destination, "{} destination".format(concept_prefix))
                except (ConfigError, TypeError) as error:
                    errors.append(str(error))
            if not isinstance(concept.get("reason"), str) or not concept.get("reason"):
                errors.append("{} reason must be a non-empty string".format(concept_prefix))
    for missing in sorted(LEGACY_SOURCES - seen):
        errors.append("{}: missing legacy source '{}'".format(relative, missing))
    for missing in sorted(MIGRATION_DISPOSITIONS - dispositions):
        errors.append("{}: missing disposition '{}'".format(relative, missing))


def _validate_level_one(root: Path, errors: List[str]) -> None:
    relative = "examples/level-1-minimal/example.json"
    data = _read_json(root, relative, errors)
    if not data:
        return
    if data.get("version") != 1 or data.get("level") != 1:
        errors.append("{}: version and level must both be 1".format(relative))
    if data.get("external_skills") is not False:
        errors.append("{}: Level 1 cannot require external skills".format(relative))
    if data.get("global_configuration") is not False:
        errors.append("{}: Level 1 cannot require global configuration".format(relative))
    adapter_id = data.get("adapter")
    if adapter_id not in REQUIRED_ADAPTERS:
        errors.append("{}: adapter is not supported".format(relative))
    else:
        adapter = _read_json(root, "adapters/{}/adapter.json".format(adapter_id), errors)
        if adapter:
            if adapter.get("discovery", {}).get("kind") != "automatic":
                errors.append("{}: Level 1 adapter must support automatic project discovery".format(relative))
            if data.get("output") != adapter.get("output", {}).get("path"):
                errors.append("{}: output must match the selected adapter".format(relative))
    components = data.get("components")
    if not isinstance(components, list) or set(components) != LEVEL_ONE_COMPONENTS:
        errors.append("{}: components must be the complete minimal canonical bundle".format(relative))
    else:
        for component in components:
            try:
                resolve_beneath(root, component, must_exist=True, label="{} component".format(relative))
            except ConfigError as error:
                errors.append(str(error))


def validate(root: Path) -> List[str]:
    """Return deterministic validation errors for a repository root."""

    try:
        resolved_root = Path(root).resolve(strict=True)
    except FileNotFoundError:
        return ["repository root does not exist: {}".format(root)]
    if not resolved_root.is_dir():
        return ["repository root is not a directory: {}".format(root)]

    errors: List[str] = []
    _validate_required_files(resolved_root, errors)
    _validate_managed_text(resolved_root, errors)
    _validate_core(resolved_root, errors)
    _validate_skill_catalog(resolved_root, errors)
    _validate_adapters(resolved_root, errors)
    _validate_authorization_cases(resolved_root, errors)
    _validate_migration_map(resolved_root, errors)
    _validate_level_one(resolved_root, errors)
    return sorted(set(errors))
