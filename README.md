# Python Helpers Toolkit Text Markdown README

![version](https://img.shields.io/badge/version-v0.2.1-blue?style=flat-square&logo=github)
![license](https://img.shields.io/badge/license-MIT-green?style=flat-square&logo=open-source-initiative)
![status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)
![python](https://img.shields.io/badge/language-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![offline-tool](https://img.shields.io/badge/offline-tool-blue?style=flat-square)
![platform-windows](https://img.shields.io/badge/platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)
![platform-linux](https://img.shields.io/badge/platform-Linux-FCC624?style=flat-square&logo=linux&logoColor=black)
![platform-macos](https://img.shields.io/badge/platform-macOS-000000?style=flat-square&logo=apple&logoColor=white)

## Description

`python_helpers.py` is a compact, stdlib-only helper toolkit for practical file, text, Markdown, and lightweight config tasks.
It is aimed at developers, scripters, content maintainers, and utility-focused project workflows that need small recurring tools without pulling in a larger dependency stack.

Typical use cases include:
- Markdown inspection and restructuring
- local link and image checks
- text normalization and search/replace jobs
- JSON, INI, TOML, and CSV conversion helpers
- small project inventory, manifest, and file-maintenance tasks

The project is most useful for people who want one portable Python file with predictable CLI commands and reusable helper functions for everyday maintenance work.

## Repository Structure

<details>
<summary>Show repository layout</summary>

```text
python-helpers-toolkit-text-markdown/
├── src/
│   └── python_helpers-toolkit-text-markdown.py   # main toolkit file
├── CHANGELOG.md                                  # version history
├── LICENSE                                       # license text
└── README.md                                     # project overview
```

</details>

## Recommended Project Placement

Copy the file into projects where repeated text, Markdown, config, or file-structure work is expected.
Typical examples:
- programming projects
- Markdown-heavy projects
- CMS/content projects
- migration and conversion projects
- utility/tooling projects

## General Usage

Run the file with a subcommand:

```bash
python python_helpers.py <toolname> [options]
```

Show top-level help:

```bash
python python_helpers.py --help
```

Show subcommand help:

```bash
python python_helpers.py project-index --help
```

## Current Tool Index


### Utility / General Helpers

- [`export-cli-docs`](COMMAND_REFERENCE.md#export-cli-docs) - Export CLI quick reference and command reference.

### Markdown

- [`codeblock-language-stats`](COMMAND_REFERENCE.md#codeblock-language-stats) - Count fenced code block languages in Markdown.
- [`extract-codeblocks`](COMMAND_REFERENCE.md#extract-codeblocks) - Extract fenced code blocks from Markdown.
- [`extract-section`](COMMAND_REFERENCE.md#extract-section) - Extract a Markdown section by heading.
- [`frontmatter-extract`](COMMAND_REFERENCE.md#frontmatter-extract) - Extract a simple frontmatter block from Markdown.
- [`frontmatter-remove`](COMMAND_REFERENCE.md#frontmatter-remove) - Remove a leading frontmatter block from Markdown.
- [`markdown-image-inventory`](COMMAND_REFERENCE.md#markdown-image-inventory) - Inventory Markdown and HTML image references.
- [`markdown-link-check`](COMMAND_REFERENCE.md#markdown-link-check) - Check local Markdown links and anchors.
- [`markdown-link-extract`](COMMAND_REFERENCE.md#markdown-link-extract) - Extract Markdown inline links and images.
- [`markdown-table-normalize`](COMMAND_REFERENCE.md#markdown-table-normalize) - Normalize Markdown tables into padded stable output.
- [`markdown-toc-generate`](COMMAND_REFERENCE.md#markdown-toc-generate) - Generate a Markdown table of contents from headings.
- [`markdown-word-count-by-heading`](COMMAND_REFERENCE.md#markdown-word-count-by-heading) - Count words per Markdown heading section.
- [`md-heading-index`](COMMAND_REFERENCE.md#md-heading-index) - Build a Markdown heading index.
- [`split-markdown-sections`](COMMAND_REFERENCE.md#split-markdown-sections) - Split a Markdown file into heading-based section files.

### JSON / TOML / INI / CSV

- [`csv-column-select`](COMMAND_REFERENCE.md#csv-column-select) - Select and reorder CSV columns.
- [`csv-to-markdown`](COMMAND_REFERENCE.md#csv-to-markdown) - Convert CSV into a padded Markdown table.
- [`ini-to-toml`](COMMAND_REFERENCE.md#ini-to-toml) - Convert a simple INI file to TOML.
- [`json-key-flatten`](COMMAND_REFERENCE.md#json-key-flatten) - Flatten JSON keys into dotted paths.
- [`json-pretty`](COMMAND_REFERENCE.md#json-pretty) - Validate and pretty-print JSON.
- [`json-to-toml`](COMMAND_REFERENCE.md#json-to-toml) - Convert a JSON object file to TOML.
- [`jsonl-to-json-array`](COMMAND_REFERENCE.md#jsonl-to-json-array) - Convert JSONL into one JSON array.
- [`toml-key-flatten`](COMMAND_REFERENCE.md#toml-key-flatten) - Flatten TOML keys into dotted paths.
- [`toml-merge`](COMMAND_REFERENCE.md#toml-merge) - Deep-merge two TOML files.
- [`xml-pretty`](COMMAND_REFERENCE.md#xml-pretty) - Validate and pretty-print XML.

### Text / Cleanup

- [`duplicate-line-finder`](COMMAND_REFERENCE.md#duplicate-line-finder) - Find duplicate lines in a text file.
- [`find-text`](COMMAND_REFERENCE.md#find-text) - Find text matches across files.
- [`normalize-text`](COMMAND_REFERENCE.md#normalize-text) - Normalize line endings and whitespace.
- [`path-rewrite`](COMMAND_REFERENCE.md#path-rewrite) - Rewrite path prefixes across text files.
- [`replace-between-markers`](COMMAND_REFERENCE.md#replace-between-markers) - Replace text between two markers.
- [`safe-search-replace`](COMMAND_REFERENCE.md#safe-search-replace) - Replace text across files with dry-run support.
- [`text-chunk-split`](COMMAND_REFERENCE.md#text-chunk-split) - Split long text into reusable chunks.
- [`text-frequency-report`](COMMAND_REFERENCE.md#text-frequency-report) - Build a frequency report for words, tokens, or lines.
- [`unique-line-filter`](COMMAND_REFERENCE.md#unique-line-filter) - Keep only the first unique occurrence of each line.

### Files / Paths / Project Scans

- [`duplicate-file-finder`](COMMAND_REFERENCE.md#duplicate-file-finder) - Find duplicate files by size and hash.
- [`file-hash-manifest`](COMMAND_REFERENCE.md#file-hash-manifest) - Create a file hash manifest for a directory.
- [`filename-slugify-batch`](COMMAND_REFERENCE.md#filename-slugify-batch) - Preview or apply slugified filename renames.
- [`manifest-diff`](COMMAND_REFERENCE.md#manifest-diff) - Compare two JSON file hash manifests.
- [`project-index`](COMMAND_REFERENCE.md#project-index) - Create a lightweight file index.
- [`project-manifest`](COMMAND_REFERENCE.md#project-manifest) - Create a compact project manifest.
- [`safe-batch-rename`](COMMAND_REFERENCE.md#safe-batch-rename) - Preview or apply safe batch file renames.

## Tool Details

### project-index

Purpose:
Create a fast file overview for a project root.

Typical use cases:
- build a quick inventory of relevant files
- ignore heavy directories like `node_modules`
- create a compact list for analysis or documentation

Example:

```bash
python python_helpers.py project-index --root . --ext py,md,js --format text
```

JSON output example:

```bash
python python_helpers.py project-index --root . --ext py,md --format json --output project_index.json
```

Important notes:
- common heavy directories are ignored by default
- more ignored directories can be added with `--ignore-dir`
- path patterns can be ignored with `--ignore`

### extract-section

Purpose:
Extract one Markdown section by exact heading text.

Example:

```bash
python python_helpers.py extract-section --input README.md --heading "Installation"
```

Example with output file:

```bash
python python_helpers.py extract-section --input README.md --heading "Usage" --output usage_section.md
```

Important notes:
- match is based on exact heading text without the leading `#`
- the extraction stops at the next heading of the same or higher level

### extract-codeblocks

Purpose:
Extract fenced code blocks from Markdown files.

Examples:

```bash
python python_helpers.py extract-codeblocks --input notes.md --language python
```

```bash
python python_helpers.py extract-codeblocks --input notes.md --language python --all --output extracted_python.txt
```

```bash
python python_helpers.py extract-codeblocks --input notes.md --language python --output-dir out_blocks --extension py
```

Important notes:
- supports language filtering
- can output a single indexed block, all combined blocks, or separate files
- block index is 1-based

### replace-between-markers

Purpose:
Replace the content between two known markers.

Examples:

```bash
python python_helpers.py replace-between-markers \
  --input app.js \
  --start-marker "/* START */" \
  --end-marker "/* END */" \
  --replacement-file new_block.txt
```

```bash
python python_helpers.py replace-between-markers \
  --input config.md \
  --start-marker "<!-- START -->" \
  --end-marker "<!-- END -->" \
  --replacement-text "New content"
```

Important notes:
- if `--output` is omitted, the input file is overwritten
- markers themselves stay in the file

### ini-to-toml

Purpose:
Convert simple INI files to TOML.

Example:

```bash
python python_helpers.py ini-to-toml --input settings.ini --output settings.toml
```

Important notes:
- designed for simple and predictable INI structures
- preserves section names and key names
- basic value inference is applied for integers, floats, booleans, and strings

### normalize-text

Purpose:
Normalize line endings and whitespace.

Examples:

```bash
python python_helpers.py normalize-text --input README.md --line-ending lf
```

```bash
python python_helpers.py normalize-text --input script.py --expand-tabs 4 --output script_clean.py
```

Important notes:
- if `--output` is omitted, the input file is overwritten
- trailing whitespace is removed by default
- a final newline is enforced by default

### json-pretty

Purpose:
Validate and pretty-print JSON.

Examples:

```bash
python python_helpers.py json-pretty --input data.json
```

```bash
python python_helpers.py json-pretty --input data.json --sort-keys --output data_pretty.json
```

Important notes:
- invalid JSON produces an error
- output is formatted with indentation

### find-text

Purpose:
Find literal text or regex matches across multiple files.

Examples:

```bash
python python_helpers.py find-text --root . --query TODO --ext py,md
```

```bash
python python_helpers.py find-text --root . --query "class\\s+\\w+" --ext py --regex --format json
```

Important notes:
- supports literal and regex search
- can limit file count, depth, and total matches
- respects ignored directories and ignore patterns

### safe-search-replace

Purpose:
Replace text across multiple files with dry-run support.

Examples:

```bash
python python_helpers.py safe-search-replace --root . --query foo --replacement bar --ext py --dry-run
```

```bash
python python_helpers.py safe-search-replace --root . --query "foo\\((.*?)\\)" --replacement "bar(\\1)" --ext py --regex --create-backup
```

Important notes:
- dry-run mode reports changes without writing files
- optional `.bak` backup creation
- supports literal and regex replacement

### md-heading-index

Purpose:
Build a heading index from a Markdown file.

Examples:

```bash
python python_helpers.py md-heading-index --input README.md
```

```bash
python python_helpers.py md-heading-index --input README.md --format json --output heading_index.json
```

Important notes:
- indexes standard ATX headings (`#` to `######`)
- reports heading level, title, line number, and anchor

### split-markdown-sections

Purpose:
Split a Markdown file into separate files by heading level.

Examples:

```bash
python python_helpers.py split-markdown-sections --input README.md --level 2 --output-dir out_sections
```

```bash
python python_helpers.py split-markdown-sections --input notes.md --level 3 --output-dir out_sections --prefix part
```

Important notes:
- splits only on the selected heading level
- output files get numeric prefixes and sanitized filenames
- useful for large Markdown restructuring

### project-manifest

Purpose:
Create a compact manifest of a project directory.

Examples:

```bash
python python_helpers.py project-manifest --root . --ext py,md,js
```

```bash
python python_helpers.py project-manifest --root . --format json --output manifest.json
```

Important notes:
- summarizes file counts and total bytes
- groups files by suffix
- lists the largest files

### frontmatter-extract

Purpose:
Extract a simple leading frontmatter block from a Markdown file.

Examples:

```bash
python python_helpers.py frontmatter-extract --input note.md
```

```bash
python python_helpers.py frontmatter-extract --input note.md --format text --body-output body.md
```

Important notes:
- expects the frontmatter block at the very start of the file
- supports simple `key: value` lines
- supports simple arrays like `[a, b, c]`

### frontmatter-remove

Purpose:
Remove a simple leading frontmatter block from a Markdown file.

Examples:

```bash
python python_helpers.py frontmatter-remove --input note.md --output note_clean.md
```

Important notes:
- only removes a frontmatter block at the file start
- if `--output` is omitted, the input file is overwritten

### csv-to-markdown

Purpose:
Convert CSV input into a padded Markdown table.

Examples:

```bash
python python_helpers.py csv-to-markdown --input table.csv
```

```bash
python python_helpers.py csv-to-markdown --input table.csv --delimiter ";" --output table.md
```

Important notes:
- normalizes uneven row lengths
- uses the first row as header by default
- `--no-header` generates synthetic column names

### toml-merge

Purpose:
Deep-merge two TOML files.

Examples:

```bash
python python_helpers.py toml-merge --base default.toml --override local.toml
```

```bash
python python_helpers.py toml-merge --base default.toml --override local.toml --output merged.toml
```

Important notes:
- nested tables are merged recursively
- scalar values in `--override` replace values from `--base`
- requires Python with stdlib `tomllib`

### codeblock-language-stats

Purpose:
Count fenced code block languages in a Markdown file.

Examples:

```bash
python python_helpers.py codeblock-language-stats --input README.md
```

```bash
python python_helpers.py codeblock-language-stats --input README.md --format json --output stats.json
```

Important notes:
- counts fenced code blocks only
- unnamed fences are reported as `<plain>`
- useful for documentation and mixed-language notes

### markdown-link-extract

Purpose:
Extract inline Markdown links and image links from a Markdown file.

Examples:

```bash
python python_helpers.py markdown-link-extract --input README.md
```

```bash
python python_helpers.py markdown-link-extract --input README.md --format json --output links.json
```

Important notes:
- scans inline links like `[text](target)`
- scans image links like `![alt](target)`
- classifies links as `external`, `email`, `anchor`, or `local`

### markdown-link-check

Purpose:
Check local Markdown links and heading anchors.

Examples:

```bash
python python_helpers.py markdown-link-check --input README.md
```

```bash
python python_helpers.py markdown-link-check --input README.md --root . --only-issues --format json
```

Important notes:
- external HTTP links are listed but not probed
- local file links are checked for file existence
- anchor-only links are checked against headings in the current file
- links like `file.md#anchor` try to validate both file and anchor

### file-hash-manifest

Purpose:
Create a path/size/hash manifest for a directory tree.

Examples:

```bash
python python_helpers.py file-hash-manifest --root . --format json --output manifest.json
```

```bash
python python_helpers.py file-hash-manifest --root . --ext md,txt --algorithm sha256
```

Important notes:
- useful for later diffing and duplicate analysis
- supports `md5`, `sha1`, and `sha256`
- JSON output is the preferred format for follow-up tools

### duplicate-line-finder

Purpose:
Find duplicate lines inside a text file.

Examples:

```bash
python python_helpers.py duplicate-line-finder --input keywords.txt
```

```bash
python python_helpers.py duplicate-line-finder --input keywords.txt --ignore-case --strip-ws --skip-empty
```

Important notes:
- reports count and line numbers
- useful for lists, tags, prompts, and URL collections
- can compare normalized lines with optional whitespace trimming and case folding

### markdown-word-count-by-heading

Purpose:
Count words for each Markdown heading section.

Examples:

```bash
python python_helpers.py markdown-word-count-by-heading --input README.md
```

```bash
python python_helpers.py markdown-word-count-by-heading --input notes.md --format json --output heading_counts.json
```

Important notes:
- counts words below each heading until the next same-level or higher-level heading
- useful for balancing long Markdown documents
- output includes line number, heading level, and word count

### manifest-diff

Purpose:
Compare two JSON file hash manifests.

Examples:

```bash
python python_helpers.py manifest-diff --base manifest_old.json --other manifest_new.json
```

```bash
python python_helpers.py manifest-diff --base manifest_old.json --other manifest_new.json --format json --output diff.json
```

Important notes:
- compares path, size, and hash
- reports added, removed, changed, and unchanged files
- expects JSON created by `file-hash-manifest`

### duplicate-file-finder

Purpose:
Find duplicate files by size and hash.

Examples:

```bash
python python_helpers.py duplicate-file-finder --root .
```

```bash
python python_helpers.py duplicate-file-finder --root . --ext jpg,png,webp --min-size 1024 --format json
```

Important notes:
- groups duplicates by `(size, hash)`
- reuses the same hashing logic as `file-hash-manifest`
- `--min-size` helps ignore trivial tiny files

### toml-key-flatten

Purpose:
Flatten nested TOML keys into dotted key paths.

Examples:

```bash
python python_helpers.py toml-key-flatten --input settings.toml
```

```bash
python python_helpers.py toml-key-flatten --input settings.toml --format json --output flat_keys.json
```

Important notes:
- requires Python with stdlib `tomllib`
- nested tables become dotted keys like `section.sub.key`
- useful for audits and config comparison

### json-to-toml

Purpose:
Convert a JSON object file to TOML.

Examples:

```bash
python python_helpers.py json-to-toml --input config.json
```

```bash
python python_helpers.py json-to-toml --input config.json --output config.toml
```

Important notes:
- the top-level JSON value must be an object
- supports nested tables
- supports arrays of tables for JSON arrays of objects

### markdown-image-inventory

Purpose:
Inventory Markdown and HTML image references from one file or a project tree.

Examples:

```bash
python python_helpers.py markdown-image-inventory --input README.md
```

```bash
python python_helpers.py markdown-image-inventory --root . --ext md,markdown --format json --output image_inventory.json
```

Important notes:
- extracts Markdown images and HTML `<img>` tags
- classifies targets as `external`, `email`, `anchor`, or `local`
- local files are checked by default unless `--no-verify-local` is used

### safe-batch-rename

Purpose:
Preview or apply safe batch renames for files.

Examples:

```bash
python python_helpers.py safe-batch-rename --root . --find old --replace new
```

```bash
python python_helpers.py safe-batch-rename --root . --prefix img_ --slugify --lowercase --apply
```

Important notes:
- works on file stems, not on directory names
- previews by default and applies only with `--apply`
- marks duplicate targets, existing targets, and rename cycles as conflicts

### text-frequency-report

Purpose:
Build a frequency report for words, tokens, or lines.

Examples:

```bash
python python_helpers.py text-frequency-report --input notes.txt --mode word --top-n 50
```

```bash
python python_helpers.py text-frequency-report --input prompts.txt --mode line --ignore-case --strip-ws --format json
```

Important notes:
- supports `word`, `token`, and `line` modes
- can limit by minimum length, minimum count, and top-N output
- useful for tags, prompt sets, keyword lists, and rough text analysis

### markdown-toc-generate

Purpose:
Generate a Markdown table of contents from headings.

Examples:

```bash
python python_helpers.py markdown-toc-generate --input README.md
```

```bash
python python_helpers.py markdown-toc-generate --input notes.md --min-level 2 --max-level 4 --skip-first-h1 --output toc.md
```

Important notes:
- generates Markdown bullet links from heading anchors
- heading range can be limited with `--min-level` and `--max-level`
- useful for large documentation files and content splitting

### json-key-flatten

Purpose:
Flatten JSON keys into dotted key paths.

Examples:

```bash
python python_helpers.py json-key-flatten --input data.json
```

```bash
python python_helpers.py json-key-flatten --input data.json --format json --output flat_keys.json
```

Important notes:
- the top-level JSON value must be an object
- nested objects become dotted paths
- arrays are represented with index segments like `[0]`

### unique-line-filter

Purpose:
Keep only the first unique occurrence of each line.

Examples:

```bash
python python_helpers.py unique-line-filter --input keywords.txt
```

```bash
python python_helpers.py unique-line-filter --input tags.txt --ignore-case --strip-ws --skip-empty --output unique_tags.txt
```

Important notes:
- keeps the first occurrence and removes later duplicates
- optional normalization can ignore case and surrounding whitespace
- useful for lists, tags, URL files, and prompt collections

### path-rewrite

Purpose:
Rewrite path prefixes across text files.

Examples:

```bash
python python_helpers.py path-rewrite --root . --from-prefix "assets/old/" --to-prefix "assets/new/"
```

```bash
python python_helpers.py path-rewrite --root . --from-prefix "C:\\Old\\Base" --to-prefix "D:\\New\\Base" --slash-style windows --apply --create-backup
```

Important notes:
- previews by default and writes only with `--apply`
- can normalize rewritten prefixes to `keep`, `posix`, or `windows`
- intended for path-prefix migrations across many text files

### filename-slugify-batch

Purpose:
Preview or apply slugified filename renames.

Examples:

```bash
python python_helpers.py filename-slugify-batch --root .
```

```bash
python python_helpers.py filename-slugify-batch --root . --ext jpg,png,webp --dedupe --lowercase-extension --apply
```

Important notes:
- normalizes file stems using the toolkit slugify rules
- previews by default and applies only with `--apply`
- `--dedupe` appends numeric suffixes to avoid duplicate targets inside the batch

## Extension Rules

When adding new tools, keep this structure:
- one focused tool function
- one CLI subcommand
- clear option names
- standard library only if possible
- short README entry with purpose and examples

Recommended internal pattern:
- `cmd_<toolname>()` for CLI entry
- reusable helper function below or above as needed
- add parser definition in `build_parser()`

## Maintenance Rule

This toolkit may be corrected, extended, or refactored whenever recurring work suggests it.
If a helper proves unstable or too narrow, adjust it instead of keeping dead weight.

## Suggested Future Additions

Potential next helpers:

## Practical Note

This file is intentionally a starter arsenal, not a finished final library.
It is meant to grow only where repeated real usage justifies growth.
