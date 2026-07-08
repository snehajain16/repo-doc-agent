import re
import json
from pathlib import Path


def _safe_path(path: str, repo_root: Path) -> Path:
    """Resolve path and verify it stays within repo_root. Raises ValueError if traversal detected."""
    resolved = (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        raise ValueError(f"Path traversal detected: {path!r} escapes repo root")
    return resolved


def list_files(path: str, repo_root: Path) -> list[str]:
    """List files and directories at the given path within the repo."""
    target = _safe_path(path, repo_root)
    if not target.exists():
        return []
    if target.is_file():
        return [str(target.relative_to(repo_root))]
    entries = []
    for entry in sorted(target.iterdir()):
        rel = str(entry.relative_to(repo_root))
        # Skip hidden dirs except .github
        if entry.name.startswith(".") and entry.name not in (".github",):
            continue
        entries.append(rel + ("/" if entry.is_dir() else ""))
    return entries


def read_file(path: str, repo_root: Path, max_chars: int = 8000) -> str:
    """Read a file's content, truncated to max_chars."""
    target = _safe_path(path, repo_root)
    if not target.exists() or not target.is_file():
        return f"File not found: {path}"
    content = target.read_text(encoding="utf-8", errors="replace")
    if len(content) > max_chars:
        content = content[:max_chars] + f"\n... [truncated at {max_chars} chars]"
    return content


def search_code(pattern: str, repo_root: Path) -> list[dict]:
    """Search for a regex pattern across all text files in the repo. Returns up to 20 matches."""
    matches = []
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return [{"error": f"Invalid regex: {e}"}]

    skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "dist", "build"}
    skip_exts = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".ttf", ".eot", ".pdf", ".zip", ".tar", ".gz"}

    for file_path in sorted(repo_root.rglob("*")):
        if not file_path.is_file():
            continue
        if any(part in skip_dirs for part in file_path.parts):
            continue
        if file_path.suffix.lower() in skip_exts:
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(text.splitlines(), 1):
                if regex.search(line):
                    matches.append({
                        "file": str(file_path.relative_to(repo_root)),
                        "line": i,
                        "content": line.strip()[:200],
                    })
                    if len(matches) >= 20:
                        return matches
        except Exception:
            continue
    return matches


def detect_language(repo_root: Path) -> dict:
    """Detect primary language and frameworks from file extensions and config files."""
    ext_counts: dict[str, int] = {}
    skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "dist", "build"}

    for file_path in repo_root.rglob("*"):
        if not file_path.is_file():
            continue
        if any(part in skip_dirs for part in file_path.parts):
            continue
        ext = file_path.suffix.lower()
        if ext:
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

    ext_to_lang = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".tsx": "TypeScript", ".jsx": "JavaScript", ".go": "Go",
        ".rs": "Rust", ".java": "Java", ".rb": "Ruby", ".php": "PHP",
        ".cs": "C#", ".cpp": "C++", ".c": "C", ".swift": "Swift",
        ".kt": "Kotlin", ".scala": "Scala", ".r": "R", ".sh": "Shell",
    }

    lang_counts: dict[str, int] = {}
    for ext, count in ext_counts.items():
        lang = ext_to_lang.get(ext)
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + count

    primary = max(lang_counts, key=lambda k: lang_counts[k]) if lang_counts else "Unknown"
    others = [lang for lang in lang_counts if lang != primary]

    # Detect frameworks
    frameworks = []
    framework_indicators = {
        "FastAPI": ["fastapi"],
        "Django": ["django"],
        "Flask": ["flask"],
        "React": ["react", "react-dom"],
        "Next.js": ["next"],
        "Vue": ["vue"],
        "Express": ["express"],
        "Gin": ["gin-gonic/gin"],
        "Echo": ["labstack/echo"],
        "Rails": ["rails"],
        "Spring": ["spring-boot"],
    }
    dep_files = ["requirements.txt", "package.json", "go.mod", "Cargo.toml", "pyproject.toml", "Gemfile"]
    dep_text = ""
    for df in dep_files:
        p = repo_root / df
        if p.exists():
            dep_text += p.read_text(errors="replace").lower()
    for fw, indicators in framework_indicators.items():
        if any(ind in dep_text for ind in indicators):
            frameworks.append(fw)

    return {"primary": primary, "others": others, "frameworks": frameworks, "extension_counts": ext_counts}


def read_dependency_file(repo_root: Path) -> dict:
    """Parse dependencies from known manifest files."""
    result: dict[str, object] = {}

    # Python - requirements.txt
    req_txt = repo_root / "requirements.txt"
    if req_txt.exists():
        deps = [line.strip() for line in req_txt.read_text().splitlines() if line.strip() and not line.startswith("#")]
        result["requirements.txt"] = deps

    # Python - pyproject.toml (basic parse)
    pyproject = repo_root / "pyproject.toml"
    if pyproject.exists():
        result["pyproject.toml"] = pyproject.read_text()[:3000]

    # Node - package.json
    pkg_json = repo_root / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text())
            result["package.json"] = {
                "name": data.get("name"),
                "version": data.get("version"),
                "dependencies": list(data.get("dependencies", {}).keys()),
                "devDependencies": list(data.get("devDependencies", {}).keys()),
                "scripts": data.get("scripts", {}),
            }
        except Exception:
            result["package.json"] = pkg_json.read_text()[:3000]

    # Go - go.mod
    go_mod = repo_root / "go.mod"
    if go_mod.exists():
        result["go.mod"] = go_mod.read_text()[:3000]

    # Rust - Cargo.toml
    cargo = repo_root / "Cargo.toml"
    if cargo.exists():
        result["Cargo.toml"] = cargo.read_text()[:3000]

    if not result:
        result["note"] = "No known dependency files found"

    return result


# Anthropic tool schema definitions
TOOLS_SCHEMA = [
    {
        "name": "list_files",
        "description": "List files and directories at the given path within the repository. Use '.' for root.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path within the repo, e.g. '.' or 'src/'"}
            },
            "required": ["path"],
        },
    },
    {
        "name": "read_file",
        "description": "Read the content of a file. Content is truncated at 8000 characters.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path to the file"}
            },
            "required": ["path"],
        },
    },
    {
        "name": "search_code",
        "description": "Search for a regex pattern across all text files. Returns up to 20 matches with file, line number, and content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex pattern to search for"}
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "detect_language",
        "description": "Detect the primary programming language and frameworks used in the repository.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "read_dependency_file",
        "description": "Parse and return dependencies from known manifest files (requirements.txt, package.json, go.mod, Cargo.toml, pyproject.toml).",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


def dispatch_tool(name: str, args: dict, repo_root: Path) -> object:
    """Route a tool call by name to the correct implementation."""
    if name == "list_files":
        return list_files(args.get("path", "."), repo_root)
    elif name == "read_file":
        return read_file(args["path"], repo_root)
    elif name == "search_code":
        return search_code(args["pattern"], repo_root)
    elif name == "detect_language":
        return detect_language(repo_root)
    elif name == "read_dependency_file":
        return read_dependency_file(repo_root)
    else:
        return f"Unknown tool: {name}"
