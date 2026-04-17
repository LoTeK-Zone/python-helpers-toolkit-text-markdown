#!/usr/bin/env python3
"""
python_helpers.py
Version: 0.1.4
Date: 2026-04-17

A compact standard-library helper collection for recurring project tasks.
The file is intentionally self-contained and executable as a CLI.
"""

from __future__ import annotations

import argparse
import configparser
import fnmatch
import json
import re
import sys
from pathlib import Path
from typing import Iterable

VERSION = "0.1.4"
DEFAULT_IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".idea",
    ".vscode",
}


def _read_text(path: Path, encoding: str = "utf-8") -> str:
    return path.read_text(encoding=encoding)



def _write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding=encoding)



def _parse_extensions(items: list[str] | None) -> set[str] | None:
    if not items:
        return None

    result: set[str] = set()

    for item in items:
        for part in item.split(","):
            s_part = part.strip().lower()
            if not s_part:
                continue
            if not s_part.startswith("."):
                s_part = "." + s_part
            result.add(s_part)

    return result or None



def _parse_comma_list(items: list[str] | None) -> list[str]:
    if not items:
        return []

    result: list[str] = []

    for item in items:
        for part in item.split(","):
            s_part = part.strip()
            if s_part:
                result.append(s_part)

    return result



def _matches_any(name: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)



def _infer_toml_value(raw_value: str) -> str:
    value = raw_value.strip()
    lowered = value.lower()

    if lowered in {"true", "false"}:
        return lowered

    if lowered in {"none", "null"}:
        return '""'

    if re.fullmatch(r"[+-]?\d+", value):
        return value

    if re.fullmatch(r"[+-]?\d+\.\d+", value):
        return value

    if value.startswith("[") and value.endswith("]"):
        return value

    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'



