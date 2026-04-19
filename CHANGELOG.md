# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

Public repository note:
Some internal/private intermediate working states are not included in this public changelog.
That is intentional and keeps the public release history cleaner than the private working tree.

## [0.2.1] - 2026-04-19

### Added
- Added `markdown-table-normalize` for padded normalization of standard Markdown tables.
- Added `jsonl-to-json-array` for converting newline-delimited JSON into one formatted JSON array.
- Added `csv-column-select` for selecting and reordering CSV columns by header name or 1-based index.
- Added `xml-pretty` for validating and pretty-printing XML.
- Added `text-chunk-split` for splitting long text files into reusable numbered chunks.

### Changed
- Continued the CLI parser cleanup around the grouped registration structure and parser-driven metadata flow.
- Kept the generated documentation workflow centered on the real CLI parser so command lists, summaries, descriptions, examples, and arguments stay aligned.
- Expanded the generated README/command-reference coverage to include the newly added commands.

### Fixed
- Fixed Windows line-ending drift for generated/exported files by forcing LF output during file writes.
- Fixed README tool-detail coverage so commands present in the command reference are not missing from the README overview.

## [0.2.0] - 2026-04-18

### Added
- Added `export-cli-docs` to generate the README quick reference, full command reference, and README marker section from the real CLI parser metadata.
- Added a reusable README template workflow with marker-based CLI quick reference replacement.
- Added centralized CLI command metadata registration for grouped documentation output.
- Added explicit CLI examples in subcommand help output.

### Changed
- Refactored the CLI parser into grouped registration blocks with clear large comment markers for future command insertion.
- Centralized shared CLI argument helpers for scan, format, output, root, and encoding options.
- Switched the parser help formatter to show defaults consistently.
- Promoted `export-cli-docs` to the utility group and placed that group first in generated references.
- Updated generated command reference output to document CLI help coverage and parser-driven documentation sync.

### Fixed
- Fixed README/CLI drift by generating the quick reference and command reference from the same parser metadata.
- Fixed the documentation command examples to use the actual README template filename.
- Fixed command ordering for generated documentation so the documentation export command appears first.

## [0.1.4] - 2026-04-17

### Added
- Added `markdown-toc-generate` for Markdown TOC creation.
- Added `json-key-flatten` for flattened JSON key output.
- Added `unique-line-filter` for first-occurrence line deduplication.
- Added `path-rewrite` for path prefix migration across text files.
- Added `filename-slugify-batch` for safe filename normalization runs.

### Changed
- Refined README structure.

## [0.1.3] - 2026-04-17

### Added
- Added `toml-key-flatten` for flattened TOML key output.
- Added `json-to-toml` for JSON object to TOML conversion.
- Added `markdown-image-inventory` for Markdown and HTML image reference scans.
- Added `safe-batch-rename` for previewable batch file renames.
- Added `text-frequency-report` for word, token, and line frequency analysis.

### Changed
- Expanded Markdown and content-maintenance coverage.

## [0.1.2] - 2026-04-17

### Added
- Added `codeblock-language-stats` for fenced code block language counting.
- Added `markdown-link-extract` for Markdown link extraction.
- Added `markdown-link-check` for local Markdown link and anchor validation.
- Added `file-hash-manifest` for file integrity manifests.
- Added `duplicate-line-finder` for repeated line detection.
- Added `markdown-word-count-by-heading` for section-based Markdown word counts.
- Added `manifest-diff` for hash manifest comparisons.
- Added `duplicate-file-finder` for duplicate file detection by size and hash.

### Changed
- Expanded the toolkit from core project/text helpers toward broader audit and migration workflows.

## [0.1.1] - 2026-04-16

### Added
- Added `find-text` for multi-file literal and regex search.
- Added `safe-search-replace` for previewable multi-file replacement.
- Added `md-heading-index` for heading-based Markdown indexing.
- Added `split-markdown-sections` for heading-level Markdown file splitting.
- Added `project-manifest` for compact project summaries.
- Added `frontmatter-extract` and `frontmatter-remove` for simple Markdown frontmatter workflows.
- Added `csv-to-markdown` for padded Markdown table conversion.
- Added `toml-merge` for deep TOML merge operations.

### Changed
- Extended the initial helper set from basic file and config utilities into practical Markdown/content tooling.

## [0.1.0] - 2026-04-16

### Added
- Added `project-index` for lightweight project file indexing.
- Added `extract-section` for exact Markdown section extraction.
- Added `extract-codeblocks` for fenced code block extraction.
- Added `replace-between-markers` for marker-based block replacement.
- Added `ini-to-toml` for simple config migration.
- Added `normalize-text` for line ending and whitespace normalization.
- Added `json-pretty` for JSON validation and formatting.

### Notes
- Established the project as a compact, single-file, standard-library-only helper toolkit with CLI usage.