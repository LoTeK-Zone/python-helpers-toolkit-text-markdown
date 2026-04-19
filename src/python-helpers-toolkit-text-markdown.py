#!/usr/bin/env python3
"""
File: python-helpers-toolkit-text-markdown.py
Description: A compact standard-library helper collection for recurring project tasks. The file is intentionally self-contained and executable as a CLI.
Author: Stephan Kühn (LoTeK)
Mail: info@lotek-zone.com
Web: https://lotek-zone.com/
GitHub: https://github.com/LoTeK-Zone
Repository: https://github.com/LoTeK-Zone/python-helpers-toolkit-text-markdown
Version: 0.2.1
Last Updated: 2026-04-19
License: MIT
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

VERSION = "0.2.1"

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
    path.write_text(text, encoding=encoding, newline="\n")  # Preserve exact LF output on all platforms

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




def convert_jsonl_to_json_array(
    jsonl_text: str,
    skip_invalid: bool,
    max_lines: int | None,
) -> tuple[list[object], int]:
    rows: list[object] = []
    skipped = 0

    for line_number, raw_line in enumerate(jsonl_text.splitlines(), start=1):
        if max_lines is not None and line_number > max_lines:
            break

        line = raw_line.strip()
        if not line:
            continue  # Ignore empty lines for cleaner JSONL handling

        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            if skip_invalid:
                skipped += 1
                continue  # Tolerate invalid rows in batch cleanup mode
            raise ValueError(f"Invalid JSON on line {line_number}: {exc.msg}") from exc

    return rows, skipped


def cmd_jsonl_to_json_array(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    rows, skipped = convert_jsonl_to_json_array(
        jsonl_text=source,
        skip_invalid=args.skip_invalid,
        max_lines=args.max_lines,
    )
    output = json.dumps(rows, indent=args.indent, ensure_ascii=args.ensure_ascii) + "\n"

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    if skipped:
        sys.stderr.write(f"Skipped invalid JSONL lines: {skipped}\n")

    return 0


def split_text_into_chunks(
    text: str,
    mode: str,
    max_size: int,
    overlap: int,
) -> list[str]:
    if max_size <= 0:
        raise ValueError("max_size must be greater than zero")

    if overlap < 0:
        raise ValueError("overlap must not be negative")

    if overlap >= max_size:
        raise ValueError("overlap must be smaller than max_size")

    if mode == "chars":
        chunks: list[str] = []
        step = max_size - overlap

        for start in range(0, len(text), step):
            chunk = text[start : start + max_size]
            if chunk:
                chunks.append(chunk)

        return chunks

    if mode == "words":
        tokens = text.split()
    elif mode == "lines":
        tokens = text.splitlines()
    else:
        raise ValueError(f"Unsupported chunk mode: {mode}")

    chunks: list[str] = []
    step = max_size - overlap

    for start in range(0, len(tokens), step):
        group = tokens[start : start + max_size]
        if not group:
            continue

        if mode == "lines":
            chunks.append("\n".join(group).rstrip("\n") + "\n")
        else:
            chunks.append(" ".join(group).strip() + "\n")

    return chunks


def cmd_text_chunk_split(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    chunks = split_text_into_chunks(
        text=source,
        mode=args.mode,
        max_size=args.max_size,
        overlap=args.overlap,
    )

    if not chunks:
        raise ValueError("No chunks were generated")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = args.prefix or "chunk"
    extension = args.extension.lstrip(".")

    for index, chunk in enumerate(chunks, start=1):
        out_path = output_dir / f"{prefix}_{index:03d}.{extension}"
        chunk_text = chunk if chunk.endswith("\n") else chunk + "\n"
        _write_text(out_path, chunk_text, encoding=args.encoding)

    sys.stdout.write(f"Wrote {len(chunks)} chunk file(s) to {output_dir}\n")
    return 0


def _split_markdown_table_cells(line: str) -> list[str]:
    stripped = line.strip()

    if stripped.startswith("|"):
        stripped = stripped[1:]

    if stripped.endswith("|"):
        stripped = stripped[:-1]

    return [cell.strip() for cell in stripped.split("|")]


def _is_markdown_table_separator(line: str, min_columns: int) -> bool:
    cells = _split_markdown_table_cells(line)
    if len(cells) < min_columns:
        return False

    for cell in cells:
        stripped = cell.replace(" ", "")
        if not stripped:
            return False
        if not re.fullmatch(r":?-{3,}:?", stripped):
            return False

    return True


def _normalize_markdown_separator_row(cells: list[str], widths: list[int]) -> str:
    normalized: list[str] = []

    for index, cell in enumerate(cells):
        stripped = cell.replace(" ", "")
        left = stripped.startswith(":")
        right = stripped.endswith(":")
        base_width = max(widths[index], 3)
        core = "-" * base_width

        if left and right and base_width >= 2:
            normalized.append(":" + core[1:-1] + ":")
        elif left and base_width >= 1:
            normalized.append(":" + core[1:])
        elif right and base_width >= 1:
            normalized.append(core[:-1] + ":")
        else:
            normalized.append(core)

    return _pad_row(normalized, widths)


def normalize_markdown_tables_in_text(text: str, min_columns: int) -> tuple[str, int]:
    lines = text.splitlines()
    output_lines: list[str] = []
    index = 0
    changed_tables = 0

    while index < len(lines):
        line = lines[index]
        next_line = lines[index + 1] if index + 1 < len(lines) else None

        if "|" not in line or next_line is None or not _is_markdown_table_separator(next_line, min_columns):
            output_lines.append(line)
            index += 1
            continue  # Keep non-table lines unchanged

        table_lines = [line, next_line]
        cursor = index + 2

        while cursor < len(lines):
            candidate = lines[cursor]
            if "|" not in candidate or not candidate.strip():
                break
            table_lines.append(candidate)
            cursor += 1

        raw_rows = [_split_markdown_table_cells(item) for item in table_lines]
        column_count = max(len(row) for row in raw_rows)
        rows = [row + [""] * (column_count - len(row)) for row in raw_rows]
        header = rows[0]
        separator = rows[1]
        body_rows = rows[2:]
        widths = _compute_column_widths(body_rows + [header], header, include_header=True)

        output_lines.append(_pad_row(header, widths))
        output_lines.append(_normalize_markdown_separator_row(separator, widths))

        for row in body_rows:
            output_lines.append(_pad_row(row, widths))

        changed_tables += 1
        index = cursor

    output = "\n".join(output_lines)
    return output.rstrip("\n") + "\n", changed_tables


def cmd_markdown_table_normalize(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    source = _read_text(input_path, encoding=args.encoding)
    output, changed_tables = normalize_markdown_tables_in_text(source, min_columns=args.min_columns)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        _write_text(input_path, output, encoding=args.encoding)

    sys.stdout.write(f"Normalized markdown tables: {changed_tables}\n")
    return 0


def _parse_column_spec(spec_text: str) -> list[str]:
    parts = [part.strip() for part in spec_text.split(",")]
    return [part for part in parts if part]


def select_csv_columns(
    csv_text: str,
    columns: list[str],
    delimiter: str,
    quotechar: str,
    has_header: bool,
) -> str:
    import csv
    import io

    reader = csv.reader(io.StringIO(csv_text), delimiter=delimiter, quotechar=quotechar)
    rows = list(reader)

    if not rows:
        raise ValueError("CSV input is empty")

    indexes: list[int] = []

    if has_header:
        header = rows[0]

        for column in columns:
            if column.isdigit():
                index = int(column) - 1
                if index < 0 or index >= len(header):
                    raise ValueError(f"CSV column index out of range: {column}")
                indexes.append(index)
            else:
                if column not in header:
                    raise ValueError(f"CSV header not found: {column}")
                indexes.append(header.index(column))
    else:
        for column in columns:
            if not column.isdigit():
                raise ValueError("Headerless CSV mode requires numeric 1-based columns")
            index = int(column) - 1
            if index < 0:
                raise ValueError(f"CSV column index out of range: {column}")
            indexes.append(index)

    selected_rows: list[list[str]] = []
    max_index = max(indexes)

    for row in rows:
        padded = row + [""] * max(0, (max_index + 1) - len(row))
        selected_rows.append([padded[index] for index in indexes])

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=delimiter, quotechar=quotechar, lineterminator="\n")
    writer.writerows(selected_rows)
    return buffer.getvalue()


def cmd_csv_column_select(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    output = select_csv_columns(
        csv_text=source,
        columns=_parse_column_spec(args.columns),
        delimiter=args.delimiter,
        quotechar=args.quotechar,
        has_header=not args.no_header,
    )

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0


def pretty_xml_text(xml_text: str, indent: int) -> str:
    from xml.dom import minidom

    parsed = minidom.parseString(xml_text.encode("utf-8"))
    pretty = parsed.toprettyxml(indent=" " * indent, encoding="utf-8").decode("utf-8")
    cleaned_lines = [line for line in pretty.splitlines() if line.strip()]  # Remove blank formatter lines
    return "\n".join(cleaned_lines).rstrip("\n") + "\n"


def cmd_xml_pretty(args: argparse.Namespace) -> int:
    source = _read_text(Path(args.input), encoding=args.encoding)
    output = pretty_xml_text(source, indent=args.indent)

    if args.output:
        _write_text(Path(args.output), output, encoding=args.encoding)
    else:
        sys.stdout.write(output)

    return 0
    

# ============================================================================
# CLI HELP FORMATTER AND REGISTRATION HELPERS
# Add new parser helper functions above this block.
# Keep comments and block headers stable so future commands can be added fast.
# ============================================================================


class ToolkitHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter,
):
    pass


# ============================================================================
# CLI METADATA REGISTRY AND DOC GENERATION HELPERS
# Keep command metadata synchronized with the real parser definitions.
# When adding a new command group, set the group once at the start of the
# registration function. Every command created afterwards is registered
# automatically for later documentation export.
# ============================================================================

CLI_GROUP_ORDER = [
    "Utility / General Helpers",
    "Markdown",
    "JSON / TOML / INI / CSV",
    "Text / Cleanup",
    "Files / Paths / Project Scans",
]

CLI_COMMAND_REGISTRY: dict[str, dict[str, object]] = {}
_CURRENT_CLI_GROUP = "Ungrouped"


def _set_cli_group(group_name: str) -> None:
    global _CURRENT_CLI_GROUP
    _CURRENT_CLI_GROUP = group_name


def _register_cli_command_metadata(
    name: str,
    summary: str,
    description: str,
    examples: list[str] | None,
) -> None:
    CLI_COMMAND_REGISTRY[name] = {
        "group": _CURRENT_CLI_GROUP,
        "name": name,
        "summary": summary,
        "description": description,
        "examples": list(examples or []),
    }


def _build_cli_examples(examples: list[str] | None) -> str:
    if not examples:
        return ""

    lines = ["Examples:"]
    for example in examples:
        lines.append(f"  {example}")

    return "\n".join(lines)


def _create_main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python-helpers-toolkit-text-markdown.py",
        description="Compact Python helper toolkit for recurring project tasks.",
        formatter_class=ToolkitHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    return parser


def _create_command_parser(
    subparsers,
    name: str,
    summary: str,
    description: str,
    examples: list[str] | None = None,
) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        name,
        help=summary,
        description=description,
        epilog=_build_cli_examples(examples),
        formatter_class=ToolkitHelpFormatter,
    )
    _register_cli_command_metadata(
        name=name,
        summary=summary,
        description=description,
        examples=examples,
    )
    return parser


def _add_input_file_arg(parser: argparse.ArgumentParser, help_text: str) -> None:
    parser.add_argument("--input", required=True, help=help_text)


def _add_output_file_arg(parser: argparse.ArgumentParser, help_text: str = "Optional output file.") -> None:
    parser.add_argument("--output", help=help_text)


def _add_encoding_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--encoding", default="utf-8", help="Text encoding used for reading and writing.")


def _add_format_arg(parser: argparse.ArgumentParser, default: str = "text") -> None:
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default=default,
        help="Output format for generated results.",
    )


def _add_root_arg(parser: argparse.ArgumentParser, help_text: str = "Project root directory.") -> None:
    parser.add_argument("--root", required=True, help=help_text)


def _add_common_scan_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ext", action="append", help="Include only these extensions, comma-separated or repeated.")
    parser.add_argument("--ignore-dir", action="append", help="Additional directory names to ignore.")
    parser.add_argument("--ignore", action="append", help="Ignore path patterns, e.g. '*.log,cache/*'.")
    parser.add_argument("--max-depth", type=int, help="Maximum relative depth below --root.")
    parser.add_argument("--max-files", type=int, help="Stop scanning after N files.")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")


# ============================================================================
# CLI DOC EXPORT HELPERS
# These helpers inspect the real parser and can be reused later to regenerate
# the README quick index and COMMAND_REFERENCE.md from one source of truth.
# ============================================================================
def _get_subparsers_action(parser: argparse.ArgumentParser):
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    raise RuntimeError("CLI subparser action not found")


def _iter_visible_option_actions(parser: argparse.ArgumentParser):
    for action in parser._actions:
        if action.dest == "help":
            continue
        yield action


def _get_action_type_label(action: argparse.Action) -> str:
    if action.option_strings:
        if action.nargs == 0 and action.const is not None and getattr(action, "default", None) is False:
            return "flag"
        if isinstance(action, argparse._StoreTrueAction):
            return "flag"
        if isinstance(action, argparse._StoreFalseAction):
            return "flag"
        if action.type is not None and hasattr(action.type, "__name__"):
            return str(action.type.__name__)
        if action.choices:
            return "choice"
        return "value"

    if action.type is not None and hasattr(action.type, "__name__"):
        return str(action.type.__name__)
    return "value"


def _normalize_action_default(action: argparse.Action) -> object:
    if action.default is argparse.SUPPRESS:
        return None
    return action.default


def collect_cli_reference_data(parser: argparse.ArgumentParser) -> list[dict[str, object]]:
    subparsers_action = _get_subparsers_action(parser)
    rows: list[dict[str, object]] = []

    for command_name, subparser in sorted(subparsers_action.choices.items(), key=lambda item: item[0]):
        command_meta = CLI_COMMAND_REGISTRY.get(
            command_name,
            {
                "group": "Ungrouped",
                "name": command_name,
                "summary": subparser.description or "",
                "description": subparser.description or "",
                "examples": [],
            },
        )
        arguments: list[dict[str, object]] = []

        for action in _iter_visible_option_actions(subparser):
            argument_name = ", ".join(action.option_strings) if action.option_strings else str(action.dest)
            arguments.append(
                {
                    "name": argument_name,
                    "dest": action.dest,
                    "required": bool(action.required),
                    "default": _normalize_action_default(action),
                    "choices": list(action.choices) if action.choices else None,
                    "type": _get_action_type_label(action),
                    "help": action.help or "",
                }
            )

        rows.append(
            {
                "group": command_meta["group"],
                "name": command_name,
                "summary": command_meta["summary"],
                "description": command_meta["description"],
                "examples": list(command_meta["examples"]),
                "arguments": arguments,
            }
        )

    group_position = {group_name: index for index, group_name in enumerate(CLI_GROUP_ORDER)}
    rows.sort(key=lambda item: (group_position.get(str(item["group"]), 999), str(item["name"])))
    return rows


def render_cli_quick_reference_markdown(
    parser: argparse.ArgumentParser,
    link_target: str = "command_reference",
) -> str:
    rows = collect_cli_reference_data(parser)
    grouped: dict[str, list[dict[str, object]]] = {}

    for row in rows:
        grouped.setdefault(str(row["group"]), []).append(row)

    lines: list[str] = []

    for group_name in CLI_GROUP_ORDER:
        items = grouped.get(group_name)
        if not items:
            continue

        lines.append(f"## {group_name}")
        lines.append("")

        for item in items:
            if link_target == "local":
                target = f"#{item['name']}"
            elif link_target == "command_reference":
                target = f"COMMAND_REFERENCE.md#{item['name']}"
            else:
                raise ValueError(f"Unsupported quick reference link target: {link_target}")

            lines.append(f"- [`{item['name']}`]({target}) - {item['summary']}")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_cli_command_reference_markdown(parser: argparse.ArgumentParser) -> str:
    rows = collect_cli_reference_data(parser)
    grouped: dict[str, list[dict[str, object]]] = {}

    for row in rows:
        grouped.setdefault(str(row["group"]), []).append(row)

    lines = [
        "# Command Reference",
        "",
        "This reference is generated from the real CLI parser metadata.",
        "",
        "## CLI Help Coverage",
        "",
        "- `python python-helpers-toolkit-text-markdown.py --help` lists all available commands.",
        "- `python python-helpers-toolkit-text-markdown.py <command> --help` lists that command's parameters, defaults, choices, and examples.",
        "- The same parser metadata drives this file, the README quick reference, and the live CLI help output.",
        "",
        "## Command Index",
        "",
    ]

    for group_name in CLI_GROUP_ORDER:
        items = grouped.get(group_name)
        if not items:
            continue

        lines.append(f"### {group_name}")
        lines.append("")

        for item in items:
            lines.append(f"- [`{item['name']}`](#{item['name']}) - {item['summary']}")

        lines.append("")

    for group_name in CLI_GROUP_ORDER:
        items = grouped.get(group_name)
        if not items:
            continue

        lines.append(f"## {group_name}")
        lines.append("")

        for item in items:
            lines.append(f"### {item['name']}")
            lines.append("")
            lines.append(item["summary"])
            lines.append("")
            lines.append("#### Description")
            lines.append("")
            lines.append(item["description"])
            lines.append("")
            lines.append("#### Parameters")
            lines.append("")

            if item["arguments"]:
                for argument in item["arguments"]:
                    lines.append(f"- `{argument['name']}`")
                    lines.append(f"  - Required: {'yes' if argument['required'] else 'no'}")
                    lines.append(f"  - Type: {argument['type']}")
                    if argument["choices"]:
                        lines.append(f"  - Choices: {', '.join(str(choice) for choice in argument['choices'])}")
                    if argument["default"] not in (None, False, [], ()):
                        lines.append(f"  - Default: `{argument['default']}`")
                    elif argument["default"] is False and argument["type"] == "flag":
                        lines.append("  - Default: `False`")
                    if argument["help"]:
                        lines.append(f"  - Notes: {argument['help']}")
            else:
                lines.append("- none")

            lines.append("")
            lines.append("#### Examples")
            lines.append("")

            if item["examples"]:
                for example in item["examples"]:
                    lines.append(f"```bash\n{example}\n```")
                    lines.append("")
            else:
                lines.append("- none")
                lines.append("")

            lines.append("[Back to Command Index](#command-index)")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def export_cli_docs(
    parser: argparse.ArgumentParser,
    quick_reference_output: Path | None,
    command_reference_output: Path | None,
    encoding: str,
) -> list[str]:
    written_paths: list[str] = []

    if quick_reference_output is not None:
        quick_text = render_cli_quick_reference_markdown(parser)
        _write_text(quick_reference_output, quick_text, encoding=encoding)
        written_paths.append(str(quick_reference_output))

    if command_reference_output is not None:
        reference_text = render_cli_command_reference_markdown(parser)
        _write_text(command_reference_output, reference_text, encoding=encoding)
        written_paths.append(str(command_reference_output))

    if not written_paths:
        raise ValueError("At least one documentation output target must be provided")

    return written_paths
def cmd_export_cli_docs(args: argparse.Namespace) -> int:
    parser = build_parser()
    written_paths = export_cli_docs(
        parser=parser,
        quick_reference_output=Path(args.quick_reference_output) if args.quick_reference_output else None,
        command_reference_output=Path(args.command_reference_output) if args.command_reference_output else None,
        encoding=args.encoding,
    )

    for path in written_paths:
        sys.stdout.write(f"Wrote documentation file: {path}\n")

    return 0


# ============================================================================
# CLI COMMAND REGISTRATION: MARKDOWN
# Add new Markdown-focused command parsers inside this section.
# Add new command handlers above the CLI helper block, then wire them here.
# ============================================================================


def _register_markdown_commands(subparsers) -> None:
    _set_cli_group("Markdown")
    parser = _create_command_parser(
        subparsers=subparsers,
        name="extract-section",
        summary="Extract a Markdown section by heading.",
        description="Extract one Markdown section by exact heading text.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py extract-section --input README.md --heading Installation",
            'python python-helpers-toolkit-text-markdown.py extract-section --input README.md --heading Usage --output usage.md',
        ],
    )
    _add_input_file_arg(parser, "Markdown input file.")
    parser.add_argument("--heading", required=True, help="Exact heading text without the leading # characters.")
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_extract_section)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="extract-codeblocks",
        summary="Extract fenced code blocks from Markdown.",
        description="Extract fenced code blocks from Markdown files.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py extract-codeblocks --input notes.md --language python",
            "python python-helpers-toolkit-text-markdown.py extract-codeblocks --input notes.md --language python --output-dir out_blocks --extension py",
        ],
    )
    _add_input_file_arg(parser, "Markdown input file.")
    parser.add_argument("--language", help="Filter by code fence language.")
    parser.add_argument("--index", type=int, default=1, help="1-based block index when not using --all.")
    parser.add_argument("--all", action="store_true", help="Output all matching blocks combined.")
    _add_output_file_arg(parser)
    parser.add_argument("--output-dir", help="Write each matching block as a separate file.")
    parser.add_argument("--extension", help="Extension used with --output-dir.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_extract_codeblocks)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="md-heading-index",
        summary="Build a Markdown heading index.",
        description="Build an index of Markdown headings with line numbers and anchors.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py md-heading-index --input README.md",
            "python python-helpers-toolkit-text-markdown.py md-heading-index --input README.md --format json --output heading_index.json",
        ],
    )
    _add_input_file_arg(parser, "Markdown input file.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_md_heading_index)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="split-markdown-sections",
        summary="Split a Markdown file into heading-based section files.",
        description="Split a Markdown file into multiple section files based on one heading level.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py split-markdown-sections --input README.md --level 2 --output-dir out_sections",
            "python python-helpers-toolkit-text-markdown.py split-markdown-sections --input notes.md --level 3 --output-dir out_sections --prefix part",
        ],
    )
    _add_input_file_arg(parser, "Markdown input file.")
    parser.add_argument("--level", type=int, default=2, help="Heading level to split on, e.g. 2 for ##.")
    parser.add_argument("--output-dir", required=True, help="Target directory for the generated section files.")
    parser.add_argument("--prefix", help="Optional filename prefix.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_split_markdown_sections)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="frontmatter-extract",
        summary="Extract a simple frontmatter block from Markdown.",
        description="Extract a simple leading frontmatter block and optionally write the remaining body.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py frontmatter-extract --input note.md",
            "python python-helpers-toolkit-text-markdown.py frontmatter-extract --input note.md --format text --body-output body.md",
        ],
    )
    _add_input_file_arg(parser, "Markdown input file.")
    _add_format_arg(parser, default="json")
    _add_output_file_arg(parser, "Optional frontmatter output file.")
    parser.add_argument("--body-output", help="Optional output file for the Markdown body without frontmatter.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_frontmatter_extract)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="frontmatter-remove",
        summary="Remove a leading frontmatter block from Markdown.",
        description="Remove a simple leading frontmatter block from a Markdown file.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py frontmatter-remove --input note.md --output note_clean.md",
        ],
    )
    _add_input_file_arg(parser, "Markdown input file.")
    _add_output_file_arg(parser, "Optional output file. If omitted, the input file is overwritten.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_frontmatter_remove)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="codeblock-language-stats",
        summary="Count fenced code block languages in Markdown.",
        description="Count fenced code blocks by language in a Markdown file.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py codeblock-language-stats --input README.md",
            "python python-helpers-toolkit-text-markdown.py codeblock-language-stats --input README.md --format json --output stats.json",
        ],
    )
    _add_input_file_arg(parser, "Markdown input file.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_codeblock_language_stats)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="markdown-link-extract",
        summary="Extract Markdown inline links and images.",
        description="Extract inline Markdown links and image references from a Markdown file.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py markdown-link-extract --input README.md",
            "python python-helpers-toolkit-text-markdown.py markdown-link-extract --input README.md --format json --output links.json",
        ],
    )
    _add_input_file_arg(parser, "Markdown input file.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_markdown_link_extract)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="markdown-link-check",
        summary="Check local Markdown links and anchors.",
        description="Check local Markdown links and local heading anchors without probing external HTTP targets.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py markdown-link-check --input README.md",
            "python python-helpers-toolkit-text-markdown.py markdown-link-check --input README.md --root . --only-issues --format json",
        ],
    )
    _add_input_file_arg(parser, "Markdown input file.")
    parser.add_argument("--root", help="Optional project root used for local link resolution.")
    parser.add_argument("--only-issues", action="store_true", help="Show only missing or warning results.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_markdown_link_check)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="markdown-image-inventory",
        summary="Inventory Markdown and HTML image references.",
        description="Inventory Markdown and HTML image references from one file or a project tree.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py markdown-image-inventory --input README.md",
            "python python-helpers-toolkit-text-markdown.py markdown-image-inventory --root . --ext md,markdown --format json --output image_inventory.json",
        ],
    )
    image_scope = parser.add_mutually_exclusive_group(required=True)
    image_scope.add_argument("--input", help="Single Markdown input file.")
    image_scope.add_argument("--root", help="Project root directory to scan for Markdown files.")
    _add_common_scan_args(parser)
    parser.add_argument("--no-verify-local", action="store_true", help="Do not check local file existence.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_markdown_image_inventory)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="markdown-word-count-by-heading",
        summary="Count words per Markdown heading section.",
        description="Count words below each Markdown heading until the next sibling or parent-level heading.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py markdown-word-count-by-heading --input README.md",
            "python python-helpers-toolkit-text-markdown.py markdown-word-count-by-heading --input notes.md --format json --output heading_counts.json",
        ],
    )
    _add_input_file_arg(parser, "Markdown input file.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_markdown_word_count_by_heading)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="markdown-toc-generate",
        summary="Generate a Markdown table of contents from headings.",
        description="Generate a Markdown table of contents based on document headings.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py markdown-toc-generate --input README.md",
            "python python-helpers-toolkit-text-markdown.py markdown-toc-generate --input notes.md --min-level 2 --max-level 4 --skip-first-h1 --output toc.md",
        ],
    )
    _add_input_file_arg(parser, "Markdown input file.")
    parser.add_argument("--min-level", type=int, default=2, help="Minimum heading level to include.")
    parser.add_argument("--max-level", type=int, default=6, help="Maximum heading level to include.")
    parser.add_argument("--skip-first-h1", action="store_true", help="Skip the first H1 heading.")
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_markdown_toc_generate)
    
    parser = _create_command_parser(
        subparsers=subparsers,
        name="markdown-table-normalize",
        summary="Normalize Markdown tables into padded stable output.",
        description="Detect standard Markdown tables and rewrite them with padded aligned columns.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py markdown-table-normalize --input README.md",
            "python python-helpers-toolkit-text-markdown.py markdown-table-normalize --input tables.md --min-columns 3 --output tables_clean.md",
        ],
    )
    _add_input_file_arg(parser, "Markdown input file.")
    parser.add_argument("--min-columns", type=int, default=2, help="Minimum number of columns required for table detection.")
    _add_output_file_arg(parser, "Optional output file. If omitted, the input file is overwritten.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_markdown_table_normalize)


# ============================================================================
# CLI COMMAND REGISTRATION: JSON, TOML, INI, CSV
# Add new data-conversion command parsers inside this section.
# ============================================================================


def _register_data_commands(subparsers) -> None:
    _set_cli_group("JSON / TOML / INI / CSV")
    parser = _create_command_parser(
        subparsers=subparsers,
        name="ini-to-toml",
        summary="Convert a simple INI file to TOML.",
        description="Convert a simple INI file to TOML using lightweight value inference.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py ini-to-toml --input settings.ini --output settings.toml",
        ],
    )
    _add_input_file_arg(parser, "INI input file.")
    _add_output_file_arg(parser, "Optional TOML output file.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_ini_to_toml)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="json-pretty",
        summary="Validate and pretty-print JSON.",
        description="Validate a JSON file and pretty-print it in a stable readable format.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py json-pretty --input data.json",
            "python python-helpers-toolkit-text-markdown.py json-pretty --input data.json --sort-keys --output data_pretty.json",
        ],
    )
    _add_input_file_arg(parser, "JSON input file.")
    _add_output_file_arg(parser)
    parser.add_argument("--indent", type=int, default=2, help="Indentation width for the JSON output.")
    parser.add_argument("--sort-keys", action="store_true", help="Sort object keys alphabetically.")
    parser.add_argument("--ensure-ascii", action="store_true", help="Escape non-ASCII characters in the output.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_json_pretty)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="csv-to-markdown",
        summary="Convert CSV into a padded Markdown table.",
        description="Convert CSV input into a padded Markdown table.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py csv-to-markdown --input table.csv",
            'python python-helpers-toolkit-text-markdown.py csv-to-markdown --input table.csv --delimiter ";" --output table.md',
        ],
    )
    _add_input_file_arg(parser, "CSV input file.")
    _add_output_file_arg(parser, "Optional Markdown output file.")
    parser.add_argument("--delimiter", default=",", help="CSV delimiter character.")
    parser.add_argument("--quotechar", default='"', help="CSV quote character.")
    parser.add_argument("--no-header", action="store_true", help="Treat the CSV as headerless input.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_csv_to_markdown)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="toml-merge",
        summary="Deep-merge two TOML files.",
        description="Deep-merge two TOML files where override values replace base values.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py toml-merge --base default.toml --override local.toml",
            "python python-helpers-toolkit-text-markdown.py toml-merge --base default.toml --override local.toml --output merged.toml",
        ],
    )
    parser.add_argument("--base", required=True, help="Base TOML file.")
    parser.add_argument("--override", required=True, help="Override TOML file.")
    _add_output_file_arg(parser, "Optional merged TOML output file.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_toml_merge)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="toml-key-flatten",
        summary="Flatten TOML keys into dotted paths.",
        description="Flatten nested TOML keys into dotted path output for audits and comparisons.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py toml-key-flatten --input settings.toml",
            "python python-helpers-toolkit-text-markdown.py toml-key-flatten --input settings.toml --format json --output flat_keys.json",
        ],
    )
    _add_input_file_arg(parser, "TOML input file.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_toml_key_flatten)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="json-to-toml",
        summary="Convert a JSON object file to TOML.",
        description="Convert a JSON object file to TOML.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py json-to-toml --input config.json",
            "python python-helpers-toolkit-text-markdown.py json-to-toml --input config.json --output config.toml",
        ],
    )
    _add_input_file_arg(parser, "JSON input file.")
    _add_output_file_arg(parser, "Optional TOML output file.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_json_to_toml)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="json-key-flatten",
        summary="Flatten JSON keys into dotted paths.",
        description="Flatten nested JSON keys into dotted paths with array indices.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py json-key-flatten --input data.json",
            "python python-helpers-toolkit-text-markdown.py json-key-flatten --input data.json --format json --output flat_keys.json",
        ],
    )
    _add_input_file_arg(parser, "JSON input file.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_json_key_flatten)
    
    
    
    parser = _create_command_parser(
        subparsers=subparsers,
        name="jsonl-to-json-array",
        summary="Convert JSONL into one JSON array.",
        description="Read newline-delimited JSON and write one pretty-printed JSON array.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py jsonl-to-json-array --input records.jsonl --output records.json",
            "python python-helpers-toolkit-text-markdown.py jsonl-to-json-array --input records.jsonl --skip-invalid --indent 2",
        ],
    )
    _add_input_file_arg(parser, "JSONL input file.")
    _add_output_file_arg(parser, "Optional JSON output file.")
    parser.add_argument("--skip-invalid", action="store_true", help="Skip invalid JSONL rows instead of failing immediately.")
    parser.add_argument("--max-lines", type=int, help="Optional maximum number of input lines to process.")
    parser.add_argument("--indent", type=int, default=2, help="Indentation width for the JSON array output.")
    parser.add_argument("--ensure-ascii", action="store_true", help="Escape non-ASCII characters in the output.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_jsonl_to_json_array)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="csv-column-select",
        summary="Select and reorder CSV columns.",
        description="Select a subset of CSV columns by header name or 1-based index and write a reduced CSV file.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py csv-column-select --input table.csv --columns title,url,date --output slim.csv",
            "python python-helpers-toolkit-text-markdown.py csv-column-select --input table.csv --columns 1,4,2 --no-header --output reordered.csv",
        ],
    )
    _add_input_file_arg(parser, "CSV input file.")
    _add_output_file_arg(parser, "Optional CSV output file.")
    parser.add_argument("--columns", required=True, help="Comma-separated header names or 1-based column indexes.")
    parser.add_argument("--delimiter", default=",", help="CSV delimiter character.")
    parser.add_argument("--quotechar", default='"', help="CSV quote character.")
    parser.add_argument("--no-header", action="store_true", help="Treat the CSV as headerless input and require numeric columns.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_csv_column_select)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="xml-pretty",
        summary="Validate and pretty-print XML.",
        description="Validate XML input and rewrite it in a stable indented layout.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py xml-pretty --input sitemap.xml",
            "python python-helpers-toolkit-text-markdown.py xml-pretty --input export.xml --indent 4 --output export_pretty.xml",
        ],
    )
    _add_input_file_arg(parser, "XML input file.")
    _add_output_file_arg(parser, "Optional XML output file.")
    parser.add_argument("--indent", type=int, default=2, help="Indentation width for pretty-printed XML output.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_xml_pretty)


# ============================================================================
# CLI COMMAND REGISTRATION: TEXT, CLEANUP, SEARCH, REWRITE
# Add new text-processing command parsers inside this section.
# ============================================================================


def _register_text_commands(subparsers) -> None:
    _set_cli_group("Text / Cleanup")
    parser = _create_command_parser(
        subparsers=subparsers,
        name="replace-between-markers",
        summary="Replace text between two markers.",
        description="Replace the content between two known start and end markers.",
        examples=[
            'python python-helpers-toolkit-text-markdown.py replace-between-markers --input app.js --start-marker "/* START */" --end-marker "/* END */" --replacement-file new_block.txt',
            'python python-helpers-toolkit-text-markdown.py replace-between-markers --input config.md --start-marker "<!-- START -->" --end-marker "<!-- END -->" --replacement-text "New content"',
        ],
    )
    _add_input_file_arg(parser, "Target file.")
    parser.add_argument("--start-marker", required=True, help="Marker where replacement starts.")
    parser.add_argument("--end-marker", required=True, help="Marker where replacement ends.")
    parser.add_argument("--replacement-text", help="Replacement text passed directly on the CLI.")
    parser.add_argument("--replacement-file", help="Read replacement text from this file.")
    _add_output_file_arg(parser, "Optional output file. If omitted, the input file is overwritten.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_replace_between_markers)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="normalize-text",
        summary="Normalize line endings and whitespace.",
        description="Normalize line endings, trim trailing whitespace, and optionally expand tabs.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py normalize-text --input README.md --line-ending lf",
            "python python-helpers-toolkit-text-markdown.py normalize-text --input script.py --expand-tabs 4 --output script_clean.py",
        ],
    )
    _add_input_file_arg(parser, "Input text file.")
    _add_output_file_arg(parser, "Optional output file. If omitted, the input file is overwritten.")
    parser.add_argument("--line-ending", choices=["lf", "crlf"], default="lf", help="Target line ending style.")
    parser.add_argument("--keep-trailing-ws", action="store_true", help="Keep trailing whitespace.")
    parser.add_argument("--no-final-newline", action="store_true", help="Do not force a final newline.")
    parser.add_argument("--expand-tabs", type=int, help="Expand tabs to spaces using this tab size.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_normalize_text)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="find-text",
        summary="Find text matches across files.",
        description="Find literal text or regex matches across multiple files.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py find-text --root . --query TODO --ext py,md",
            'python python-helpers-toolkit-text-markdown.py find-text --root . --query "class\\s+\\w+" --ext py --regex --format json',
        ],
    )
    _add_root_arg(parser, "Root directory to scan.")
    parser.add_argument("--query", required=True, help="Literal text or regex pattern to find.")
    _add_common_scan_args(parser)
    parser.add_argument("--max-matches", type=int, help="Stop after N total matches.")
    parser.add_argument("--regex", action="store_true", help="Treat --query as a regular expression.")
    parser.add_argument("--case-sensitive", action="store_true", help="Use case-sensitive matching.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_find_text)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="safe-search-replace",
        summary="Replace text across files with dry-run support.",
        description="Replace text across multiple files with optional dry-run and backup support.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py safe-search-replace --root . --query foo --replacement bar --ext py --dry-run",
            'python python-helpers-toolkit-text-markdown.py safe-search-replace --root . --query "foo\\((.*?)\\)" --replacement "bar(\\1)" --ext py --regex --create-backup',
        ],
    )
    _add_root_arg(parser, "Root directory to scan.")
    parser.add_argument("--query", required=True, help="Literal text or regex pattern to replace.")
    parser.add_argument("--replacement", required=True, help="Replacement text.")
    _add_common_scan_args(parser)
    parser.add_argument("--regex", action="store_true", help="Treat --query as a regular expression.")
    parser.add_argument("--case-sensitive", action="store_true", help="Use case-sensitive matching.")
    parser.add_argument("--dry-run", action="store_true", help="Only report changes without writing files.")
    parser.add_argument("--create-backup", action="store_true", help="Write .bak files before modifying originals.")
    _add_format_arg(parser)
    _add_output_file_arg(parser, "Optional report output file.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_safe_search_replace)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="duplicate-line-finder",
        summary="Find duplicate lines in a text file.",
        description="Find duplicate lines inside a text file.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py duplicate-line-finder --input keywords.txt",
            "python python-helpers-toolkit-text-markdown.py duplicate-line-finder --input keywords.txt --ignore-case --strip-ws --skip-empty",
        ],
    )
    _add_input_file_arg(parser, "Input text file.")
    parser.add_argument("--ignore-case", action="store_true", help="Compare lines case-insensitively.")
    parser.add_argument("--strip-ws", action="store_true", help="Trim surrounding whitespace before comparing.")
    parser.add_argument("--skip-empty", action="store_true", help="Ignore empty lines.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_duplicate_line_finder)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="text-frequency-report",
        summary="Build a frequency report for words, tokens, or lines.",
        description="Build a frequency report for words, tokens, or lines in a text file.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py text-frequency-report --input notes.txt --mode word --top-n 50",
            "python python-helpers-toolkit-text-markdown.py text-frequency-report --input prompts.txt --mode line --ignore-case --strip-ws --format json",
        ],
    )
    _add_input_file_arg(parser, "Input text file.")
    parser.add_argument("--mode", choices=["word", "token", "line"], default="word", help="Frequency mode to use.")
    parser.add_argument("--ignore-case", action="store_true", help="Compare items case-insensitively.")
    parser.add_argument("--strip-ws", action="store_true", help="Trim surrounding whitespace before counting.")
    parser.add_argument("--min-length", type=int, default=1, help="Ignore items shorter than this length.")
    parser.add_argument("--min-count", type=int, default=1, help="Ignore items below this count.")
    parser.add_argument("--top-n", type=int, help="Limit output to the top N rows.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_text_frequency_report)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="unique-line-filter",
        summary="Keep only the first unique occurrence of each line.",
        description="Keep only the first unique occurrence of each line from a text file.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py unique-line-filter --input keywords.txt",
            "python python-helpers-toolkit-text-markdown.py unique-line-filter --input tags.txt --ignore-case --strip-ws --skip-empty --output unique_tags.txt",
        ],
    )
    _add_input_file_arg(parser, "Input text file.")
    parser.add_argument("--ignore-case", action="store_true", help="Compare lines case-insensitively.")
    parser.add_argument("--strip-ws", action="store_true", help="Trim surrounding whitespace before comparing.")
    parser.add_argument("--skip-empty", action="store_true", help="Ignore empty lines completely.")
    parser.add_argument("--sort-output", action="store_true", help="Sort the unique output lines.")
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_unique_line_filter)
    
    parser = _create_command_parser(
        subparsers=subparsers,
        name="path-rewrite",
        summary="Rewrite path prefixes across text files.",
        description="Rewrite path prefixes across multiple text files with preview or apply mode.",
        examples=[
            'python python-helpers-toolkit-text-markdown.py path-rewrite --root . --from-prefix "assets/old/" --to-prefix "assets/new/"',
            'python python-helpers-toolkit-text-markdown.py path-rewrite --root . --from-prefix "C:\\Old\\Base" --to-prefix "D:\\New\\Base" --slash-style windows --apply --create-backup',
        ],
    )
    _add_root_arg(parser, "Project root directory.")
    parser.add_argument("--from-prefix", required=True, help="Source path prefix to replace.")
    parser.add_argument("--to-prefix", required=True, help="Target path prefix.")
    _add_common_scan_args(parser)
    parser.add_argument("--slash-style", choices=["keep", "posix", "windows"], default="keep", help="Slash style for rewritten paths.")
    parser.add_argument("--case-sensitive", action="store_true", help="Use case-sensitive matching.")
    parser.add_argument("--create-backup", action="store_true", help="Write .bak files before modifying originals.")
    parser.add_argument("--apply", action="store_true", help="Apply the rewrite. Without this flag only preview is performed.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_path_rewrite)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="text-chunk-split",
        summary="Split long text into reusable chunks.",
        description="Split a text file into numbered chunks by characters, words, or lines.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py text-chunk-split --input big.txt --output-dir out_chunks --mode words --max-size 400",
            "python python-helpers-toolkit-text-markdown.py text-chunk-split --input big.txt --output-dir out_chunks --mode chars --max-size 2000 --overlap 200",
        ],
    )
    _add_input_file_arg(parser, "Input text file.")
    parser.add_argument("--output-dir", required=True, help="Target directory for generated chunk files.")
    parser.add_argument("--mode", choices=["chars", "words", "lines"], default="chars", help="Chunking mode.")
    parser.add_argument("--max-size", required=True, type=int, help="Maximum chunk size measured in the selected mode.")
    parser.add_argument("--overlap", type=int, default=0, help="Overlap size between adjacent chunks in the selected mode.")
    parser.add_argument("--prefix", default="chunk", help="Filename prefix for generated chunk files.")
    parser.add_argument("--extension", default="txt", help="Filename extension for generated chunk files.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_text_chunk_split)
    
    
# ============================================================================
# CLI COMMAND REGISTRATION: FILES, PATHS, PROJECT SCANS, HASHING, RENAMES
# Add new filesystem-oriented command parsers inside this section.
# ============================================================================


def _register_file_commands(subparsers) -> None:
    _set_cli_group("Files / Paths / Project Scans")
    parser = _create_command_parser(
        subparsers=subparsers,
        name="project-index",
        summary="Create a lightweight file index.",
        description="Create a lightweight file index for a project root.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py project-index --root . --ext py,md,js --format text",
            "python python-helpers-toolkit-text-markdown.py project-index --root . --ext py,md --format json --output project_index.json",
        ],
    )
    _add_root_arg(parser, "Project root directory.")
    _add_common_scan_args(parser)
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    parser.set_defaults(func=cmd_project_index)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="project-manifest",
        summary="Create a compact project manifest.",
        description="Create a compact project manifest with suffix statistics and largest files.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py project-manifest --root . --ext py,md,js",
            "python python-helpers-toolkit-text-markdown.py project-manifest --root . --format json --output manifest.json",
        ],
    )
    _add_root_arg(parser, "Project root directory.")
    _add_common_scan_args(parser)
    parser.add_argument("--top-n", type=int, default=10, help="Number of largest files to include.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_project_manifest)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="file-hash-manifest",
        summary="Create a file hash manifest for a directory.",
        description="Create a file hash manifest for a directory tree.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py file-hash-manifest --root . --format json --output manifest.json",
            "python python-helpers-toolkit-text-markdown.py file-hash-manifest --root . --ext md,txt --algorithm sha256",
        ],
    )
    _add_root_arg(parser, "Project root directory.")
    _add_common_scan_args(parser)
    parser.add_argument("--algorithm", choices=["md5", "sha1", "sha256"], default="sha256", help="Hash algorithm used for each file.")
    _add_format_arg(parser, default="json")
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_file_hash_manifest)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="manifest-diff",
        summary="Compare two JSON file hash manifests.",
        description="Compare two JSON file hash manifests generated by file-hash-manifest.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py manifest-diff --base manifest_old.json --other manifest_new.json",
            "python python-helpers-toolkit-text-markdown.py manifest-diff --base manifest_old.json --other manifest_new.json --format json --output diff.json",
        ],
    )
    parser.add_argument("--base", required=True, help="Base manifest JSON file.")
    parser.add_argument("--other", required=True, help="Other manifest JSON file.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_manifest_diff)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="duplicate-file-finder",
        summary="Find duplicate files by size and hash.",
        description="Find duplicate files by size and hash across a directory tree.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py duplicate-file-finder --root .",
            "python python-helpers-toolkit-text-markdown.py duplicate-file-finder --root . --ext jpg,png,webp --min-size 1024 --format json",
        ],
    )
    _add_root_arg(parser, "Project root directory.")
    _add_common_scan_args(parser)
    parser.add_argument("--algorithm", choices=["md5", "sha1", "sha256"], default="sha256", help="Hash algorithm used for duplicate detection.")
    parser.add_argument("--min-size", type=int, default=1, help="Ignore files smaller than this byte size.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_duplicate_file_finder)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="safe-batch-rename",
        summary="Preview or apply safe batch file renames.",
        description="Preview or apply safe batch file renames based on stem transformations.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py safe-batch-rename --root . --find old --replace new",
            "python python-helpers-toolkit-text-markdown.py safe-batch-rename --root . --prefix img_ --slugify --lowercase --apply",
        ],
    )
    _add_root_arg(parser, "Project root directory.")
    _add_common_scan_args(parser)
    parser.add_argument("--find", help="Literal text to replace in the filename stem.")
    parser.add_argument("--replace", default="", help="Replacement text for --find or --regex.")
    parser.add_argument("--regex", help="Regex pattern applied to the filename stem.")
    parser.add_argument("--prefix", help="Prefix added to the filename stem.")
    parser.add_argument("--suffix", help="Suffix added to the filename stem before the extension.")
    parser.add_argument("--lowercase", action="store_true", help="Lowercase the filename stem.")
    parser.add_argument("--slugify", action="store_true", help="Normalize the filename stem to a safe slug.")
    parser.add_argument("--lowercase-extension", action="store_true", help="Lowercase the file extension.")
    parser.add_argument("--apply", action="store_true", help="Apply the planned renames.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_safe_batch_rename)

    parser = _create_command_parser(
        subparsers=subparsers,
        name="filename-slugify-batch",
        summary="Preview or apply slugified filename renames.",
        description="Preview or apply slugified filename renames using the toolkit slugify rules.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py filename-slugify-batch --root .",
            "python python-helpers-toolkit-text-markdown.py filename-slugify-batch --root . --ext jpg,png,webp --dedupe --lowercase-extension --apply",
        ],
    )
    _add_root_arg(parser, "Project root directory.")
    _add_common_scan_args(parser)
    parser.add_argument("--lowercase-extension", action="store_true", help="Lowercase the file extension.")
    parser.add_argument("--dedupe", action="store_true", help="Append numeric suffixes to avoid duplicate targets inside the batch.")
    parser.add_argument("--apply", action="store_true", help="Apply the planned renames.")
    _add_format_arg(parser)
    _add_output_file_arg(parser)
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_filename_slugify_batch)


# ============================================================================
# CLI COMMAND REGISTRATION: UTILITY / DOC EXPORT
# Add new utility-oriented command parsers inside this section.
# Place documentation export commands here so they stay easy to find.
# ============================================================================


def _register_utility_commands(subparsers) -> None:
    _set_cli_group("Utility / General Helpers")
    parser = _create_command_parser(
        subparsers=subparsers,
        name="export-cli-docs",
        summary="Export CLI quick reference and command reference.",
        description="Export CLI-driven documentation files from the real parser metadata registry.",
        examples=[
            "python python-helpers-toolkit-text-markdown.py export-cli-docs --command-reference-output COMMAND_REFERENCE.md",
            "python python-helpers-toolkit-text-markdown.py export-cli-docs --quick-reference-output README_QUICK_REFERENCE.md --command-reference-output COMMAND_REFERENCE.md",
        ],
    )
    parser.add_argument("--quick-reference-output", help="Optional output file for the generated README quick reference section.")
    parser.add_argument("--command-reference-output", help="Optional output file for the generated full command reference.")
    _add_encoding_arg(parser)
    parser.set_defaults(func=cmd_export_cli_docs)


# ============================================================================
# CLI BUILD ENTRY POINT
# Add new command group registration calls inside build_parser().
# Keep build_parser() short. Place detailed parser definitions in the group
# registration blocks above so future commands can be inserted predictably.
# ============================================================================


def build_parser() -> argparse.ArgumentParser:
    parser = _create_main_parser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    _register_utility_commands(subparsers)
    _register_markdown_commands(subparsers)
    _register_data_commands(subparsers)
    _register_text_commands(subparsers)
    _register_file_commands(subparsers)

    return parser



# Keep main() and the bootstrap block at the end of the file.
# Add new helper functions and cmd_* handlers above the CLI helper block.
# Add new parser helper functions above the CLI helper block.
# Add new command definitions inside the registration blocks above build_parser().

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.func(args))
    except Exception as exc:  # pragma: no cover
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())