def build_project_index(
    root: Path,
    include_ext: set[str] | None,
    ignored_dirs: set[str],
    ignored_patterns: list[str],
    max_depth: int | None,
    include_hidden: bool,
    max_files: int | None,
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    root = root.resolve()

    for path in root.rglob("*"):
        rel_path = path.relative_to(root)
        parts = rel_path.parts

        if not parts:
            continue

        if not include_hidden and any(part.startswith(".") for part in parts):
            continue

        if any(part in ignored_dirs for part in parts[:-1]):
            continue

        if max_depth is not None and len(parts) - 1 > max_depth:
            continue

        if _matches_any(str(rel_path), ignored_patterns):
            continue

        if path.is_dir():
            continue

        if include_ext and path.suffix.lower() not in include_ext:
            continue

        stat = path.stat()
        results.append(
            {
                "path": str(rel_path).replace("\\", "/"),
                "suffix": path.suffix.lower(),
                "size": stat.st_size,
            }
        )

        if max_files is not None and len(results) >= max_files:
            break

    results.sort(key=lambda item: str(item["path"]).lower())
    return results



def render_project_index_text(root: Path, entries: list[dict[str, object]]) -> str:
    lines = [f"Project index for: {root}", f"Files: {len(entries)}", ""]

    for entry in entries:
        lines.append(f"{entry['path']} | {entry['size']} bytes")

    return "\n".join(lines)



def extract_markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    target = heading.strip().lower()
    start_index: int | None = None
    start_level: int | None = None

    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip().lower()
        if title == target:
            start_index = index
            start_level = level
            break

    if start_index is None or start_level is None:
        raise ValueError(f"Heading not found: {heading}")

    end_index = len(lines)

    for index in range(start_index + 1, len(lines)):
        match = re.match(r"^(#{1,6})\s+(.*?)\s*$", lines[index])
        if match and len(match.group(1)) <= start_level:
            end_index = index
            break

    return "\n".join(lines[start_index:end_index]).rstrip() + "\n"



def extract_fenced_code_blocks(text: str, language: str | None = None) -> list[str]:
    pattern = re.compile(r"```([\w+-]*)\n(.*?)\n```", re.DOTALL)
    results: list[str] = []
    wanted = (language or "").strip().lower()

    for match in pattern.finditer(text):
        lang = match.group(1).strip().lower()
        block = match.group(2)
        if wanted and lang != wanted:
            continue
        results.append(block)

    return results



def replace_between_markers(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start_index = text.find(start_marker)
    if start_index == -1:
        raise ValueError("Start marker not found")

    search_from = start_index + len(start_marker)
    end_index = text.find(end_marker, search_from)
    if end_index == -1:
        raise ValueError("End marker not found")

    return text[:search_from] + "\n" + replacement.rstrip("\n") + "\n" + text[end_index:]



def convert_ini_to_toml(ini_text: str) -> str:
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    parser.read_string(ini_text)
    lines: list[str] = []

    defaults = dict(parser.defaults())
    if defaults:
        for key, value in defaults.items():
            lines.append(f"{key} = {_infer_toml_value(value)}")
        lines.append("")

    for section in parser.sections():
        lines.append(f"[{section}]")
        for key, value in parser.items(section, raw=True):
            if key in defaults and defaults[key] == value:
                continue
            lines.append(f"{key} = {_infer_toml_value(value)}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"



def normalize_text(
    text: str,
    line_ending: str,
    trim_trailing_ws: bool,
    final_newline: bool,
    tab_size: int | None,
) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")

    if trim_trailing_ws:
        lines = [line.rstrip() for line in lines]

    if tab_size is not None:
        lines = [line.expandtabs(tab_size) for line in lines]

    normalized = "\n".join(lines)

    if final_newline:
        normalized = normalized.rstrip("\n") + "\n"

    if line_ending == "lf":
        return normalized
    if line_ending == "crlf":
        return normalized.replace("\n", "\r\n")

    raise ValueError(f"Unsupported line ending: {line_ending}")



def pretty_json(text: str, indent: int, sort_keys: bool, ensure_ascii: bool) -> str:
    data = json.loads(text)
    return json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii) + "\n"



def cmd_project_index(args: argparse.Namespace) -> int:
    root = Path(args.root)
    include_ext = _parse_extensions(args.ext)
    ignored_dirs = DEFAULT_IGNORED_DIRS | set(_parse_comma_list(args.ignore_dir))
    ignored_patterns = _parse_comma_list(args.ignore)
    entries = build_project_index(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=args.max_depth,
        include_hidden=args.include_hidden,
        max_files=args.max_files,
    )

    if args.format == "json":
        output = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_project_index_text(root, entries)
        if not output.endswith("\n"):
            output += "\n"

    if args.output:
        _write_text(Path(args.output), output)
    else:
        sys.stdout.write(output)

    return 0



def cmd_extract_section(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    output = extract_markdown_section(source, args.heading)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_extract_codeblocks(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    blocks = extract_fenced_code_blocks(source, args.language)

    if not blocks:
        raise ValueError("No matching code blocks found")

    if args.output_dir:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        extension = args.extension or (args.language.lower() if args.language else "txt")
        extension = extension.lstrip(".")

        for index, block in enumerate(blocks, start=1):
            out_path = out_dir / f"block_{index:03d}.{extension}"
            _write_text(out_path, block.rstrip("\n") + "\n", encoding=args.encoding)

        sys.stdout.write(f"Wrote {len(blocks)} code block(s) to {out_dir}\n")
        return 0

    selected = blocks if args.all else [blocks[args.index - 1]]
    output = "\n\n".join(block.rstrip("\n") for block in selected) + "\n"

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_replace_between_markers(args: argparse.Namespace) -> int:
    target_path = Path(args.input)
    source = _read_text(target_path, encoding=args.encoding)

    if args.replacement_file:
        replacement = _read_text(Path(args.replacement_file), encoding=args.encoding)
    else:
        replacement = args.replacement_text or ""

    output = replace_between_markers(source, args.start_marker, args.end_marker, replacement)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        _write_text(target_path, output, encoding=args.encoding)

    return 0



def cmd_ini_to_toml(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    output = convert_ini_to_toml(source)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_normalize_text(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    source = _read_text(input_path, encoding=args.encoding)
    output = normalize_text(
        text=source,
        line_ending=args.line_ending,
        trim_trailing_ws=not args.keep_trailing_ws,
        final_newline=not args.no_final_newline,
        tab_size=args.expand_tabs,
    )

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        _write_text(input_path, output, encoding=args.encoding)

    return 0



def cmd_json_pretty(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    output = pretty_json(
        text=source,
        indent=args.indent,
        sort_keys=args.sort_keys,
        ensure_ascii=args.ensure_ascii,
    )

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def _sanitize_filename(name: str) -> str:
    cleaned = name.strip().lower()  # normalize for stable file output
    cleaned = re.sub(r"[^a-z0-9._ -]+", "_", cleaned)  # replace unsafe characters
    cleaned = cleaned.replace(" ", "_")  # keep output filenames shell-friendly
    cleaned = re.sub(r"_+", "_", cleaned)  # collapse duplicate separators
    cleaned = cleaned.strip("._")  # remove unstable edge characters
    return cleaned or "section"  # fallback for empty headings



def _collect_text_files(
    root: Path,
    include_ext: set[str] | None,
    ignored_dirs: set[str],
    ignored_patterns: list[str],
    max_depth: int | None,
    include_hidden: bool,
    max_files: int | None,
) -> list[Path]:
    files: list[Path] = []
    root = root.resolve()

    for path in root.rglob("*"):
        rel_path = path.relative_to(root)
        parts = rel_path.parts

        if not parts:
            continue

        if not include_hidden and any(part.startswith(".") for part in parts):
            continue  # skip hidden content unless explicitly requested

        if any(part in ignored_dirs for part in parts[:-1]):
            continue  # skip files inside ignored directories

        if max_depth is not None and len(parts) - 1 > max_depth:
            continue  # stop at configured relative depth

        if _matches_any(str(rel_path), ignored_patterns):
            continue  # skip ignored glob-style paths

        if path.is_dir():
            continue  # collect files only

        if include_ext and path.suffix.lower() not in include_ext:
            continue  # keep only wanted suffixes

        files.append(path)

        if max_files is not None and len(files) >= max_files:
            break  # stop early for bounded scans

    files.sort(key=lambda item: str(item).lower())
    return files



def find_text_matches(
    root: Path,
    query: str,
    include_ext: set[str] | None,
    ignored_dirs: set[str],
    ignored_patterns: list[str],
    max_depth: int | None,
    include_hidden: bool,
    max_files: int | None,
    use_regex: bool,
    case_sensitive: bool,
    encoding: str,
    max_matches: int | None,
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    files = _collect_text_files(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=max_depth,
        include_hidden=include_hidden,
        max_files=max_files,
    )
    root = root.resolve()

    flags = 0 if case_sensitive else re.IGNORECASE  # keep literal and regex mode aligned
    regex = re.compile(query, flags) if use_regex else None
    needle = query if case_sensitive else query.lower()

    for path in files:
        text = _read_text(path, encoding=encoding)

        for line_number, line in enumerate(text.splitlines(), start=1):
            matched = bool(regex.search(line)) if regex else needle in (line if case_sensitive else line.lower())
            if not matched:
                continue

            results.append(
                {
                    "path": str(path.relative_to(root)).replace("\\", "/"),
                    "line": line_number,
                    "text": line,
                }
            )

            if max_matches is not None and len(results) >= max_matches:
                return results  # bounded result mode for large projects

    return results



def render_text_matches_text(root: Path, matches: list[dict[str, object]]) -> str:
    lines = [f"Text matches for: {root}", f"Matches: {len(matches)}", ""]

    for match in matches:
        lines.append(f"{match['path']}:{match['line']} | {match['text']}")

    return "\n".join(lines).rstrip() + "\n"



def replace_text_matches(
    root: Path,
    query: str,
    replacement: str,
    include_ext: set[str] | None,
    ignored_dirs: set[str],
    ignored_patterns: list[str],
    max_depth: int | None,
    include_hidden: bool,
    max_files: int | None,
    use_regex: bool,
    case_sensitive: bool,
    encoding: str,
    create_backup: bool,
    dry_run: bool,
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    files = _collect_text_files(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=max_depth,
        include_hidden=include_hidden,
        max_files=max_files,
    )
    root = root.resolve()

    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(query, flags) if use_regex else None

    for path in files:
        source = _read_text(path, encoding=encoding)

        if regex:
            updated, replacements = regex.subn(replacement, source)  # regex mode supports groups and patterns
        else:
            if case_sensitive:
                updated = source.replace(query, replacement)
                replacements = source.count(query)
            else:
                updated, replacements = re.subn(re.escape(query), replacement, source, flags=re.IGNORECASE)

        if replacements <= 0:
            continue

        rel_path = str(path.relative_to(root)).replace("\\", "/")
        results.append({"path": rel_path, "replacements": replacements})

        if dry_run:
            continue  # preview mode without touching files

        if create_backup:
            backup_path = path.with_suffix(path.suffix + ".bak")
            _write_text(backup_path, source, encoding=encoding)  # simple rollback support

        _write_text(path, updated, encoding=encoding)

    return results



def render_replace_results_text(root: Path, results: list[dict[str, object]], dry_run: bool) -> str:
    mode = "Dry run" if dry_run else "Applied"
    lines = [f"{mode} replacements for: {root}", f"Changed files: {len(results)}", ""]

    for item in results:
        lines.append(f"{item['path']} | replacements={item['replacements']}")

    return "\n".join(lines).rstrip() + "\n"



def build_markdown_heading_index(text: str) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        match = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if not match:
            continue  # only standard ATX headings are indexed

        level = len(match.group(1))
        title = match.group(2).strip()
        anchor = re.sub(r"[^a-z0-9 -]", "", title.lower())  # simple GitHub-like anchor approximation
        anchor = anchor.replace(" ", "-")
        anchor = re.sub(r"-+", "-", anchor).strip("-")
        results.append(
            {
                "level": level,
                "title": title,
                "line": line_number,
                "anchor": anchor,
            }
        )

    return results



def render_heading_index_text(entries: list[dict[str, object]]) -> str:
    lines = [f"Headings: {len(entries)}", ""]

    for entry in entries:
        indent = "  " * (int(entry["level"]) - 1)
        lines.append(f"{indent}L{entry['line']} | H{entry['level']} | {entry['title']} | #{entry['anchor']}")

    return "\n".join(lines).rstrip() + "\n"



def split_markdown_sections(text: str, level: int) -> list[dict[str, object]]:
    lines = text.splitlines()
    sections: list[dict[str, object]] = []
    matches: list[tuple[int, int, str]] = []

    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if not match:
            continue
        if len(match.group(1)) != level:
            continue  # split only on the requested heading level
        matches.append((index, level, match.group(2).strip()))

    for idx, (start_index, _heading_level, title) in enumerate(matches):
        end_index = matches[idx + 1][0] if idx + 1 < len(matches) else len(lines)
        content = "\n".join(lines[start_index:end_index]).rstrip() + "\n"
        sections.append(
            {
                "title": title,
                "slug": _sanitize_filename(title),
                "content": content,
            }
        )

    return sections



def build_project_manifest(
    root: Path,
    include_ext: set[str] | None,
    ignored_dirs: set[str],
    ignored_patterns: list[str],
    max_depth: int | None,
    include_hidden: bool,
    max_files: int | None,
    top_n: int,
) -> dict[str, object]:
    files = _collect_text_files(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=max_depth,
        include_hidden=include_hidden,
        max_files=max_files,
    )
    root = root.resolve()
    suffix_stats: dict[str, dict[str, int]] = {}
    largest_files: list[dict[str, object]] = []
    total_bytes = 0

    for path in files:
        stat = path.stat()
        size = stat.st_size
        suffix = path.suffix.lower() or "<no_ext>"
        total_bytes += size

        if suffix not in suffix_stats:
            suffix_stats[suffix] = {"count": 0, "bytes": 0}

        suffix_stats[suffix]["count"] += 1
        suffix_stats[suffix]["bytes"] += size
        largest_files.append({"path": str(path.relative_to(root)).replace("\\", "/"), "size": size})

    largest_files.sort(key=lambda item: int(item["size"]), reverse=True)
    suffix_rows = [
        {"suffix": suffix, "count": data["count"], "bytes": data["bytes"]}
        for suffix, data in sorted(suffix_stats.items(), key=lambda item: item[0])
    ]

    return {
        "root": str(root),
        "files": len(files),
        "total_bytes": total_bytes,
        "by_suffix": suffix_rows,
        "largest_files": largest_files[:top_n],
    }



def render_project_manifest_text(manifest: dict[str, object]) -> str:
    lines = [
        f"Project manifest for: {manifest['root']}",
        f"Files: {manifest['files']}",
        f"Total bytes: {manifest['total_bytes']}",
        "",
        "By suffix:",
    ]

    for row in manifest["by_suffix"]:
        lines.append(f"{row['suffix']} | count={row['count']} | bytes={row['bytes']}")

    lines.append("")
    lines.append("Largest files:")

    for item in manifest["largest_files"]:
        lines.append(f"{item['path']} | {item['size']} bytes")

    return "\n".join(lines).rstrip() + "\n"



def cmd_find_text(args: argparse.Namespace) -> int:
    root = Path(args.root)
    include_ext = _parse_extensions(args.ext)
    ignored_dirs = DEFAULT_IGNORED_DIRS | set(_parse_comma_list(args.ignore_dir))
    ignored_patterns = _parse_comma_list(args.ignore)
    matches = find_text_matches(
        root=root,
        query=args.query,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=args.max_depth,
        include_hidden=args.include_hidden,
        max_files=args.max_files,
        use_regex=args.regex,
        case_sensitive=args.case_sensitive,
        encoding=args.encoding,
        max_matches=args.max_matches,
    )

    if args.format == "json":
        output = json.dumps(matches, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_text_matches_text(root, matches)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_safe_search_replace(args: argparse.Namespace) -> int:
    root = Path(args.root)
    include_ext = _parse_extensions(args.ext)
    ignored_dirs = DEFAULT_IGNORED_DIRS | set(_parse_comma_list(args.ignore_dir))
    ignored_patterns = _parse_comma_list(args.ignore)
    results = replace_text_matches(
        root=root,
        query=args.query,
        replacement=args.replacement,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=args.max_depth,
        include_hidden=args.include_hidden,
        max_files=args.max_files,
        use_regex=args.regex,
        case_sensitive=args.case_sensitive,
        encoding=args.encoding,
        create_backup=args.create_backup,
        dry_run=args.dry_run,
    )

    if args.format == "json":
        output = json.dumps(results, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_replace_results_text(root, results, dry_run=args.dry_run)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_md_heading_index(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    entries = build_markdown_heading_index(source)

    if args.format == "json":
        output = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_heading_index_text(entries)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_split_markdown_sections(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    source = _read_text(input_path, encoding=args.encoding)
    sections = split_markdown_sections(source, level=args.level)

    if not sections:
        raise ValueError(f"No markdown headings found for level {args.level}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"{args.prefix}_" if args.prefix else ""

    for index, section in enumerate(sections, start=1):
        file_name = f"{prefix}{index:03d}_{section['slug']}.md"
        _write_text(output_dir / file_name, str(section["content"]), encoding=args.encoding)

    sys.stdout.write(f"Wrote {len(sections)} section file(s) to {output_dir}\n")
    return 0



def cmd_project_manifest(args: argparse.Namespace) -> int:
    root = Path(args.root)
    include_ext = _parse_extensions(args.ext)
    ignored_dirs = DEFAULT_IGNORED_DIRS | set(_parse_comma_list(args.ignore_dir))
    ignored_patterns = _parse_comma_list(args.ignore)
    manifest = build_project_manifest(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=args.max_depth,
        include_hidden=args.include_hidden,
        max_files=args.max_files,
        top_n=args.top_n,
    )

    if args.format == "json":
        output = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_project_manifest_text(manifest)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0


def extract_frontmatter_block(text: str) -> tuple[dict[str, object], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("Frontmatter block not found at start of file")  # require leading block only

    end_index: int | None = None

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break  # stop at the closing delimiter

    if end_index is None:
        raise ValueError("Closing frontmatter delimiter not found")

    raw_block = "\n".join(lines[1:end_index]).strip() + "\n"
    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    data: dict[str, object] = {}

    for line_number, line in enumerate(raw_block.splitlines(), start=1):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue  # ignore empty lines and simple comment lines

        if ":" not in stripped:
            raise ValueError(f"Invalid frontmatter line {line_number}: {line}")

        key, value = stripped.split(":", 1)
        s_key = key.strip()
        s_value = value.strip()

        if not s_key:
            raise ValueError(f"Empty frontmatter key on line {line_number}")

        data[s_key] = _parse_simple_scalar_or_list(s_value)

    return data, body


def _parse_simple_scalar_or_list(value: str) -> object:
    lowered = value.lower()

    if not value:
        return ""

    if lowered in {"true", "false"}:
        return lowered == "true"  # convert common boolean values

    if lowered in {"null", "none"}:
        return None  # convert null-like values

    if re.fullmatch(r"[+-]?\d+", value):
        return int(value)  # parse integer values

    if re.fullmatch(r"[+-]?\d+\.\d+", value):
        return float(value)  # parse float values

    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []  # support empty arrays
        return [_parse_simple_scalar_or_list(part.strip().strip('"').strip("'")) for part in inner.split(",")]

    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        return value[1:-1]  # strip matching quotes for simple scalar strings

    return value


def render_frontmatter_text(data: dict[str, object]) -> str:
    lines = [f"Frontmatter keys: {len(data)}", ""]

    for key, value in data.items():
        lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")

    return "\n".join(lines).rstrip() + "\n"


def remove_frontmatter_block(text: str) -> str:
    _data, body = extract_frontmatter_block(text)
    return body if body.endswith("\n") else body + "\n"


def _compute_column_widths(rows: list[list[str]], headers: list[str], include_header: bool) -> list[int]:
    widths = [len(header) for header in headers]

    if not include_header:
        widths = [0 for _ in headers]  # width should still grow from row data

    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    return widths


def _pad_row(values: list[str], widths: list[int]) -> str:
    padded = [value.ljust(widths[index]) for index, value in enumerate(values)]
    return "| " + " | ".join(padded) + " |"


def convert_csv_to_markdown(
    csv_text: str,
    delimiter: str,
    quotechar: str,
    has_header: bool,
) -> str:
    import csv  # stdlib import kept local because only this tool needs it
    import io

    reader = csv.reader(io.StringIO(csv_text), delimiter=delimiter, quotechar=quotechar)
    raw_rows = [[cell.strip() for cell in row] for row in reader]

    if not raw_rows:
        raise ValueError("CSV input is empty")

    column_count = max(len(row) for row in raw_rows)
    rows = [row + [""] * (column_count - len(row)) for row in raw_rows]  # normalize row width for safe rendering

    if has_header:
        headers = rows[0]
        data_rows = rows[1:]
    else:
        headers = [f"col_{index + 1}" for index in range(column_count)]
        data_rows = rows

    widths = _compute_column_widths(data_rows, headers, include_header=True)
    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    lines = [_pad_row(headers, widths), separator]

    for row in data_rows:
        lines.append(_pad_row(row, widths))

    return "\n".join(lines).rstrip() + "\n"


def _deep_merge_dicts(base: dict[str, object], override: dict[str, object]) -> dict[str, object]:
    result: dict[str, object] = dict(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dicts(result[key], value)  # merge nested tables recursively
        else:
            result[key] = value  # override scalar or replace incompatible value types

    return result


def merge_toml_texts(base_text: str, override_text: str) -> str:
    try:
        import tomllib  # Python 3.11+ stdlib parser
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise RuntimeError("tomllib is not available in this Python runtime") from exc

    base_data = tomllib.loads(base_text)
    override_data = tomllib.loads(override_text)
    merged = _deep_merge_dicts(base_data, override_data)
    return dump_toml_text(merged)


def collect_codeblock_language_stats(text: str) -> dict[str, object]:
    pattern = re.compile(r"```([\w+-]*)\n(.*?)\n```", re.DOTALL)
    counts: dict[str, int] = {}
    unnamed = 0
    total = 0

    for match in pattern.finditer(text):
        total += 1
        language = match.group(1).strip().lower()

        if not language:
            unnamed += 1
            language = "<plain>"  # keep unnamed fences visible in output

        counts[language] = counts.get(language, 0) + 1

    ordered = dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
    return {"total_blocks": total, "unnamed_blocks": unnamed, "languages": ordered}


def render_codeblock_language_stats_text(stats: dict[str, object]) -> str:
    lines = [
        f"Total code blocks: {stats['total_blocks']}",
        f"Unnamed code blocks: {stats['unnamed_blocks']}",
        "",
        "Languages:",
    ]

    for language, count in stats["languages"].items():
        lines.append(f"{language} | {count}")

    return "\n".join(lines).rstrip() + "\n"


def cmd_frontmatter_extract(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    data, body = extract_frontmatter_block(source)

    if args.body_output:
        _write_text(Path(args.body_output), body if body.endswith("\n") else body + "\n", encoding=args.encoding)

    if args.format == "json":
        output = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_frontmatter_text(data)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0


def cmd_frontmatter_remove(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    source = _read_text(input_path, encoding=args.encoding)
    output = remove_frontmatter_block(source)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        _write_text(input_path, output, encoding=args.encoding)

    return 0


def cmd_csv_to_markdown(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    output = convert_csv_to_markdown(
        csv_text=source,
        delimiter=args.delimiter,
        quotechar=args.quotechar,
        has_header=not args.no_header,
    )

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0


def cmd_toml_merge(args: argparse.Namespace) -> int:
    base_text = _read_text(Path(args.base), encoding=args.encoding)
    override_text = _read_text(Path(args.override), encoding=args.encoding)
    output = merge_toml_texts(base_text, override_text)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0


def cmd_codeblock_language_stats(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    stats = collect_codeblock_language_stats(source)

    if args.format == "json":
        output = json.dumps(stats, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_codeblock_language_stats_text(stats)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def _collect_files_for_scan(
    root: Path,
    include_ext: set[str] | None,
    ignored_dirs: set[str],
    ignored_patterns: list[str],
    max_depth: int | None,
    include_hidden: bool,
    max_files: int | None,
) -> list[Path]:
    files: list[Path] = []
    root = root.resolve()

    for path in root.rglob("*"):
        rel_path = path.relative_to(root)
        parts = rel_path.parts

        if not parts:
            continue

        if not include_hidden and any(part.startswith(".") for part in parts):
            continue  # skip hidden files and folders by default

        if any(part in ignored_dirs for part in parts[:-1]):
            continue  # skip files inside ignored directories

        if max_depth is not None and len(parts) - 1 > max_depth:
            continue  # stop at the configured relative depth

        if _matches_any(str(rel_path), ignored_patterns):
            continue  # skip ignored path patterns

        if path.is_dir():
            continue

        if include_ext and path.suffix.lower() not in include_ext:
            continue

        files.append(path)

        if max_files is not None and len(files) >= max_files:
            break

    files.sort(key=lambda item: str(item).lower())
    return files



def _markdown_anchor_slug(title: str) -> str:
    anchor = re.sub(r"[^a-z0-9 -]", "", title.lower())  # keep slug close to common Markdown anchors
    anchor = anchor.replace(" ", "-")
    anchor = re.sub(r"-+", "-", anchor).strip("-")
    return anchor



def _extract_markdown_links(text: str) -> list[dict[str, object]]:
    pattern = re.compile(r'(!)?\[([^\]]*)\]\(([^)]+)\)')
    results: list[dict[str, object]] = []

    for match in pattern.finditer(text):
        is_image = bool(match.group(1))
        label = match.group(2)
        target = match.group(3).strip()
        lower_target = target.lower()

        if lower_target.startswith(("http://", "https://")):
            target_type = "external"
        elif lower_target.startswith("mailto:"):
            target_type = "email"
        elif target.startswith("#"):
            target_type = "anchor"
        else:
            target_type = "local"

        results.append(
            {
                "kind": "image" if is_image else "link",
                "label": label,
                "target": target,
                "target_type": target_type,
                "span_start": match.start(),
                "span_end": match.end(),
            }
        )

    return results



def _build_heading_anchor_set(text: str) -> set[str]:
    anchors: set[str] = set()

    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if not match:
            continue
        anchors.add(_markdown_anchor_slug(match.group(2).strip()))

    return anchors



def extract_markdown_links(text: str) -> list[dict[str, object]]:
    return _extract_markdown_links(text)



def render_markdown_links_text(entries: list[dict[str, object]]) -> str:
    lines = [f"Markdown links: {len(entries)}", ""]

    for entry in entries:
        lines.append(f"{entry['kind']} | {entry['target_type']} | {entry['label']} | {entry['target']}")

    return "\n".join(lines).rstrip() + "\n"



def check_markdown_links(input_path: Path, root: Path | None, encoding: str) -> list[dict[str, object]]:
    source = _read_text(input_path, encoding=encoding)
    links = _extract_markdown_links(source)
    base_dir = (root or input_path.parent).resolve()
    current_dir = input_path.resolve().parent
    current_anchors = _build_heading_anchor_set(source)
    results: list[dict[str, object]] = []

    for entry in links:
        target = str(entry["target"])
        target_type = str(entry["target_type"])
        status = "ok"
        detail = ""

        if target_type in {"external", "email"}:
            detail = "not_checked"  # external availability is intentionally not probed here
        elif target_type == "anchor":
            anchor = target[1:]
            if anchor not in current_anchors:
                status = "missing"
                detail = "anchor_not_found"
        else:
            path_part, sep, anchor_part = target.partition("#")
            candidate = (current_dir / path_part).resolve()

            if not candidate.exists() and not Path(path_part).is_absolute():
                alternative = (base_dir / path_part).resolve()
                if alternative.exists():
                    candidate = alternative  # optional root-based resolution for project files

            if not candidate.exists():
                status = "missing"
                detail = "file_not_found"
            elif sep and anchor_part:
                try:
                    target_text = _read_text(candidate, encoding=encoding)
                    anchors = _build_heading_anchor_set(target_text)
                    if anchor_part not in anchors:
                        status = "missing"
                        detail = "anchor_not_found"
                except Exception:
                    status = "warning"
                    detail = "anchor_not_checked"

        results.append(
            {
                "kind": entry["kind"],
                "target": target,
                "target_type": target_type,
                "status": status,
                "detail": detail,
            }
        )

    return results



def render_markdown_link_check_text(results: list[dict[str, object]]) -> str:
    issues = sum(1 for item in results if item["status"] != "ok")
    lines = [f"Checked links: {len(results)}", f"Issues: {issues}", ""]

    for item in results:
        lines.append(f"{item['status']} | {item['kind']} | {item['target_type']} | {item['target']} | {item['detail']}")

    return "\n".join(lines).rstrip() + "\n"



def build_file_hash_manifest(
    root: Path,
    include_ext: set[str] | None,
    ignored_dirs: set[str],
    ignored_patterns: list[str],
    max_depth: int | None,
    include_hidden: bool,
    max_files: int | None,
    algorithm: str,
) -> dict[str, object]:
    import hashlib

    files = _collect_files_for_scan(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=max_depth,
        include_hidden=include_hidden,
        max_files=max_files,
    )
    root = root.resolve()
    rows: list[dict[str, object]] = []

    for path in files:
        hasher = hashlib.new(algorithm)

        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)

        stat = path.stat()
        rows.append(
            {
                "path": str(path.relative_to(root)).replace("\\", "/"),
                "size": stat.st_size,
                "hash": hasher.hexdigest(),
            }
        )

    return {
        "root": str(root),
        "algorithm": algorithm,
        "files": len(rows),
        "entries": rows,
    }



def render_file_hash_manifest_text(manifest: dict[str, object]) -> str:
    lines = [
        f"File hash manifest for: {manifest['root']}",
        f"Algorithm: {manifest['algorithm']}",
        f"Files: {manifest['files']}",
        "",
    ]

    for entry in manifest["entries"]:
        lines.append(f"{entry['path']} | {entry['size']} | {entry['hash']}")

    return "\n".join(lines).rstrip() + "\n"



def find_duplicate_lines(text: str, ignore_case: bool, strip_ws: bool, skip_empty: bool) -> list[dict[str, object]]:
    seen: dict[str, dict[str, object]] = {}

    for line_number, line in enumerate(text.splitlines(), start=1):
        candidate = line.strip() if strip_ws else line
        if skip_empty and not candidate:
            continue
        key = candidate.lower() if ignore_case else candidate

        if key not in seen:
            seen[key] = {"value": candidate, "count": 0, "lines": []}

        seen[key]["count"] = int(seen[key]["count"]) + 1
        seen[key]["lines"].append(line_number)

    results = [item for item in seen.values() if int(item["count"]) > 1]
    results.sort(key=lambda item: (-int(item["count"]), str(item["value"])))
    return results



def render_duplicate_lines_text(results: list[dict[str, object]]) -> str:
    lines = [f"Duplicate lines: {len(results)}", ""]

    for item in results:
        line_list = ",".join(str(number) for number in item["lines"])
        lines.append(f"count={item['count']} | lines={line_list} | {item['value']}")

    return "\n".join(lines).rstrip() + "\n"



def markdown_word_count_by_heading(text: str) -> list[dict[str, object]]:
    lines = text.splitlines()
    matches: list[tuple[int, int, str]] = []

    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if not match:
            continue
        matches.append((index, len(match.group(1)), match.group(2).strip()))

    if not matches:
        return []

    results: list[dict[str, object]] = []

    for idx, (start_index, level, title) in enumerate(matches):
        end_index = len(lines)

        for next_index in range(idx + 1, len(matches)):
            if matches[next_index][1] <= level:
                end_index = matches[next_index][0]
                break  # stop at the next sibling or parent-level heading

        content = "\n".join(lines[start_index + 1 : end_index])
        words = re.findall(r"\b\w+\b", content, flags=re.UNICODE)
        results.append(
            {
                "line": start_index + 1,
                "level": level,
                "title": title,
                "word_count": len(words),
            }
        )

    return results



def render_markdown_word_counts_text(entries: list[dict[str, object]]) -> str:
    lines = [f"Headings counted: {len(entries)}", ""]

    for entry in entries:
        indent = "  " * (int(entry["level"]) - 1)
        lines.append(f"{indent}L{entry['line']} | H{entry['level']} | words={entry['word_count']} | {entry['title']}")

    return "\n".join(lines).rstrip() + "\n"



def diff_hash_manifests(base_manifest: dict[str, object], other_manifest: dict[str, object]) -> dict[str, object]:
    base_map = {str(entry["path"]): entry for entry in base_manifest.get("entries", [])}
    other_map = {str(entry["path"]): entry for entry in other_manifest.get("entries", [])}

    added = [other_map[path] for path in sorted(set(other_map) - set(base_map))]
    removed = [base_map[path] for path in sorted(set(base_map) - set(other_map))]
    changed: list[dict[str, object]] = []
    unchanged = 0

    for path in sorted(set(base_map) & set(other_map)):
        base_entry = base_map[path]
        other_entry = other_map[path]

        if base_entry.get("hash") == other_entry.get("hash") and base_entry.get("size") == other_entry.get("size"):
            unchanged += 1
            continue

        changed.append(
            {
                "path": path,
                "base_size": base_entry.get("size"),
                "other_size": other_entry.get("size"),
                "base_hash": base_entry.get("hash"),
                "other_hash": other_entry.get("hash"),
            }
        )

    return {
        "base_root": base_manifest.get("root", ""),
        "other_root": other_manifest.get("root", ""),
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }



def render_manifest_diff_text(diff: dict[str, object]) -> str:
    lines = [
        f"Base root: {diff['base_root']}",
        f"Other root: {diff['other_root']}",
        f"Added: {len(diff['added'])}",
        f"Removed: {len(diff['removed'])}",
        f"Changed: {len(diff['changed'])}",
        f"Unchanged: {diff['unchanged']}",
        "",
        "Added files:",
    ]

    for entry in diff["added"]:
        lines.append(f"+ {entry['path']} | {entry['size']} | {entry['hash']}")

    lines.append("")
    lines.append("Removed files:")

    for entry in diff["removed"]:
        lines.append(f"- {entry['path']} | {entry['size']} | {entry['hash']}")

    lines.append("")
    lines.append("Changed files:")

    for entry in diff["changed"]:
        lines.append(f"* {entry['path']} | {entry['base_size']} -> {entry['other_size']}")

    return "\n".join(lines).rstrip() + "\n"



def find_duplicate_files(
    root: Path,
    include_ext: set[str] | None,
    ignored_dirs: set[str],
    ignored_patterns: list[str],
    max_depth: int | None,
    include_hidden: bool,
    max_files: int | None,
    algorithm: str,
    min_size: int,
) -> list[dict[str, object]]:
    manifest = build_file_hash_manifest(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=max_depth,
        include_hidden=include_hidden,
        max_files=max_files,
        algorithm=algorithm,
    )
    groups: dict[tuple[int, str], list[dict[str, object]]] = {}

    for entry in manifest["entries"]:
        size = int(entry["size"])
        if size < min_size:
            continue
        key = (size, str(entry["hash"]))
        groups.setdefault(key, []).append(entry)

    results: list[dict[str, object]] = []

    for (size, file_hash), entries in groups.items():
        if len(entries) < 2:
            continue

        results.append(
            {
                "size": size,
                "hash": file_hash,
                "count": len(entries),
                "paths": [entry["path"] for entry in entries],
            }
        )

    results.sort(key=lambda item: (-int(item["count"]), -int(item["size"]), str(item["hash"])))
    return results



def render_duplicate_files_text(results: list[dict[str, object]]) -> str:
    lines = [f"Duplicate groups: {len(results)}", ""]

    for item in results:
        lines.append(f"count={item['count']} | size={item['size']} | hash={item['hash']}")
        for path in item["paths"]:
            lines.append(f"  {path}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"



def _flatten_mapping(data: dict[str, object], prefix: str = "") -> dict[str, object]:
    result: dict[str, object] = {}

    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(_flatten_mapping(value, prefix=full_key))
        else:
            result[full_key] = value

    return result



def flatten_toml_keys(text: str) -> dict[str, object]:
    try:
        import tomllib
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise RuntimeError("tomllib is not available in this Python runtime") from exc

    data = tomllib.loads(text)
    return dict(sorted(_flatten_mapping(data).items(), key=lambda item: item[0]))



def render_flattened_mapping_text(data: dict[str, object]) -> str:
    lines = [f"Flattened keys: {len(data)}", ""]

    for key, value in data.items():
        lines.append(f"{key} = {json.dumps(value, ensure_ascii=False)}")

    return "\n".join(lines).rstrip() + "\n"



def _format_toml_scalar(value: object) -> str:
    if value is None:
        return '""'  # keep null-like values safely representable

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    if isinstance(value, list):
        return "[" + ", ".join(_format_toml_scalar(item) for item in value) + "]"

    raise TypeError(f"Unsupported TOML value type: {type(value).__name__}")



def _dump_toml_table(data: dict[str, object], prefix: str | None = None) -> list[str]:
    lines: list[str] = []
    scalar_items: list[tuple[str, object]] = []
    table_items: list[tuple[str, dict[str, object]]] = []
    array_table_items: list[tuple[str, list[dict[str, object]]]] = []

    for key, value in data.items():
        if isinstance(value, dict):
            table_items.append((key, value))
        elif isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            array_table_items.append((key, value))
        else:
            scalar_items.append((key, value))

    for key, value in scalar_items:
        lines.append(f"{key} = {_format_toml_scalar(value)}")

    if scalar_items and (table_items or array_table_items):
        lines.append("")  # keep nested sections visually separated

    for index, (key, value) in enumerate(table_items):
        full_name = f"{prefix}.{key}" if prefix else key
        lines.append(f"[{full_name}]")
        lines.extend(_dump_toml_table(value, prefix=full_name))

        if index < len(table_items) - 1 or array_table_items:
            lines.append("")

    for outer_index, (key, items) in enumerate(array_table_items):
        full_name = f"{prefix}.{key}" if prefix else key

        for inner_index, item in enumerate(items):
            lines.append(f"[[{full_name}]]")
            lines.extend(_dump_toml_table(item, prefix=full_name))

            if inner_index < len(items) - 1 or outer_index < len(array_table_items) - 1:
                lines.append("")

    return lines



def dump_toml_text(data: dict[str, object]) -> str:
    if not isinstance(data, dict):
        raise TypeError("Top-level TOML document must be a JSON object")

    lines = _dump_toml_table(data)
    return "\n".join(lines).rstrip() + "\n"



def convert_json_to_toml(json_text: str) -> str:
    data = json.loads(json_text)

    if not isinstance(data, dict):
        raise TypeError("Top-level JSON value must be an object for TOML conversion")

    return dump_toml_text(data)



def cmd_markdown_link_extract(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    entries = extract_markdown_links(source)

    if args.format == "json":
        output = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_markdown_links_text(entries)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_markdown_link_check(args: argparse.Namespace) -> int:
    results = check_markdown_links(
        input_path=Path(args.input),
        root=Path(args.root) if args.root else None,
        encoding=args.encoding,
    )

    if args.only_issues:
        results = [item for item in results if item["status"] != "ok"]

    if args.format == "json":
        output = json.dumps(results, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_markdown_link_check_text(results)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_file_hash_manifest(args: argparse.Namespace) -> int:
    root = Path(args.root)
    include_ext = _parse_extensions(args.ext)
    ignored_dirs = DEFAULT_IGNORED_DIRS | set(_parse_comma_list(args.ignore_dir))
    ignored_patterns = _parse_comma_list(args.ignore)
    manifest = build_file_hash_manifest(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=args.max_depth,
        include_hidden=args.include_hidden,
        max_files=args.max_files,
        algorithm=args.algorithm,
    )

    if args.format == "json":
        output = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_file_hash_manifest_text(manifest)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_duplicate_line_finder(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    results = find_duplicate_lines(
        text=source,
        ignore_case=args.ignore_case,
        strip_ws=args.strip_ws,
        skip_empty=args.skip_empty,
    )

    if args.format == "json":
        output = json.dumps(results, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_duplicate_lines_text(results)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_markdown_word_count_by_heading(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    entries = markdown_word_count_by_heading(source)

    if args.format == "json":
        output = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_markdown_word_counts_text(entries)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_manifest_diff(args: argparse.Namespace) -> int:
    base_manifest = json.loads(_read_text(Path(args.base), encoding=args.encoding))
    other_manifest = json.loads(_read_text(Path(args.other), encoding=args.encoding))
    diff = diff_hash_manifests(base_manifest, other_manifest)

    if args.format == "json":
        output = json.dumps(diff, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_manifest_diff_text(diff)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_duplicate_file_finder(args: argparse.Namespace) -> int:
    root = Path(args.root)
    include_ext = _parse_extensions(args.ext)
    ignored_dirs = DEFAULT_IGNORED_DIRS | set(_parse_comma_list(args.ignore_dir))
    ignored_patterns = _parse_comma_list(args.ignore)
    results = find_duplicate_files(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=args.max_depth,
        include_hidden=args.include_hidden,
        max_files=args.max_files,
        algorithm=args.algorithm,
        min_size=args.min_size,
    )

    if args.format == "json":
        output = json.dumps(results, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_duplicate_files_text(results)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_toml_key_flatten(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    data = flatten_toml_keys(source)

    if args.format == "json":
        output = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_flattened_mapping_text(data)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def cmd_json_to_toml(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    output = convert_json_to_toml(source)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



def _classify_target_type(target: str) -> str:
    lower_target = target.lower()

    if lower_target.startswith(("http://", "https://")):
        return "external"

    if lower_target.startswith("mailto:"):
        return "email"

    if target.startswith("#"):
        return "anchor"

    return "local"


def _extract_markdown_image_entries(text: str) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []

    pattern_md = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    pattern_html = re.compile(r"<img\b([^>]*)>", flags=re.IGNORECASE)

    for match in pattern_md.finditer(text):
        alt_text = match.group(1).strip()
        target = match.group(2).strip()
        results.append(
            {
                "kind": "markdown_image",
                "alt": alt_text,
                "target": target,
                "target_type": _classify_target_type(target),
            }
        )

    for match in pattern_html.finditer(text):
        attrs = match.group(1)
        src_match = re.search(r'''src\s*=\s*["']([^"']+)["']''', attrs, flags=re.IGNORECASE)
        if not src_match:
            continue  # skip img tags without a usable src attribute

        alt_match = re.search(r'''alt\s*=\s*["']([^"']*)["']''', attrs, flags=re.IGNORECASE)
        target = src_match.group(1).strip()
        alt_text = alt_match.group(1).strip() if alt_match else ""
        results.append(
            {
                "kind": "html_image",
                "alt": alt_text,
                "target": target,
                "target_type": _classify_target_type(target),
            }
        )

    return results


def _resolve_local_target(base_file: Path, root: Path | None, target: str) -> bool | None:
    if _classify_target_type(target) != "local":
        return None  # only local file existence can be checked safely here

    path_part = target.partition("#")[0].strip()
    if not path_part:
        return None  # empty local target is not treated as a file path

    candidate = (base_file.parent / path_part).resolve()
    if candidate.exists():
        return True

    if root is not None:
        alternative = (root.resolve() / path_part).resolve()
        if alternative.exists():
            return True

    return False


def collect_markdown_image_inventory(
    files: list[Path],
    root: Path | None,
    encoding: str,
    verify_local: bool,
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    root_resolved = root.resolve() if root is not None else None

    for path in files:
        source = _read_text(path, encoding=encoding)
        entries = _extract_markdown_image_entries(source)

        for entry in entries:
            local_exists = _resolve_local_target(path, root_resolved, str(entry["target"])) if verify_local else None

            if root_resolved is not None:
                source_path = str(path.resolve().relative_to(root_resolved)).replace("\\", "/")
            else:
                source_path = str(path)

            results.append(
                {
                    "source_path": source_path,
                    "kind": entry["kind"],
                    "alt": entry["alt"],
                    "target": entry["target"],
                    "target_type": entry["target_type"],
                    "local_exists": local_exists,
                }
            )

    return results


def render_markdown_image_inventory_text(entries: list[dict[str, object]]) -> str:
    lines = [f"Markdown images: {len(entries)}", ""]

    for entry in entries:
        exists_text = "n/a" if entry["local_exists"] is None else ("yes" if entry["local_exists"] else "no")
        lines.append(
            f"{entry['source_path']} | {entry['kind']} | {entry['target_type']} | exists={exists_text} | alt={entry['alt']} | {entry['target']}"
        )

    return "\n".join(lines).rstrip() + "\n"


def _transform_filename_stem(
    stem: str,
    find_text: str | None,
    replace_text: str,
    regex_pattern: str | None,
    prefix: str | None,
    suffix: str | None,
    lowercase: bool,
    slugify: bool,
) -> str:
    updated = stem

    if find_text:
        updated = updated.replace(find_text, replace_text)  # simple literal rename step

    if regex_pattern:
        updated = re.sub(regex_pattern, replace_text, updated)  # regex rename step

    if prefix:
        updated = prefix + updated

    if suffix:
        updated = updated + suffix

    if lowercase:
        updated = updated.lower()

    if slugify:
        updated = _sanitize_filename(updated)  # normalize to a safer filename stem

    return updated


def _build_safe_batch_rename_plan(
    root: Path,
    include_ext: set[str] | None,
    ignored_dirs: set[str],
    ignored_patterns: list[str],
    max_depth: int | None,
    include_hidden: bool,
    max_files: int | None,
    find_text: str | None,
    replace_text: str,
    regex_pattern: str | None,
    prefix: str | None,
    suffix: str | None,
    lowercase: bool,
    slugify: bool,
    lowercase_extension: bool,
) -> list[dict[str, object]]:
    files = _collect_files_for_scan(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=max_depth,
        include_hidden=include_hidden,
        max_files=max_files,
    )
    root = root.resolve()
    plan: list[dict[str, object]] = []
    planned_targets: dict[str, int] = {}

    for path in files:
        stem = path.stem
        suffix_text = path.suffix.lower() if lowercase_extension else path.suffix
        new_stem = _transform_filename_stem(
            stem=stem,
            find_text=find_text,
            replace_text=replace_text,
            regex_pattern=regex_pattern,
            prefix=prefix,
            suffix=suffix,
            lowercase=lowercase,
            slugify=slugify,
        )
        new_name = new_stem + suffix_text

        if new_name == path.name:
            continue  # skip unchanged filenames

        target_path = path.with_name(new_name)
        rel_source = str(path.relative_to(root)).replace("\\", "/")
        rel_target = str(target_path.relative_to(root)).replace("\\", "/")
        planned_targets[rel_target] = planned_targets.get(rel_target, 0) + 1

        plan.append(
            {
                "source_path": rel_source,
                "target_path": rel_target,
                "source_abs": str(path),
                "target_abs": str(target_path),
                "status": "pending",
                "detail": "",
            }
        )

    existing_sources = {item["source_path"] for item in plan}

    for item in plan:
        target_abs = Path(str(item["target_abs"]))
        target_rel = str(item["target_path"])

        if planned_targets[target_rel] > 1:
            item["status"] = "conflict"
            item["detail"] = "duplicate_target"
            continue

        if target_abs.exists() and target_rel not in existing_sources:
            item["status"] = "conflict"
            item["detail"] = "target_exists"
            continue

        if target_rel in existing_sources:
            item["status"] = "conflict"
            item["detail"] = "rename_cycle"
            continue

        item["status"] = "ready"
        item["detail"] = "ok"

    return plan


def apply_safe_batch_rename(plan: list[dict[str, object]]) -> int:
    renamed = 0

    for item in plan:
        if item["status"] != "ready":
            continue

        source_path = Path(str(item["source_abs"]))
        target_path = Path(str(item["target_abs"]))
        source_path.rename(target_path)
        renamed += 1

    return renamed


def render_safe_batch_rename_text(plan: list[dict[str, object]], apply_mode: bool) -> str:
    mode = "Apply" if apply_mode else "Preview"
    ready = sum(1 for item in plan if item["status"] == "ready")
    conflicts = sum(1 for item in plan if item["status"] == "conflict")
    lines = [f"{mode} batch rename", f"Planned renames: {len(plan)}", f"Ready: {ready}", f"Conflicts: {conflicts}", ""]

    for item in plan:
        lines.append(f"{item['status']} | {item['source_path']} -> {item['target_path']} | {item['detail']}")

    return "\n".join(lines).rstrip() + "\n"


def build_text_frequency_report(
    text: str,
    mode: str,
    ignore_case: bool,
    strip_ws: bool,
    min_length: int,
    min_count: int,
    top_n: int | None,
) -> list[dict[str, object]]:
    from collections import Counter  # local import keeps top-level file stable

    if mode == "word":
        tokens = re.findall(r"\b\w+\b", text, flags=re.UNICODE)
    elif mode == "token":
        tokens = text.split()
    elif mode == "line":
        tokens = text.splitlines()
    else:
        raise ValueError(f"Unsupported frequency mode: {mode}")

    prepared: list[str] = []

    for token in tokens:
        item = token.strip() if strip_ws else token

        if not item:
            continue

        if ignore_case:
            item = item.lower()

        if len(item) < min_length:
            continue

        prepared.append(item)

    counter = Counter(prepared)
    rows = [
        {"item": key, "count": value}
        for key, value in sorted(counter.items(), key=lambda pair: (-pair[1], pair[0]))
        if value >= min_count
    ]

    if top_n is not None:
        rows = rows[:top_n]

    return rows


def render_text_frequency_report_text(mode: str, rows: list[dict[str, object]]) -> str:
    lines = [f"Frequency report mode: {mode}", f"Rows: {len(rows)}", ""]

    for row in rows:
        lines.append(f"{row['count']} | {row['item']}")

    return "\n".join(lines).rstrip() + "\n"


def generate_markdown_toc(
    text: str,
    min_level: int,
    max_level: int,
    skip_first_h1: bool,
) -> str:
    entries = build_markdown_heading_index(text)
    lines: list[str] = []
    first_h1_skipped = False

    for entry in entries:
        level = int(entry["level"])

        if level < min_level or level > max_level:
            continue

        if skip_first_h1 and not first_h1_skipped and level == 1:
            first_h1_skipped = True
            continue  # optionally keep the document title out of the TOC

        indent = "  " * (level - min_level)
        lines.append(f"{indent}- [{entry['title']}](#{entry['anchor']})")

    return "\n".join(lines).rstrip() + "\n"


def _flatten_json_value(value: object, prefix: str, output: dict[str, object]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            full_key = f"{prefix}.{key}" if prefix else key
            _flatten_json_value(child, full_key, output)
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            full_key = f"{prefix}[{index}]"
            _flatten_json_value(child, full_key, output)
        if not value and prefix:
            output[prefix] = []  # keep empty arrays visible in flattened output
        return

    output[prefix] = value


def flatten_json_keys(json_text: str) -> dict[str, object]:
    data = json.loads(json_text)
    output: dict[str, object] = {}

    if not isinstance(data, dict):
        raise TypeError("Top-level JSON value must be an object")

    _flatten_json_value(data, "", output)
    return dict(sorted(output.items(), key=lambda item: item[0]))


def filter_unique_lines(
    text: str,
    ignore_case: bool,
    strip_ws: bool,
    skip_empty: bool,
    sort_output: bool,
) -> str:
    seen: set[str] = set()
    kept: list[str] = []

    for raw_line in text.splitlines():
        compare_value = raw_line.strip() if strip_ws else raw_line

        if skip_empty and not compare_value:
            continue

        key = compare_value.lower() if ignore_case else compare_value

        if key in seen:
            continue

        seen.add(key)
        kept.append(compare_value if strip_ws else raw_line)

    if sort_output:
        kept.sort(key=lambda item: item.lower() if ignore_case else item)

    return "\n".join(kept).rstrip() + "\n"


def _normalize_path_prefix(value: str, slash_style: str) -> str:
    if slash_style == "posix":
        return value.replace("\\", "/")

    if slash_style == "windows":
        return value.replace("/", "\\")

    return value


def rewrite_path_prefixes_in_text(
    text: str,
    from_prefix: str,
    to_prefix: str,
    slash_style: str,
    case_sensitive: bool,
) -> tuple[str, int]:
    normalized_to = _normalize_path_prefix(to_prefix, slash_style)
    search_variants = {from_prefix}

    if "/" in from_prefix or "\\" in from_prefix:
        search_variants.add(from_prefix.replace("\\", "/"))
        search_variants.add(from_prefix.replace("/", "\\"))

    updated = text
    total_replacements = 0

    for variant in sorted(search_variants, key=len, reverse=True):
        if case_sensitive:
            count = updated.count(variant)
            if count:
                updated = updated.replace(variant, normalized_to)
                total_replacements += count
        else:
            updated, count = re.subn(re.escape(variant), normalized_to, updated, flags=re.IGNORECASE)
            total_replacements += count

    return updated, total_replacements


def apply_path_rewrite(
    root: Path,
    include_ext: set[str] | None,
    ignored_dirs: set[str],
    ignored_patterns: list[str],
    max_depth: int | None,
    include_hidden: bool,
    max_files: int | None,
    from_prefix: str,
    to_prefix: str,
    slash_style: str,
    case_sensitive: bool,
    encoding: str,
    create_backup: bool,
    dry_run: bool,
) -> list[dict[str, object]]:
    files = _collect_text_files(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=max_depth,
        include_hidden=include_hidden,
        max_files=max_files,
    )
    root = root.resolve()
    results: list[dict[str, object]] = []

    for path in files:
        source = _read_text(path, encoding=encoding)
        updated, replacements = rewrite_path_prefixes_in_text(
            text=source,
            from_prefix=from_prefix,
            to_prefix=to_prefix,
            slash_style=slash_style,
            case_sensitive=case_sensitive,
        )

        if replacements <= 0:
            continue

        rel_path = str(path.relative_to(root)).replace("\\", "/")
        results.append({"path": rel_path, "replacements": replacements})

        if dry_run:
            continue  # preview mode only

        if create_backup:
            backup_path = path.with_suffix(path.suffix + ".bak")
            _write_text(backup_path, source, encoding=encoding)

        _write_text(path, updated, encoding=encoding)

    return results


def build_slugify_batch_plan(
    root: Path,
    include_ext: set[str] | None,
    ignored_dirs: set[str],
    ignored_patterns: list[str],
    max_depth: int | None,
    include_hidden: bool,
    max_files: int | None,
    lowercase_extension: bool,
    dedupe: bool,
) -> list[dict[str, object]]:
    files = _collect_files_for_scan(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=max_depth,
        include_hidden=include_hidden,
        max_files=max_files,
    )
    root = root.resolve()
    plan: list[dict[str, object]] = []
    used_targets: set[str] = set()

    for path in files:
        suffix_text = path.suffix.lower() if lowercase_extension else path.suffix
        base_stem = _sanitize_filename(path.stem)
        new_name = base_stem + suffix_text
        counter = 2

        while dedupe and new_name in used_targets:
            new_name = f"{base_stem}_{counter}{suffix_text}"
            counter += 1  # keep target names unique inside the batch plan

        rel_source = str(path.relative_to(root)).replace("\\", "/")
        rel_target = str(path.with_name(new_name).relative_to(root)).replace("\\", "/")
        used_targets.add(new_name)

        if new_name == path.name:
            continue  # skip unchanged filenames

        status = "ready"
        detail = "ok"
        target_abs = path.with_name(new_name)

        if target_abs.exists():
            status = "conflict"
            detail = "target_exists"

        plan.append(
            {
                "source_path": rel_source,
                "target_path": rel_target,
                "source_abs": str(path),
                "target_abs": str(target_abs),
                "status": status,
                "detail": detail,
            }
        )

    return plan


def apply_slugify_batch_plan(plan: list[dict[str, object]]) -> int:
    renamed = 0

    for item in plan:
        if item["status"] != "ready":
            continue

        Path(str(item["source_abs"])).rename(Path(str(item["target_abs"])))
        renamed += 1

    return renamed


def render_slugify_batch_text(plan: list[dict[str, object]], apply_mode: bool) -> str:
    mode = "Apply" if apply_mode else "Preview"
    ready = sum(1 for item in plan if item["status"] == "ready")
    conflicts = sum(1 for item in plan if item["status"] == "conflict")
    lines = [f"{mode} filename slugify batch", f"Planned renames: {len(plan)}", f"Ready: {ready}", f"Conflicts: {conflicts}", ""]

    for item in plan:
        lines.append(f"{item['status']} | {item['source_path']} -> {item['target_path']} | {item['detail']}")

    return "\n".join(lines).rstrip() + "\n"


def cmd_markdown_image_inventory(args: argparse.Namespace) -> int:
    if args.input:
        files = [Path(args.input)]
        root = None
    else:
        root = Path(args.root)
        include_ext = _parse_extensions(args.ext) or {".md", ".markdown"}
        ignored_dirs = DEFAULT_IGNORED_DIRS | set(_parse_comma_list(args.ignore_dir))
        ignored_patterns = _parse_comma_list(args.ignore)
        files = _collect_files_for_scan(
            root=root,
            include_ext=include_ext,
            ignored_dirs=ignored_dirs,
            ignored_patterns=ignored_patterns,
            max_depth=args.max_depth,
            include_hidden=args.include_hidden,
            max_files=args.max_files,
        )

    entries = collect_markdown_image_inventory(
        files=files,
        root=root,
        encoding=args.encoding,
        verify_local=not args.no_verify_local,
    )

    if args.format == "json":
        output = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_markdown_image_inventory_text(entries)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0


def cmd_safe_batch_rename(args: argparse.Namespace) -> int:
    root = Path(args.root)
    include_ext = _parse_extensions(args.ext)
    ignored_dirs = DEFAULT_IGNORED_DIRS | set(_parse_comma_list(args.ignore_dir))
    ignored_patterns = _parse_comma_list(args.ignore)
    plan = _build_safe_batch_rename_plan(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=args.max_depth,
        include_hidden=args.include_hidden,
        max_files=args.max_files,
        find_text=args.find,
        replace_text=args.replace,
        regex_pattern=args.regex,
        prefix=args.prefix,
        suffix=args.suffix,
        lowercase=args.lowercase,
        slugify=args.slugify,
        lowercase_extension=args.lowercase_extension,
    )

    if args.apply:
        apply_safe_batch_rename(plan)

    if args.format == "json":
        output = json.dumps(plan, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_safe_batch_rename_text(plan, apply_mode=args.apply)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0


def cmd_text_frequency_report(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    rows = build_text_frequency_report(
        text=source,
        mode=args.mode,
        ignore_case=args.ignore_case,
        strip_ws=args.strip_ws,
        min_length=args.min_length,
        min_count=args.min_count,
        top_n=args.top_n,
    )

    if args.format == "json":
        output = json.dumps(rows, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_text_frequency_report_text(args.mode, rows)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0


def cmd_markdown_toc_generate(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    output = generate_markdown_toc(
        text=source,
        min_level=args.min_level,
        max_level=args.max_level,
        skip_first_h1=args.skip_first_h1,
    )

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0


def cmd_json_key_flatten(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    data = flatten_json_keys(source)

    if args.format == "json":
        output = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_flattened_mapping_text(data)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0


def cmd_unique_line_filter(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    output = filter_unique_lines(
        text=source,
        ignore_case=args.ignore_case,
        strip_ws=args.strip_ws,
        skip_empty=args.skip_empty,
        sort_output=args.sort_output,
    )

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0


def cmd_path_rewrite(args: argparse.Namespace) -> int:
    root = Path(args.root)
    include_ext = _parse_extensions(args.ext)
    ignored_dirs = DEFAULT_IGNORED_DIRS | set(_parse_comma_list(args.ignore_dir))
    ignored_patterns = _parse_comma_list(args.ignore)
    results = apply_path_rewrite(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=args.max_depth,
        include_hidden=args.include_hidden,
        max_files=args.max_files,
        from_prefix=args.from_prefix,
        to_prefix=args.to_prefix,
        slash_style=args.slash_style,
        case_sensitive=args.case_sensitive,
        encoding=args.encoding,
        create_backup=args.create_backup,
        dry_run=not args.apply,
    )

    if args.format == "json":
        output = json.dumps(results, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_replace_results_text(root, results, dry_run=not args.apply)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0


def cmd_filename_slugify_batch(args: argparse.Namespace) -> int:
    root = Path(args.root)
    include_ext = _parse_extensions(args.ext)
    ignored_dirs = DEFAULT_IGNORED_DIRS | set(_parse_comma_list(args.ignore_dir))
    ignored_patterns = _parse_comma_list(args.ignore)
    plan = build_slugify_batch_plan(
        root=root,
        include_ext=include_ext,
        ignored_dirs=ignored_dirs,
        ignored_patterns=ignored_patterns,
        max_depth=args.max_depth,
        include_hidden=args.include_hidden,
        max_files=args.max_files,
        lowercase_extension=args.lowercase_extension,
        dedupe=args.dedupe,
    )

    if args.apply:
        apply_slugify_batch_plan(plan)

    if args.format == "json":
        output = json.dumps(plan, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_slugify_batch_text(plan, apply_mode=args.apply)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0



# Add new helper functions and cmd_* handlers above this section.
# Add new CLI subparser definitions inside build_parser() before 'return parser'.


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compact Python helper toolkit for recurring project tasks."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_index = subparsers.add_parser("project-index", help="Create a lightweight file index.")
    p_index.add_argument("--root", required=True, help="Project root directory.")
    p_index.add_argument("--ext", action="append", help="Include only these extensions, comma-separated or repeated.")
    p_index.add_argument("--ignore-dir", action="append", help="Additional directory names to ignore.")
    p_index.add_argument("--ignore", action="append", help="Ignore path patterns, e.g. '*.log,cache/*'.")
    p_index.add_argument("--max-depth", type=int, help="Maximum relative depth.")
    p_index.add_argument("--max-files", type=int, help="Stop after N files.")
    p_index.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    p_index.add_argument("--format", choices=["text", "json"], default="text")
    p_index.add_argument("--output", help="Optional output file.")
    p_index.set_defaults(func=cmd_project_index)

    p_section = subparsers.add_parser("extract-section", help="Extract a Markdown section by heading.")
    p_section.add_argument("--input", required=True, help="Markdown file.")
    p_section.add_argument("--heading", required=True, help="Exact heading text without #.")
    p_section.add_argument("--output", help="Optional output file.")
    p_section.add_argument("--encoding", default="utf-8")
    p_section.set_defaults(func=cmd_extract_section)

    p_code = subparsers.add_parser("extract-codeblocks", help="Extract fenced code blocks from Markdown.")
    p_code.add_argument("--input", required=True, help="Markdown file.")
    p_code.add_argument("--language", help="Filter by code fence language.")
    p_code.add_argument("--index", type=int, default=1, help="1-based block index when not using --all.")
    p_code.add_argument("--all", action="store_true", help="Output all matching blocks combined.")
    p_code.add_argument("--output", help="Optional output file.")
    p_code.add_argument("--output-dir", help="Write each block as a separate file.")
    p_code.add_argument("--extension", help="Extension used with --output-dir.")
    p_code.add_argument("--encoding", default="utf-8")
    p_code.set_defaults(func=cmd_extract_codeblocks)

    p_replace = subparsers.add_parser("replace-between-markers", help="Replace text between two markers.")
    p_replace.add_argument("--input", required=True, help="Target file.")
    p_replace.add_argument("--start-marker", required=True)
    p_replace.add_argument("--end-marker", required=True)
    p_replace.add_argument("--replacement-text", help="Replacement text passed directly on the CLI.")
    p_replace.add_argument("--replacement-file", help="Read replacement text from this file.")
    p_replace.add_argument("--output", help="Optional output file. If omitted, input file is overwritten.")
    p_replace.add_argument("--encoding", default="utf-8")
    p_replace.set_defaults(func=cmd_replace_between_markers)

    p_ini = subparsers.add_parser("ini-to-toml", help="Convert a simple INI file to TOML.")
    p_ini.add_argument("--input", required=True, help="INI input file.")
    p_ini.add_argument("--output", help="Optional TOML output file.")
    p_ini.add_argument("--encoding", default="utf-8")
    p_ini.set_defaults(func=cmd_ini_to_toml)

    p_norm = subparsers.add_parser("normalize-text", help="Normalize line endings and whitespace.")
    p_norm.add_argument("--input", required=True, help="Input text file.")
    p_norm.add_argument("--output", help="Optional output file. If omitted, input file is overwritten.")
    p_norm.add_argument("--line-ending", choices=["lf", "crlf"], default="lf")
    p_norm.add_argument("--keep-trailing-ws", action="store_true", help="Keep trailing whitespace.")
    p_norm.add_argument("--no-final-newline", action="store_true", help="Do not force a final newline.")
    p_norm.add_argument("--expand-tabs", type=int, help="Expand tabs to spaces using this tab size.")
    p_norm.add_argument("--encoding", default="utf-8")
    p_norm.set_defaults(func=cmd_normalize_text)

    p_json = subparsers.add_parser("json-pretty", help="Validate and pretty-print JSON.")
    p_json.add_argument("--input", required=True, help="JSON input file.")
    p_json.add_argument("--output", help="Optional output file.")
    p_json.add_argument("--indent", type=int, default=2)
    p_json.add_argument("--sort-keys", action="store_true")
    p_json.add_argument("--ensure-ascii", action="store_true")
    p_json.add_argument("--encoding", default="utf-8")
    p_json.set_defaults(func=cmd_json_pretty)

    p_find = subparsers.add_parser("find-text", help="Find text matches across files.")
    p_find.add_argument("--root", required=True, help="Root directory to scan.")
    p_find.add_argument("--query", required=True, help="Literal text or regex pattern to find.")
    p_find.add_argument("--ext", action="append", help="Include only these extensions, comma-separated or repeated.")
    p_find.add_argument("--ignore-dir", action="append", help="Additional directory names to ignore.")
    p_find.add_argument("--ignore", action="append", help="Ignore path patterns, e.g. '*.log,cache/*'.")
    p_find.add_argument("--max-depth", type=int, help="Maximum relative depth.")
    p_find.add_argument("--max-files", type=int, help="Stop scanning after N files.")
    p_find.add_argument("--max-matches", type=int, help="Stop after N total matches.")
    p_find.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    p_find.add_argument("--regex", action="store_true", help="Treat --query as a regular expression.")
    p_find.add_argument("--case-sensitive", action="store_true", help="Use case-sensitive matching.")
    p_find.add_argument("--format", choices=["text", "json"], default="text")
    p_find.add_argument("--output", help="Optional output file.")
    p_find.add_argument("--encoding", default="utf-8")
    p_find.set_defaults(func=cmd_find_text)

    p_replace = subparsers.add_parser("safe-search-replace", help="Replace text across files with dry-run support.")
    p_replace.add_argument("--root", required=True, help="Root directory to scan.")
    p_replace.add_argument("--query", required=True, help="Literal text or regex pattern to replace.")
    p_replace.add_argument("--replacement", required=True, help="Replacement text.")
    p_replace.add_argument("--ext", action="append", help="Include only these extensions, comma-separated or repeated.")
    p_replace.add_argument("--ignore-dir", action="append", help="Additional directory names to ignore.")
    p_replace.add_argument("--ignore", action="append", help="Ignore path patterns, e.g. '*.log,cache/*'.")
    p_replace.add_argument("--max-depth", type=int, help="Maximum relative depth.")
    p_replace.add_argument("--max-files", type=int, help="Stop scanning after N files.")
    p_replace.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    p_replace.add_argument("--regex", action="store_true", help="Treat --query as a regular expression.")
    p_replace.add_argument("--case-sensitive", action="store_true", help="Use case-sensitive matching.")
    p_replace.add_argument("--dry-run", action="store_true", help="Only report changes without writing files.")
    p_replace.add_argument("--create-backup", action="store_true", help="Write .bak files before modifying originals.")
    p_replace.add_argument("--format", choices=["text", "json"], default="text")
    p_replace.add_argument("--output", help="Optional report file.")
    p_replace.add_argument("--encoding", default="utf-8")
    p_replace.set_defaults(func=cmd_safe_search_replace)

    p_heading = subparsers.add_parser("md-heading-index", help="Build a Markdown heading index.")
    p_heading.add_argument("--input", required=True, help="Markdown input file.")
    p_heading.add_argument("--format", choices=["text", "json"], default="text")
    p_heading.add_argument("--output", help="Optional output file.")
    p_heading.add_argument("--encoding", default="utf-8")
    p_heading.set_defaults(func=cmd_md_heading_index)

    p_split = subparsers.add_parser("split-markdown-sections", help="Split a Markdown file into heading-based section files.")
    p_split.add_argument("--input", required=True, help="Markdown input file.")
    p_split.add_argument("--level", type=int, default=2, help="Heading level to split on, e.g. 2 for ##.")
    p_split.add_argument("--output-dir", required=True, help="Target directory for section files.")
    p_split.add_argument("--prefix", help="Optional filename prefix.")
    p_split.add_argument("--encoding", default="utf-8")
    p_split.set_defaults(func=cmd_split_markdown_sections)

    p_manifest = subparsers.add_parser("project-manifest", help="Create a compact project manifest.")
    p_manifest.add_argument("--root", required=True, help="Project root directory.")
    p_manifest.add_argument("--ext", action="append", help="Include only these extensions, comma-separated or repeated.")
    p_manifest.add_argument("--ignore-dir", action="append", help="Additional directory names to ignore.")
    p_manifest.add_argument("--ignore", action="append", help="Ignore path patterns, e.g. '*.log,cache/*'.")
    p_manifest.add_argument("--max-depth", type=int, help="Maximum relative depth.")
    p_manifest.add_argument("--max-files", type=int, help="Stop scanning after N files.")
    p_manifest.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    p_manifest.add_argument("--top-n", type=int, default=10, help="Number of largest files to include.")
    p_manifest.add_argument("--format", choices=["text", "json"], default="text")
    p_manifest.add_argument("--output", help="Optional output file.")
    p_manifest.add_argument("--encoding", default="utf-8")
    p_manifest.set_defaults(func=cmd_project_manifest)

    p_frontmatter = subparsers.add_parser("frontmatter-extract", help="Extract a simple frontmatter block from Markdown.")
    p_frontmatter.add_argument("--input", required=True, help="Markdown input file.")
    p_frontmatter.add_argument("--format", choices=["text", "json"], default="json")
    p_frontmatter.add_argument("--output", help="Optional frontmatter output file.")
    p_frontmatter.add_argument("--body-output", help="Optional output file for the Markdown body without frontmatter.")
    p_frontmatter.add_argument("--encoding", default="utf-8")
    p_frontmatter.set_defaults(func=cmd_frontmatter_extract)

    p_frontmatter_remove = subparsers.add_parser("frontmatter-remove", help="Remove a leading frontmatter block from Markdown.")
    p_frontmatter_remove.add_argument("--input", required=True, help="Markdown input file.")
    p_frontmatter_remove.add_argument("--output", help="Optional output file. If omitted, input file is overwritten.")
    p_frontmatter_remove.add_argument("--encoding", default="utf-8")
    p_frontmatter_remove.set_defaults(func=cmd_frontmatter_remove)

    p_csv = subparsers.add_parser("csv-to-markdown", help="Convert CSV into a padded Markdown table.")
    p_csv.add_argument("--input", required=True, help="CSV input file.")
    p_csv.add_argument("--output", help="Optional Markdown output file.")
    p_csv.add_argument("--delimiter", default=",", help="CSV delimiter character.")
    p_csv.add_argument("--quotechar", default='"', help="CSV quote character.")
    p_csv.add_argument("--no-header", action="store_true", help="Treat the CSV as headerless input.")
    p_csv.add_argument("--encoding", default="utf-8")
    p_csv.set_defaults(func=cmd_csv_to_markdown)

    p_toml_merge = subparsers.add_parser("toml-merge", help="Deep-merge two TOML files.")
    p_toml_merge.add_argument("--base", required=True, help="Base TOML file.")
    p_toml_merge.add_argument("--override", required=True, help="Override TOML file.")
    p_toml_merge.add_argument("--output", help="Optional merged TOML output file.")
    p_toml_merge.add_argument("--encoding", default="utf-8")
    p_toml_merge.set_defaults(func=cmd_toml_merge)

    p_stats = subparsers.add_parser("codeblock-language-stats", help="Count fenced code block languages in Markdown.")
    p_stats.add_argument("--input", required=True, help="Markdown input file.")
    p_stats.add_argument("--format", choices=["text", "json"], default="text")
    p_stats.add_argument("--output", help="Optional output file.")
    p_stats.add_argument("--encoding", default="utf-8")
    p_stats.set_defaults(func=cmd_codeblock_language_stats)

    p_link_extract = subparsers.add_parser("markdown-link-extract", help="Extract Markdown inline links and images.")
    p_link_extract.add_argument("--input", required=True, help="Markdown input file.")
    p_link_extract.add_argument("--format", choices=["text", "json"], default="text")
    p_link_extract.add_argument("--output", help="Optional output file.")
    p_link_extract.add_argument("--encoding", default="utf-8")
    p_link_extract.set_defaults(func=cmd_markdown_link_extract)

    p_link_check = subparsers.add_parser("markdown-link-check", help="Check local Markdown links and anchors.")
    p_link_check.add_argument("--input", required=True, help="Markdown input file.")
    p_link_check.add_argument("--root", help="Optional project root for local link resolution.")
    p_link_check.add_argument("--only-issues", action="store_true", help="Show only missing or warning results.")
    p_link_check.add_argument("--format", choices=["text", "json"], default="text")
    p_link_check.add_argument("--output", help="Optional output file.")
    p_link_check.add_argument("--encoding", default="utf-8")
    p_link_check.set_defaults(func=cmd_markdown_link_check)

    p_hash_manifest = subparsers.add_parser("file-hash-manifest", help="Create a file hash manifest for a directory.")
    p_hash_manifest.add_argument("--root", required=True, help="Project root directory.")
    p_hash_manifest.add_argument("--ext", action="append", help="Include only these extensions, comma-separated or repeated.")
    p_hash_manifest.add_argument("--ignore-dir", action="append", help="Additional directory names to ignore.")
    p_hash_manifest.add_argument("--ignore", action="append", help="Ignore path patterns, e.g. '*.log,cache/*'.")
    p_hash_manifest.add_argument("--max-depth", type=int, help="Maximum relative depth.")
    p_hash_manifest.add_argument("--max-files", type=int, help="Stop scanning after N files.")
    p_hash_manifest.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    p_hash_manifest.add_argument("--algorithm", choices=["md5", "sha1", "sha256"], default="sha256")
    p_hash_manifest.add_argument("--format", choices=["text", "json"], default="json")
    p_hash_manifest.add_argument("--output", help="Optional output file.")
    p_hash_manifest.add_argument("--encoding", default="utf-8")
    p_hash_manifest.set_defaults(func=cmd_file_hash_manifest)

    p_dup_lines = subparsers.add_parser("duplicate-line-finder", help="Find duplicate lines in a text file.")
    p_dup_lines.add_argument("--input", required=True, help="Input text file.")
    p_dup_lines.add_argument("--ignore-case", action="store_true", help="Compare lines case-insensitively.")
    p_dup_lines.add_argument("--strip-ws", action="store_true", help="Trim surrounding whitespace before comparing.")
    p_dup_lines.add_argument("--skip-empty", action="store_true", help="Ignore empty lines.")
    p_dup_lines.add_argument("--format", choices=["text", "json"], default="text")
    p_dup_lines.add_argument("--output", help="Optional output file.")
    p_dup_lines.add_argument("--encoding", default="utf-8")
    p_dup_lines.set_defaults(func=cmd_duplicate_line_finder)

    p_wc = subparsers.add_parser("markdown-word-count-by-heading", help="Count words per Markdown heading section.")
    p_wc.add_argument("--input", required=True, help="Markdown input file.")
    p_wc.add_argument("--format", choices=["text", "json"], default="text")
    p_wc.add_argument("--output", help="Optional output file.")
    p_wc.add_argument("--encoding", default="utf-8")
    p_wc.set_defaults(func=cmd_markdown_word_count_by_heading)

    p_manifest_diff = subparsers.add_parser("manifest-diff", help="Compare two JSON file hash manifests.")
    p_manifest_diff.add_argument("--base", required=True, help="Base manifest JSON file.")
    p_manifest_diff.add_argument("--other", required=True, help="Other manifest JSON file.")
    p_manifest_diff.add_argument("--format", choices=["text", "json"], default="text")
    p_manifest_diff.add_argument("--output", help="Optional output file.")
    p_manifest_diff.add_argument("--encoding", default="utf-8")
    p_manifest_diff.set_defaults(func=cmd_manifest_diff)

    p_dup_files = subparsers.add_parser("duplicate-file-finder", help="Find duplicate files by size and hash.")
    p_dup_files.add_argument("--root", required=True, help="Project root directory.")
    p_dup_files.add_argument("--ext", action="append", help="Include only these extensions, comma-separated or repeated.")
    p_dup_files.add_argument("--ignore-dir", action="append", help="Additional directory names to ignore.")
    p_dup_files.add_argument("--ignore", action="append", help="Ignore path patterns, e.g. '*.log,cache/*'.")
    p_dup_files.add_argument("--max-depth", type=int, help="Maximum relative depth.")
    p_dup_files.add_argument("--max-files", type=int, help="Stop scanning after N files.")
    p_dup_files.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    p_dup_files.add_argument("--algorithm", choices=["md5", "sha1", "sha256"], default="sha256")
    p_dup_files.add_argument("--min-size", type=int, default=1, help="Ignore files smaller than this byte size.")
    p_dup_files.add_argument("--format", choices=["text", "json"], default="text")
    p_dup_files.add_argument("--output", help="Optional output file.")
    p_dup_files.add_argument("--encoding", default="utf-8")
    p_dup_files.set_defaults(func=cmd_duplicate_file_finder)

    p_toml_flatten = subparsers.add_parser("toml-key-flatten", help="Flatten TOML keys into dotted paths.")
    p_toml_flatten.add_argument("--input", required=True, help="TOML input file.")
    p_toml_flatten.add_argument("--format", choices=["text", "json"], default="text")
    p_toml_flatten.add_argument("--output", help="Optional output file.")
    p_toml_flatten.add_argument("--encoding", default="utf-8")
    p_toml_flatten.set_defaults(func=cmd_toml_key_flatten)

    p_json_to_toml = subparsers.add_parser("json-to-toml", help="Convert a JSON object file to TOML.")
    p_json_to_toml.add_argument("--input", required=True, help="JSON input file.")
    p_json_to_toml.add_argument("--output", help="Optional TOML output file.")
    p_json_to_toml.add_argument("--encoding", default="utf-8")
    p_json_to_toml.set_defaults(func=cmd_json_to_toml)

    p_image_inventory = subparsers.add_parser("markdown-image-inventory", help="Inventory Markdown and HTML image references.")
    p_image_scope = p_image_inventory.add_mutually_exclusive_group(required=True)
    p_image_scope.add_argument("--input", help="Single Markdown input file.")
    p_image_scope.add_argument("--root", help="Project root directory to scan for Markdown files.")
    p_image_inventory.add_argument("--ext", action="append", help="Include only these extensions when using --root.")
    p_image_inventory.add_argument("--ignore-dir", action="append", help="Additional directory names to ignore.")
    p_image_inventory.add_argument("--ignore", action="append", help="Ignore path patterns, e.g. '*.log,cache/*'.")
    p_image_inventory.add_argument("--max-depth", type=int, help="Maximum relative depth when using --root.")
    p_image_inventory.add_argument("--max-files", type=int, help="Stop scanning after N files.")
    p_image_inventory.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    p_image_inventory.add_argument("--no-verify-local", action="store_true", help="Do not check local file existence.")
    p_image_inventory.add_argument("--format", choices=["text", "json"], default="text")
    p_image_inventory.add_argument("--output", help="Optional output file.")
    p_image_inventory.add_argument("--encoding", default="utf-8")
    p_image_inventory.set_defaults(func=cmd_markdown_image_inventory)

    p_batch_rename = subparsers.add_parser("safe-batch-rename", help="Preview or apply safe batch file renames.")
    p_batch_rename.add_argument("--root", required=True, help="Project root directory.")
    p_batch_rename.add_argument("--ext", action="append", help="Include only these extensions, comma-separated or repeated.")
    p_batch_rename.add_argument("--ignore-dir", action="append", help="Additional directory names to ignore.")
    p_batch_rename.add_argument("--ignore", action="append", help="Ignore path patterns, e.g. '*.log,cache/*'.")
    p_batch_rename.add_argument("--max-depth", type=int, help="Maximum relative depth.")
    p_batch_rename.add_argument("--max-files", type=int, help="Stop scanning after N files.")
    p_batch_rename.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    p_batch_rename.add_argument("--find", help="Literal text to replace in the filename stem.")
    p_batch_rename.add_argument("--replace", default="", help="Replacement text for --find or --regex.")
    p_batch_rename.add_argument("--regex", help="Regex pattern applied to the filename stem.")
    p_batch_rename.add_argument("--prefix", help="Prefix added to the filename stem.")
    p_batch_rename.add_argument("--suffix", help="Suffix added to the filename stem before the extension.")
    p_batch_rename.add_argument("--lowercase", action="store_true", help="Lowercase the filename stem.")
    p_batch_rename.add_argument("--slugify", action="store_true", help="Normalize the filename stem to a safe slug.")
    p_batch_rename.add_argument("--lowercase-extension", action="store_true", help="Lowercase the file extension.")
    p_batch_rename.add_argument("--apply", action="store_true", help="Apply the planned renames.")
    p_batch_rename.add_argument("--format", choices=["text", "json"], default="text")
    p_batch_rename.add_argument("--output", help="Optional output file.")
    p_batch_rename.add_argument("--encoding", default="utf-8")
    p_batch_rename.set_defaults(func=cmd_safe_batch_rename)

    p_freq = subparsers.add_parser("text-frequency-report", help="Build a frequency report for words, tokens, or lines.")
    p_freq.add_argument("--input", required=True, help="Input text file.")
    p_freq.add_argument("--mode", choices=["word", "token", "line"], default="word")
    p_freq.add_argument("--ignore-case", action="store_true", help="Compare items case-insensitively.")
    p_freq.add_argument("--strip-ws", action="store_true", help="Trim surrounding whitespace before counting.")
    p_freq.add_argument("--min-length", type=int, default=1, help="Ignore items shorter than this length.")
    p_freq.add_argument("--min-count", type=int, default=1, help="Ignore items below this count.")
    p_freq.add_argument("--top-n", type=int, help="Limit output to the top N rows.")
    p_freq.add_argument("--format", choices=["text", "json"], default="text")
    p_freq.add_argument("--output", help="Optional output file.")
    p_freq.add_argument("--encoding", default="utf-8")
    p_freq.set_defaults(func=cmd_text_frequency_report)

    p_toc = subparsers.add_parser("markdown-toc-generate", help="Generate a Markdown table of contents from headings.")
    p_toc.add_argument("--input", required=True, help="Markdown input file.")
    p_toc.add_argument("--min-level", type=int, default=2, help="Minimum heading level to include.")
    p_toc.add_argument("--max-level", type=int, default=6, help="Maximum heading level to include.")
    p_toc.add_argument("--skip-first-h1", action="store_true", help="Skip the first H1 heading.")
    p_toc.add_argument("--output", help="Optional output file.")
    p_toc.add_argument("--encoding", default="utf-8")
    p_toc.set_defaults(func=cmd_markdown_toc_generate)

    p_json_flatten = subparsers.add_parser("json-key-flatten", help="Flatten JSON keys into dotted paths.")
    p_json_flatten.add_argument("--input", required=True, help="JSON input file.")
    p_json_flatten.add_argument("--format", choices=["text", "json"], default="text")
    p_json_flatten.add_argument("--output", help="Optional output file.")
    p_json_flatten.add_argument("--encoding", default="utf-8")
    p_json_flatten.set_defaults(func=cmd_json_key_flatten)

    p_unique = subparsers.add_parser("unique-line-filter", help="Keep only the first unique occurrence of each line.")
    p_unique.add_argument("--input", required=True, help="Input text file.")
    p_unique.add_argument("--ignore-case", action="store_true", help="Compare lines case-insensitively.")
    p_unique.add_argument("--strip-ws", action="store_true", help="Trim surrounding whitespace before comparing.")
    p_unique.add_argument("--skip-empty", action="store_true", help="Ignore empty lines completely.")
    p_unique.add_argument("--sort-output", action="store_true", help="Sort the unique output lines.")
    p_unique.add_argument("--output", help="Optional output file.")
    p_unique.add_argument("--encoding", default="utf-8")
    p_unique.set_defaults(func=cmd_unique_line_filter)

    p_path_rewrite = subparsers.add_parser("path-rewrite", help="Rewrite path prefixes across text files.")
    p_path_rewrite.add_argument("--root", required=True, help="Project root directory.")
    p_path_rewrite.add_argument("--from-prefix", required=True, help="Source path prefix to replace.")
    p_path_rewrite.add_argument("--to-prefix", required=True, help="Target path prefix.")
    p_path_rewrite.add_argument("--ext", action="append", help="Include only these extensions, comma-separated or repeated.")
    p_path_rewrite.add_argument("--ignore-dir", action="append", help="Additional directory names to ignore.")
    p_path_rewrite.add_argument("--ignore", action="append", help="Ignore path patterns, e.g. '*.log,cache/*'.")
    p_path_rewrite.add_argument("--max-depth", type=int, help="Maximum relative depth.")
    p_path_rewrite.add_argument("--max-files", type=int, help="Stop scanning after N files.")
    p_path_rewrite.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    p_path_rewrite.add_argument("--slash-style", choices=["keep", "posix", "windows"], default="keep")
    p_path_rewrite.add_argument("--case-sensitive", action="store_true", help="Use case-sensitive matching.")
    p_path_rewrite.add_argument("--create-backup", action="store_true", help="Write .bak files before modifying originals.")
    p_path_rewrite.add_argument("--apply", action="store_true", help="Apply the rewrite. Without this flag, only preview.")
    p_path_rewrite.add_argument("--format", choices=["text", "json"], default="text")
    p_path_rewrite.add_argument("--output", help="Optional output file.")
    p_path_rewrite.add_argument("--encoding", default="utf-8")
    p_path_rewrite.set_defaults(func=cmd_path_rewrite)

    p_slugify = subparsers.add_parser("filename-slugify-batch", help="Preview or apply slugified filename renames.")
    p_slugify.add_argument("--root", required=True, help="Project root directory.")
    p_slugify.add_argument("--ext", action="append", help="Include only these extensions, comma-separated or repeated.")
    p_slugify.add_argument("--ignore-dir", action="append", help="Additional directory names to ignore.")
    p_slugify.add_argument("--ignore", action="append", help="Ignore path patterns, e.g. '*.log,cache/*'.")
    p_slugify.add_argument("--max-depth", type=int, help="Maximum relative depth.")
    p_slugify.add_argument("--max-files", type=int, help="Stop scanning after N files.")
    p_slugify.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    p_slugify.add_argument("--lowercase-extension", action="store_true", help="Lowercase the file extension.")
    p_slugify.add_argument("--dedupe", action="store_true", help="Append numeric suffixes to avoid duplicate targets inside the batch.")
    p_slugify.add_argument("--apply", action="store_true", help="Apply the planned renames.")
    p_slugify.add_argument("--format", choices=["text", "json"], default="text")
    p_slugify.add_argument("--output", help="Optional output file.")
    p_slugify.add_argument("--encoding", default="utf-8")
    p_slugify.set_defaults(func=cmd_filename_slugify_batch)

    return parser




# Keep main() and the bootstrap block at the end of the file.
# Add new helper functions and cmd_* handlers above build_parser().
# Add new CLI parser entries inside build_parser() before 'return parser'.

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.func(args))
    except Exception as exc:  # pragma: no cover
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())