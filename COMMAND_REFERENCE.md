# Command Reference

This reference is generated from the real CLI parser metadata.

## CLI Help Coverage

- `python python-helpers-toolkit-text-markdown.py --help` lists all available commands.
- `python python-helpers-toolkit-text-markdown.py <command> --help` lists that command's parameters, defaults, choices, and examples.
- The same parser metadata drives this file, the README quick reference, and the live CLI help output.

## Command Index

### Utility / General Helpers

- [`export-cli-docs`](#export-cli-docs) - Export CLI quick reference and command reference.

### Markdown

- [`codeblock-language-stats`](#codeblock-language-stats) - Count fenced code block languages in Markdown.
- [`extract-codeblocks`](#extract-codeblocks) - Extract fenced code blocks from Markdown.
- [`extract-section`](#extract-section) - Extract a Markdown section by heading.
- [`frontmatter-extract`](#frontmatter-extract) - Extract a simple frontmatter block from Markdown.
- [`frontmatter-remove`](#frontmatter-remove) - Remove a leading frontmatter block from Markdown.
- [`markdown-image-inventory`](#markdown-image-inventory) - Inventory Markdown and HTML image references.
- [`markdown-link-check`](#markdown-link-check) - Check local Markdown links and anchors.
- [`markdown-link-extract`](#markdown-link-extract) - Extract Markdown inline links and images.
- [`markdown-table-normalize`](#markdown-table-normalize) - Normalize Markdown tables into padded stable output.
- [`markdown-toc-generate`](#markdown-toc-generate) - Generate a Markdown table of contents from headings.
- [`markdown-word-count-by-heading`](#markdown-word-count-by-heading) - Count words per Markdown heading section.
- [`md-heading-index`](#md-heading-index) - Build a Markdown heading index.
- [`split-markdown-sections`](#split-markdown-sections) - Split a Markdown file into heading-based section files.

### JSON / TOML / INI / CSV

- [`csv-column-select`](#csv-column-select) - Select and reorder CSV columns.
- [`csv-to-markdown`](#csv-to-markdown) - Convert CSV into a padded Markdown table.
- [`ini-to-toml`](#ini-to-toml) - Convert a simple INI file to TOML.
- [`json-key-flatten`](#json-key-flatten) - Flatten JSON keys into dotted paths.
- [`json-pretty`](#json-pretty) - Validate and pretty-print JSON.
- [`json-to-toml`](#json-to-toml) - Convert a JSON object file to TOML.
- [`jsonl-to-json-array`](#jsonl-to-json-array) - Convert JSONL into one JSON array.
- [`toml-key-flatten`](#toml-key-flatten) - Flatten TOML keys into dotted paths.
- [`toml-merge`](#toml-merge) - Deep-merge two TOML files.
- [`xml-pretty`](#xml-pretty) - Validate and pretty-print XML.

### Text / Cleanup

- [`duplicate-line-finder`](#duplicate-line-finder) - Find duplicate lines in a text file.
- [`find-text`](#find-text) - Find text matches across files.
- [`normalize-text`](#normalize-text) - Normalize line endings and whitespace.
- [`path-rewrite`](#path-rewrite) - Rewrite path prefixes across text files.
- [`replace-between-markers`](#replace-between-markers) - Replace text between two markers.
- [`safe-search-replace`](#safe-search-replace) - Replace text across files with dry-run support.
- [`text-chunk-split`](#text-chunk-split) - Split long text into reusable chunks.
- [`text-frequency-report`](#text-frequency-report) - Build a frequency report for words, tokens, or lines.
- [`unique-line-filter`](#unique-line-filter) - Keep only the first unique occurrence of each line.

### Files / Paths / Project Scans

- [`duplicate-file-finder`](#duplicate-file-finder) - Find duplicate files by size and hash.
- [`file-hash-manifest`](#file-hash-manifest) - Create a file hash manifest for a directory.
- [`filename-slugify-batch`](#filename-slugify-batch) - Preview or apply slugified filename renames.
- [`manifest-diff`](#manifest-diff) - Compare two JSON file hash manifests.
- [`project-index`](#project-index) - Create a lightweight file index.
- [`project-manifest`](#project-manifest) - Create a compact project manifest.
- [`safe-batch-rename`](#safe-batch-rename) - Preview or apply safe batch file renames.

## Utility / General Helpers

### export-cli-docs

Export CLI quick reference and command reference.

#### Description

Export CLI-driven documentation files from the real parser metadata registry.

#### Parameters

- `--quick-reference-output`
  - Required: no
  - Type: value
  - Notes: Optional output file for the generated README quick reference section.
- `--command-reference-output`
  - Required: no
  - Type: value
  - Notes: Optional output file for the generated full command reference.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py export-cli-docs --command-reference-output COMMAND_REFERENCE.md
```

```bash
python python-helpers-toolkit-text-markdown.py export-cli-docs --quick-reference-output README_QUICK_REFERENCE.md --command-reference-output COMMAND_REFERENCE.md
```

[Back to Command Index](#command-index)

## Markdown

### codeblock-language-stats

Count fenced code block languages in Markdown.

#### Description

Count fenced code blocks by language in a Markdown file.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Markdown input file.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py codeblock-language-stats --input README.md
```

```bash
python python-helpers-toolkit-text-markdown.py codeblock-language-stats --input README.md --format json --output stats.json
```

[Back to Command Index](#command-index)

### extract-codeblocks

Extract fenced code blocks from Markdown.

#### Description

Extract fenced code blocks from Markdown files.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Markdown input file.
- `--language`
  - Required: no
  - Type: value
  - Notes: Filter by code fence language.
- `--index`
  - Required: no
  - Type: int
  - Default: `1`
  - Notes: 1-based block index when not using --all.
- `--all`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Output all matching blocks combined.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--output-dir`
  - Required: no
  - Type: value
  - Notes: Write each matching block as a separate file.
- `--extension`
  - Required: no
  - Type: value
  - Notes: Extension used with --output-dir.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py extract-codeblocks --input notes.md --language python
```

```bash
python python-helpers-toolkit-text-markdown.py extract-codeblocks --input notes.md --language python --output-dir out_blocks --extension py
```

[Back to Command Index](#command-index)

### extract-section

Extract a Markdown section by heading.

#### Description

Extract one Markdown section by exact heading text.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Markdown input file.
- `--heading`
  - Required: yes
  - Type: value
  - Notes: Exact heading text without the leading # characters.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py extract-section --input README.md --heading Installation
```

```bash
python python-helpers-toolkit-text-markdown.py extract-section --input README.md --heading Usage --output usage.md
```

[Back to Command Index](#command-index)

### frontmatter-extract

Extract a simple frontmatter block from Markdown.

#### Description

Extract a simple leading frontmatter block and optionally write the remaining body.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Markdown input file.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `json`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional frontmatter output file.
- `--body-output`
  - Required: no
  - Type: value
  - Notes: Optional output file for the Markdown body without frontmatter.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py frontmatter-extract --input note.md
```

```bash
python python-helpers-toolkit-text-markdown.py frontmatter-extract --input note.md --format text --body-output body.md
```

[Back to Command Index](#command-index)

### frontmatter-remove

Remove a leading frontmatter block from Markdown.

#### Description

Remove a simple leading frontmatter block from a Markdown file.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Markdown input file.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file. If omitted, the input file is overwritten.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py frontmatter-remove --input note.md --output note_clean.md
```

[Back to Command Index](#command-index)

### markdown-image-inventory

Inventory Markdown and HTML image references.

#### Description

Inventory Markdown and HTML image references from one file or a project tree.

#### Parameters

- `--input`
  - Required: no
  - Type: value
  - Notes: Single Markdown input file.
- `--root`
  - Required: no
  - Type: value
  - Notes: Project root directory to scan for Markdown files.
- `--ext`
  - Required: no
  - Type: value
  - Notes: Include only these extensions, comma-separated or repeated.
- `--ignore-dir`
  - Required: no
  - Type: value
  - Notes: Additional directory names to ignore.
- `--ignore`
  - Required: no
  - Type: value
  - Notes: Ignore path patterns, e.g. '*.log,cache/*'.
- `--max-depth`
  - Required: no
  - Type: int
  - Notes: Maximum relative depth below --root.
- `--max-files`
  - Required: no
  - Type: int
  - Notes: Stop scanning after N files.
- `--include-hidden`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Include hidden files and folders.
- `--no-verify-local`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Do not check local file existence.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py markdown-image-inventory --input README.md
```

```bash
python python-helpers-toolkit-text-markdown.py markdown-image-inventory --root . --ext md,markdown --format json --output image_inventory.json
```

[Back to Command Index](#command-index)

### markdown-link-check

Check local Markdown links and anchors.

#### Description

Check local Markdown links and local heading anchors without probing external HTTP targets.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Markdown input file.
- `--root`
  - Required: no
  - Type: value
  - Notes: Optional project root used for local link resolution.
- `--only-issues`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Show only missing or warning results.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py markdown-link-check --input README.md
```

```bash
python python-helpers-toolkit-text-markdown.py markdown-link-check --input README.md --root . --only-issues --format json
```

[Back to Command Index](#command-index)

### markdown-link-extract

Extract Markdown inline links and images.

#### Description

Extract inline Markdown links and image references from a Markdown file.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Markdown input file.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py markdown-link-extract --input README.md
```

```bash
python python-helpers-toolkit-text-markdown.py markdown-link-extract --input README.md --format json --output links.json
```

[Back to Command Index](#command-index)

### markdown-table-normalize

Normalize Markdown tables into padded stable output.

#### Description

Detect standard Markdown tables and rewrite them with padded aligned columns.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Markdown input file.
- `--min-columns`
  - Required: no
  - Type: int
  - Default: `2`
  - Notes: Minimum number of columns required for table detection.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file. If omitted, the input file is overwritten.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py markdown-table-normalize --input README.md
```

```bash
python python-helpers-toolkit-text-markdown.py markdown-table-normalize --input tables.md --min-columns 3 --output tables_clean.md
```

[Back to Command Index](#command-index)

### markdown-toc-generate

Generate a Markdown table of contents from headings.

#### Description

Generate a Markdown table of contents based on document headings.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Markdown input file.
- `--min-level`
  - Required: no
  - Type: int
  - Default: `2`
  - Notes: Minimum heading level to include.
- `--max-level`
  - Required: no
  - Type: int
  - Default: `6`
  - Notes: Maximum heading level to include.
- `--skip-first-h1`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Skip the first H1 heading.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py markdown-toc-generate --input README.md
```

```bash
python python-helpers-toolkit-text-markdown.py markdown-toc-generate --input notes.md --min-level 2 --max-level 4 --skip-first-h1 --output toc.md
```

[Back to Command Index](#command-index)

### markdown-word-count-by-heading

Count words per Markdown heading section.

#### Description

Count words below each Markdown heading until the next sibling or parent-level heading.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Markdown input file.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py markdown-word-count-by-heading --input README.md
```

```bash
python python-helpers-toolkit-text-markdown.py markdown-word-count-by-heading --input notes.md --format json --output heading_counts.json
```

[Back to Command Index](#command-index)

### md-heading-index

Build a Markdown heading index.

#### Description

Build an index of Markdown headings with line numbers and anchors.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Markdown input file.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py md-heading-index --input README.md
```

```bash
python python-helpers-toolkit-text-markdown.py md-heading-index --input README.md --format json --output heading_index.json
```

[Back to Command Index](#command-index)

### split-markdown-sections

Split a Markdown file into heading-based section files.

#### Description

Split a Markdown file into multiple section files based on one heading level.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Markdown input file.
- `--level`
  - Required: no
  - Type: int
  - Default: `2`
  - Notes: Heading level to split on, e.g. 2 for ##.
- `--output-dir`
  - Required: yes
  - Type: value
  - Notes: Target directory for the generated section files.
- `--prefix`
  - Required: no
  - Type: value
  - Notes: Optional filename prefix.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py split-markdown-sections --input README.md --level 2 --output-dir out_sections
```

```bash
python python-helpers-toolkit-text-markdown.py split-markdown-sections --input notes.md --level 3 --output-dir out_sections --prefix part
```

[Back to Command Index](#command-index)

## JSON / TOML / INI / CSV

### csv-column-select

Select and reorder CSV columns.

#### Description

Select a subset of CSV columns by header name or 1-based index and write a reduced CSV file.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: CSV input file.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional CSV output file.
- `--columns`
  - Required: yes
  - Type: value
  - Notes: Comma-separated header names or 1-based column indexes.
- `--delimiter`
  - Required: no
  - Type: value
  - Default: `,`
  - Notes: CSV delimiter character.
- `--quotechar`
  - Required: no
  - Type: value
  - Default: `"`
  - Notes: CSV quote character.
- `--no-header`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Treat the CSV as headerless input and require numeric columns.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py csv-column-select --input table.csv --columns title,url,date --output slim.csv
```

```bash
python python-helpers-toolkit-text-markdown.py csv-column-select --input table.csv --columns 1,4,2 --no-header --output reordered.csv
```

[Back to Command Index](#command-index)

### csv-to-markdown

Convert CSV into a padded Markdown table.

#### Description

Convert CSV input into a padded Markdown table.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: CSV input file.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional Markdown output file.
- `--delimiter`
  - Required: no
  - Type: value
  - Default: `,`
  - Notes: CSV delimiter character.
- `--quotechar`
  - Required: no
  - Type: value
  - Default: `"`
  - Notes: CSV quote character.
- `--no-header`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Treat the CSV as headerless input.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py csv-to-markdown --input table.csv
```

```bash
python python-helpers-toolkit-text-markdown.py csv-to-markdown --input table.csv --delimiter ";" --output table.md
```

[Back to Command Index](#command-index)

### ini-to-toml

Convert a simple INI file to TOML.

#### Description

Convert a simple INI file to TOML using lightweight value inference.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: INI input file.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional TOML output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py ini-to-toml --input settings.ini --output settings.toml
```

[Back to Command Index](#command-index)

### json-key-flatten

Flatten JSON keys into dotted paths.

#### Description

Flatten nested JSON keys into dotted paths with array indices.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: JSON input file.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py json-key-flatten --input data.json
```

```bash
python python-helpers-toolkit-text-markdown.py json-key-flatten --input data.json --format json --output flat_keys.json
```

[Back to Command Index](#command-index)

### json-pretty

Validate and pretty-print JSON.

#### Description

Validate a JSON file and pretty-print it in a stable readable format.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: JSON input file.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--indent`
  - Required: no
  - Type: int
  - Default: `2`
  - Notes: Indentation width for the JSON output.
- `--sort-keys`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Sort object keys alphabetically.
- `--ensure-ascii`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Escape non-ASCII characters in the output.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py json-pretty --input data.json
```

```bash
python python-helpers-toolkit-text-markdown.py json-pretty --input data.json --sort-keys --output data_pretty.json
```

[Back to Command Index](#command-index)

### json-to-toml

Convert a JSON object file to TOML.

#### Description

Convert a JSON object file to TOML.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: JSON input file.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional TOML output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py json-to-toml --input config.json
```

```bash
python python-helpers-toolkit-text-markdown.py json-to-toml --input config.json --output config.toml
```

[Back to Command Index](#command-index)

### jsonl-to-json-array

Convert JSONL into one JSON array.

#### Description

Read newline-delimited JSON and write one pretty-printed JSON array.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: JSONL input file.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional JSON output file.
- `--skip-invalid`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Skip invalid JSONL rows instead of failing immediately.
- `--max-lines`
  - Required: no
  - Type: int
  - Notes: Optional maximum number of input lines to process.
- `--indent`
  - Required: no
  - Type: int
  - Default: `2`
  - Notes: Indentation width for the JSON array output.
- `--ensure-ascii`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Escape non-ASCII characters in the output.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py jsonl-to-json-array --input records.jsonl --output records.json
```

```bash
python python-helpers-toolkit-text-markdown.py jsonl-to-json-array --input records.jsonl --skip-invalid --indent 2
```

[Back to Command Index](#command-index)

### toml-key-flatten

Flatten TOML keys into dotted paths.

#### Description

Flatten nested TOML keys into dotted path output for audits and comparisons.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: TOML input file.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py toml-key-flatten --input settings.toml
```

```bash
python python-helpers-toolkit-text-markdown.py toml-key-flatten --input settings.toml --format json --output flat_keys.json
```

[Back to Command Index](#command-index)

### toml-merge

Deep-merge two TOML files.

#### Description

Deep-merge two TOML files where override values replace base values.

#### Parameters

- `--base`
  - Required: yes
  - Type: value
  - Notes: Base TOML file.
- `--override`
  - Required: yes
  - Type: value
  - Notes: Override TOML file.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional merged TOML output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py toml-merge --base default.toml --override local.toml
```

```bash
python python-helpers-toolkit-text-markdown.py toml-merge --base default.toml --override local.toml --output merged.toml
```

[Back to Command Index](#command-index)

### xml-pretty

Validate and pretty-print XML.

#### Description

Validate XML input and rewrite it in a stable indented layout.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: XML input file.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional XML output file.
- `--indent`
  - Required: no
  - Type: int
  - Default: `2`
  - Notes: Indentation width for pretty-printed XML output.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py xml-pretty --input sitemap.xml
```

```bash
python python-helpers-toolkit-text-markdown.py xml-pretty --input export.xml --indent 4 --output export_pretty.xml
```

[Back to Command Index](#command-index)

## Text / Cleanup

### duplicate-line-finder

Find duplicate lines in a text file.

#### Description

Find duplicate lines inside a text file.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Input text file.
- `--ignore-case`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Compare lines case-insensitively.
- `--strip-ws`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Trim surrounding whitespace before comparing.
- `--skip-empty`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Ignore empty lines.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py duplicate-line-finder --input keywords.txt
```

```bash
python python-helpers-toolkit-text-markdown.py duplicate-line-finder --input keywords.txt --ignore-case --strip-ws --skip-empty
```

[Back to Command Index](#command-index)

### find-text

Find text matches across files.

#### Description

Find literal text or regex matches across multiple files.

#### Parameters

- `--root`
  - Required: yes
  - Type: value
  - Notes: Root directory to scan.
- `--query`
  - Required: yes
  - Type: value
  - Notes: Literal text or regex pattern to find.
- `--ext`
  - Required: no
  - Type: value
  - Notes: Include only these extensions, comma-separated or repeated.
- `--ignore-dir`
  - Required: no
  - Type: value
  - Notes: Additional directory names to ignore.
- `--ignore`
  - Required: no
  - Type: value
  - Notes: Ignore path patterns, e.g. '*.log,cache/*'.
- `--max-depth`
  - Required: no
  - Type: int
  - Notes: Maximum relative depth below --root.
- `--max-files`
  - Required: no
  - Type: int
  - Notes: Stop scanning after N files.
- `--include-hidden`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Include hidden files and folders.
- `--max-matches`
  - Required: no
  - Type: int
  - Notes: Stop after N total matches.
- `--regex`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Treat --query as a regular expression.
- `--case-sensitive`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Use case-sensitive matching.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py find-text --root . --query TODO --ext py,md
```

```bash
python python-helpers-toolkit-text-markdown.py find-text --root . --query "class\s+\w+" --ext py --regex --format json
```

[Back to Command Index](#command-index)

### normalize-text

Normalize line endings and whitespace.

#### Description

Normalize line endings, trim trailing whitespace, and optionally expand tabs.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Input text file.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file. If omitted, the input file is overwritten.
- `--line-ending`
  - Required: no
  - Type: choice
  - Choices: lf, crlf
  - Default: `lf`
  - Notes: Target line ending style.
- `--keep-trailing-ws`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Keep trailing whitespace.
- `--no-final-newline`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Do not force a final newline.
- `--expand-tabs`
  - Required: no
  - Type: int
  - Notes: Expand tabs to spaces using this tab size.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py normalize-text --input README.md --line-ending lf
```

```bash
python python-helpers-toolkit-text-markdown.py normalize-text --input script.py --expand-tabs 4 --output script_clean.py
```

[Back to Command Index](#command-index)

### path-rewrite

Rewrite path prefixes across text files.

#### Description

Rewrite path prefixes across multiple text files with preview or apply mode.

#### Parameters

- `--root`
  - Required: yes
  - Type: value
  - Notes: Project root directory.
- `--from-prefix`
  - Required: yes
  - Type: value
  - Notes: Source path prefix to replace.
- `--to-prefix`
  - Required: yes
  - Type: value
  - Notes: Target path prefix.
- `--ext`
  - Required: no
  - Type: value
  - Notes: Include only these extensions, comma-separated or repeated.
- `--ignore-dir`
  - Required: no
  - Type: value
  - Notes: Additional directory names to ignore.
- `--ignore`
  - Required: no
  - Type: value
  - Notes: Ignore path patterns, e.g. '*.log,cache/*'.
- `--max-depth`
  - Required: no
  - Type: int
  - Notes: Maximum relative depth below --root.
- `--max-files`
  - Required: no
  - Type: int
  - Notes: Stop scanning after N files.
- `--include-hidden`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Include hidden files and folders.
- `--slash-style`
  - Required: no
  - Type: choice
  - Choices: keep, posix, windows
  - Default: `keep`
  - Notes: Slash style for rewritten paths.
- `--case-sensitive`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Use case-sensitive matching.
- `--create-backup`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Write .bak files before modifying originals.
- `--apply`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Apply the rewrite. Without this flag only preview is performed.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py path-rewrite --root . --from-prefix "assets/old/" --to-prefix "assets/new/"
```

```bash
python python-helpers-toolkit-text-markdown.py path-rewrite --root . --from-prefix "C:\Old\Base" --to-prefix "D:\New\Base" --slash-style windows --apply --create-backup
```

[Back to Command Index](#command-index)

### replace-between-markers

Replace text between two markers.

#### Description

Replace the content between two known start and end markers.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Target file.
- `--start-marker`
  - Required: yes
  - Type: value
  - Notes: Marker where replacement starts.
- `--end-marker`
  - Required: yes
  - Type: value
  - Notes: Marker where replacement ends.
- `--replacement-text`
  - Required: no
  - Type: value
  - Notes: Replacement text passed directly on the CLI.
- `--replacement-file`
  - Required: no
  - Type: value
  - Notes: Read replacement text from this file.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file. If omitted, the input file is overwritten.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py replace-between-markers --input app.js --start-marker "/* START */" --end-marker "/* END */" --replacement-file new_block.txt
```

```bash
python python-helpers-toolkit-text-markdown.py replace-between-markers --input config.md --start-marker "<!-- START -->" --end-marker "<!-- END -->" --replacement-text "New content"
```

[Back to Command Index](#command-index)

### safe-search-replace

Replace text across files with dry-run support.

#### Description

Replace text across multiple files with optional dry-run and backup support.

#### Parameters

- `--root`
  - Required: yes
  - Type: value
  - Notes: Root directory to scan.
- `--query`
  - Required: yes
  - Type: value
  - Notes: Literal text or regex pattern to replace.
- `--replacement`
  - Required: yes
  - Type: value
  - Notes: Replacement text.
- `--ext`
  - Required: no
  - Type: value
  - Notes: Include only these extensions, comma-separated or repeated.
- `--ignore-dir`
  - Required: no
  - Type: value
  - Notes: Additional directory names to ignore.
- `--ignore`
  - Required: no
  - Type: value
  - Notes: Ignore path patterns, e.g. '*.log,cache/*'.
- `--max-depth`
  - Required: no
  - Type: int
  - Notes: Maximum relative depth below --root.
- `--max-files`
  - Required: no
  - Type: int
  - Notes: Stop scanning after N files.
- `--include-hidden`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Include hidden files and folders.
- `--regex`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Treat --query as a regular expression.
- `--case-sensitive`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Use case-sensitive matching.
- `--dry-run`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Only report changes without writing files.
- `--create-backup`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Write .bak files before modifying originals.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional report output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py safe-search-replace --root . --query foo --replacement bar --ext py --dry-run
```

```bash
python python-helpers-toolkit-text-markdown.py safe-search-replace --root . --query "foo\((.*?)\)" --replacement "bar(\1)" --ext py --regex --create-backup
```

[Back to Command Index](#command-index)

### text-chunk-split

Split long text into reusable chunks.

#### Description

Split a text file into numbered chunks by characters, words, or lines.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Input text file.
- `--output-dir`
  - Required: yes
  - Type: value
  - Notes: Target directory for generated chunk files.
- `--mode`
  - Required: no
  - Type: choice
  - Choices: chars, words, lines
  - Default: `chars`
  - Notes: Chunking mode.
- `--max-size`
  - Required: yes
  - Type: int
  - Notes: Maximum chunk size measured in the selected mode.
- `--overlap`
  - Required: no
  - Type: int
  - Notes: Overlap size between adjacent chunks in the selected mode.
- `--prefix`
  - Required: no
  - Type: value
  - Default: `chunk`
  - Notes: Filename prefix for generated chunk files.
- `--extension`
  - Required: no
  - Type: value
  - Default: `txt`
  - Notes: Filename extension for generated chunk files.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py text-chunk-split --input big.txt --output-dir out_chunks --mode words --max-size 400
```

```bash
python python-helpers-toolkit-text-markdown.py text-chunk-split --input big.txt --output-dir out_chunks --mode chars --max-size 2000 --overlap 200
```

[Back to Command Index](#command-index)

### text-frequency-report

Build a frequency report for words, tokens, or lines.

#### Description

Build a frequency report for words, tokens, or lines in a text file.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Input text file.
- `--mode`
  - Required: no
  - Type: choice
  - Choices: word, token, line
  - Default: `word`
  - Notes: Frequency mode to use.
- `--ignore-case`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Compare items case-insensitively.
- `--strip-ws`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Trim surrounding whitespace before counting.
- `--min-length`
  - Required: no
  - Type: int
  - Default: `1`
  - Notes: Ignore items shorter than this length.
- `--min-count`
  - Required: no
  - Type: int
  - Default: `1`
  - Notes: Ignore items below this count.
- `--top-n`
  - Required: no
  - Type: int
  - Notes: Limit output to the top N rows.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py text-frequency-report --input notes.txt --mode word --top-n 50
```

```bash
python python-helpers-toolkit-text-markdown.py text-frequency-report --input prompts.txt --mode line --ignore-case --strip-ws --format json
```

[Back to Command Index](#command-index)

### unique-line-filter

Keep only the first unique occurrence of each line.

#### Description

Keep only the first unique occurrence of each line from a text file.

#### Parameters

- `--input`
  - Required: yes
  - Type: value
  - Notes: Input text file.
- `--ignore-case`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Compare lines case-insensitively.
- `--strip-ws`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Trim surrounding whitespace before comparing.
- `--skip-empty`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Ignore empty lines completely.
- `--sort-output`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Sort the unique output lines.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py unique-line-filter --input keywords.txt
```

```bash
python python-helpers-toolkit-text-markdown.py unique-line-filter --input tags.txt --ignore-case --strip-ws --skip-empty --output unique_tags.txt
```

[Back to Command Index](#command-index)

## Files / Paths / Project Scans

### duplicate-file-finder

Find duplicate files by size and hash.

#### Description

Find duplicate files by size and hash across a directory tree.

#### Parameters

- `--root`
  - Required: yes
  - Type: value
  - Notes: Project root directory.
- `--ext`
  - Required: no
  - Type: value
  - Notes: Include only these extensions, comma-separated or repeated.
- `--ignore-dir`
  - Required: no
  - Type: value
  - Notes: Additional directory names to ignore.
- `--ignore`
  - Required: no
  - Type: value
  - Notes: Ignore path patterns, e.g. '*.log,cache/*'.
- `--max-depth`
  - Required: no
  - Type: int
  - Notes: Maximum relative depth below --root.
- `--max-files`
  - Required: no
  - Type: int
  - Notes: Stop scanning after N files.
- `--include-hidden`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Include hidden files and folders.
- `--algorithm`
  - Required: no
  - Type: choice
  - Choices: md5, sha1, sha256
  - Default: `sha256`
  - Notes: Hash algorithm used for duplicate detection.
- `--min-size`
  - Required: no
  - Type: int
  - Default: `1`
  - Notes: Ignore files smaller than this byte size.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py duplicate-file-finder --root .
```

```bash
python python-helpers-toolkit-text-markdown.py duplicate-file-finder --root . --ext jpg,png,webp --min-size 1024 --format json
```

[Back to Command Index](#command-index)

### file-hash-manifest

Create a file hash manifest for a directory.

#### Description

Create a file hash manifest for a directory tree.

#### Parameters

- `--root`
  - Required: yes
  - Type: value
  - Notes: Project root directory.
- `--ext`
  - Required: no
  - Type: value
  - Notes: Include only these extensions, comma-separated or repeated.
- `--ignore-dir`
  - Required: no
  - Type: value
  - Notes: Additional directory names to ignore.
- `--ignore`
  - Required: no
  - Type: value
  - Notes: Ignore path patterns, e.g. '*.log,cache/*'.
- `--max-depth`
  - Required: no
  - Type: int
  - Notes: Maximum relative depth below --root.
- `--max-files`
  - Required: no
  - Type: int
  - Notes: Stop scanning after N files.
- `--include-hidden`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Include hidden files and folders.
- `--algorithm`
  - Required: no
  - Type: choice
  - Choices: md5, sha1, sha256
  - Default: `sha256`
  - Notes: Hash algorithm used for each file.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `json`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py file-hash-manifest --root . --format json --output manifest.json
```

```bash
python python-helpers-toolkit-text-markdown.py file-hash-manifest --root . --ext md,txt --algorithm sha256
```

[Back to Command Index](#command-index)

### filename-slugify-batch

Preview or apply slugified filename renames.

#### Description

Preview or apply slugified filename renames using the toolkit slugify rules.

#### Parameters

- `--root`
  - Required: yes
  - Type: value
  - Notes: Project root directory.
- `--ext`
  - Required: no
  - Type: value
  - Notes: Include only these extensions, comma-separated or repeated.
- `--ignore-dir`
  - Required: no
  - Type: value
  - Notes: Additional directory names to ignore.
- `--ignore`
  - Required: no
  - Type: value
  - Notes: Ignore path patterns, e.g. '*.log,cache/*'.
- `--max-depth`
  - Required: no
  - Type: int
  - Notes: Maximum relative depth below --root.
- `--max-files`
  - Required: no
  - Type: int
  - Notes: Stop scanning after N files.
- `--include-hidden`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Include hidden files and folders.
- `--lowercase-extension`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Lowercase the file extension.
- `--dedupe`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Append numeric suffixes to avoid duplicate targets inside the batch.
- `--apply`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Apply the planned renames.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py filename-slugify-batch --root .
```

```bash
python python-helpers-toolkit-text-markdown.py filename-slugify-batch --root . --ext jpg,png,webp --dedupe --lowercase-extension --apply
```

[Back to Command Index](#command-index)

### manifest-diff

Compare two JSON file hash manifests.

#### Description

Compare two JSON file hash manifests generated by file-hash-manifest.

#### Parameters

- `--base`
  - Required: yes
  - Type: value
  - Notes: Base manifest JSON file.
- `--other`
  - Required: yes
  - Type: value
  - Notes: Other manifest JSON file.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py manifest-diff --base manifest_old.json --other manifest_new.json
```

```bash
python python-helpers-toolkit-text-markdown.py manifest-diff --base manifest_old.json --other manifest_new.json --format json --output diff.json
```

[Back to Command Index](#command-index)

### project-index

Create a lightweight file index.

#### Description

Create a lightweight file index for a project root.

#### Parameters

- `--root`
  - Required: yes
  - Type: value
  - Notes: Project root directory.
- `--ext`
  - Required: no
  - Type: value
  - Notes: Include only these extensions, comma-separated or repeated.
- `--ignore-dir`
  - Required: no
  - Type: value
  - Notes: Additional directory names to ignore.
- `--ignore`
  - Required: no
  - Type: value
  - Notes: Ignore path patterns, e.g. '*.log,cache/*'.
- `--max-depth`
  - Required: no
  - Type: int
  - Notes: Maximum relative depth below --root.
- `--max-files`
  - Required: no
  - Type: int
  - Notes: Stop scanning after N files.
- `--include-hidden`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Include hidden files and folders.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py project-index --root . --ext py,md,js --format text
```

```bash
python python-helpers-toolkit-text-markdown.py project-index --root . --ext py,md --format json --output project_index.json
```

[Back to Command Index](#command-index)

### project-manifest

Create a compact project manifest.

#### Description

Create a compact project manifest with suffix statistics and largest files.

#### Parameters

- `--root`
  - Required: yes
  - Type: value
  - Notes: Project root directory.
- `--ext`
  - Required: no
  - Type: value
  - Notes: Include only these extensions, comma-separated or repeated.
- `--ignore-dir`
  - Required: no
  - Type: value
  - Notes: Additional directory names to ignore.
- `--ignore`
  - Required: no
  - Type: value
  - Notes: Ignore path patterns, e.g. '*.log,cache/*'.
- `--max-depth`
  - Required: no
  - Type: int
  - Notes: Maximum relative depth below --root.
- `--max-files`
  - Required: no
  - Type: int
  - Notes: Stop scanning after N files.
- `--include-hidden`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Include hidden files and folders.
- `--top-n`
  - Required: no
  - Type: int
  - Default: `10`
  - Notes: Number of largest files to include.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py project-manifest --root . --ext py,md,js
```

```bash
python python-helpers-toolkit-text-markdown.py project-manifest --root . --format json --output manifest.json
```

[Back to Command Index](#command-index)

### safe-batch-rename

Preview or apply safe batch file renames.

#### Description

Preview or apply safe batch file renames based on stem transformations.

#### Parameters

- `--root`
  - Required: yes
  - Type: value
  - Notes: Project root directory.
- `--ext`
  - Required: no
  - Type: value
  - Notes: Include only these extensions, comma-separated or repeated.
- `--ignore-dir`
  - Required: no
  - Type: value
  - Notes: Additional directory names to ignore.
- `--ignore`
  - Required: no
  - Type: value
  - Notes: Ignore path patterns, e.g. '*.log,cache/*'.
- `--max-depth`
  - Required: no
  - Type: int
  - Notes: Maximum relative depth below --root.
- `--max-files`
  - Required: no
  - Type: int
  - Notes: Stop scanning after N files.
- `--include-hidden`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Include hidden files and folders.
- `--find`
  - Required: no
  - Type: value
  - Notes: Literal text to replace in the filename stem.
- `--replace`
  - Required: no
  - Type: value
  - Default: ``
  - Notes: Replacement text for --find or --regex.
- `--regex`
  - Required: no
  - Type: value
  - Notes: Regex pattern applied to the filename stem.
- `--prefix`
  - Required: no
  - Type: value
  - Notes: Prefix added to the filename stem.
- `--suffix`
  - Required: no
  - Type: value
  - Notes: Suffix added to the filename stem before the extension.
- `--lowercase`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Lowercase the filename stem.
- `--slugify`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Normalize the filename stem to a safe slug.
- `--lowercase-extension`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Lowercase the file extension.
- `--apply`
  - Required: no
  - Type: flag
  - Default: `False`
  - Notes: Apply the planned renames.
- `--format`
  - Required: no
  - Type: choice
  - Choices: text, json
  - Default: `text`
  - Notes: Output format for generated results.
- `--output`
  - Required: no
  - Type: value
  - Notes: Optional output file.
- `--encoding`
  - Required: no
  - Type: value
  - Default: `utf-8`
  - Notes: Text encoding used for reading and writing.

#### Examples

```bash
python python-helpers-toolkit-text-markdown.py safe-batch-rename --root . --find old --replace new
```

```bash
python python-helpers-toolkit-text-markdown.py safe-batch-rename --root . --prefix img_ --slugify --lowercase --apply
```

[Back to Command Index](#command-index)
