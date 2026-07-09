---
name: agentme-edr-policy-050-ml-dataset-structure
description: Defines the standard folder layout and file conventions for ML datasets used in AI/ML projects. Use when creating, organizing, or consuming datasets for machine learning tasks such as image labeling, document extraction, tabular data, LLM evaluation, and Q&A sets.
apply-to: ML and AI projects that produce or consume datasets
valid-from: 2026-05-27
---

# agentme-edr-policy-050: ML dataset structure

## Context and Problem Statement

ML projects accumulate datasets of different shapes: file-paired annotations, tabular CSVs, and complex per-record structures. Without a shared layout convention, tooling and agents cannot reliably discover schema files, consume data programmatically, or understand what a dataset contains.

How should ML datasets be organized on disk so they are self-describing, easy to consume, and consistent across dataset types?

## Decision Outcome

**A standard root layout with mandatory README.md and dataset.schema.json, plus type-specific conventions for data files**

Every dataset MUST live in its own named folder and include a README and a JSON Schema file. Data files are organized according to three dataset types, each with its own placement rule.

### Details

#### 01-root-structure-is-mandatory

Every dataset MUST follow this root layout:

```
/[name-of-dataset]/
    README.md
    dataset.schema.json
    data/              (present when dataset files are referenced by other data, or for file+annotation pairs)
    ...                (additional files depending on dataset type)
```

- `README.md` MUST explain what the dataset is about, the procedures used to create it, remarks on data quality, and instructions on how to consume it with examples.
- `dataset.schema.json` MUST be a valid [JSON Schema](https://json-schema.org/) document describing the structure of the dataset's primary data.
- The dataset folder name MUST be lowercase, using underscores as separators (e.g. `my_dataset`).

#### 02-file-annotation-pairs-must-use-data-folder

Datasets where each item is a file paired with structured JSON output (e.g. image labeling, document data extraction, medical records with known features) MUST store all files inside the `data/` subfolder. Each data file MUST have a sibling JSON annotation file named with the same filename suffixed with `.json`.

```
/[name-of-dataset]/
    data/
        image1.jpg
        image1.jpg.json
        docu.pdf
        docu.pdf.json
        case-123.json
        case-123.json.json
    dataset.schema.json    (defines the schema for the .json annotation files)
    README.md
```

Placing the annotation file next to its source file (same name + `.json`) keeps them adjacent even in large directories, making it easy to iterate pairs programmatically.

Subdirectories inside `data/` are allowed when the number of files warrants grouping, but the `.json` sibling convention MUST be preserved at each level.

Each `.json` annotation file MUST include a top-level `$schema` property whose value is the correct relative path to the dataset's root `dataset.schema.json`, accounting for subdirectory depth (e.g. `"$schema": "../dataset.schema.json"` at one level, `"../../dataset.schema.json"` at two levels). This is the standard editor-tooling convention for associating a JSON instance with its schema, and is validated by rule `06`.

#### 03-tabular-datasets-must-use-csv-files-at-root

Datasets composed of column-oriented tabular data MUST place CSV files at the root of the dataset folder. All tabular files MUST conform to the schema defined in `dataset.schema.json`, which MUST describe columns as named attributes with their types.

```
/[name-of-dataset]/
    samples-special.csv
    samples-simple.csv
    dataset.schema.json    (column definitions with types for all tabular files)
    README.md
```

Multiple CSV files are allowed when they represent different slices or splits of the same schema (e.g. train/test splits, subsets by source). All files in the same dataset MUST share the same column schema. Each row MUST also be validated by `make lint` per rule `06` — CSV has no `$schema` field (not applicable to that format), so only the row content is checked, not a schema pointer.

#### 04-complex-structured-datasets-must-use-per-entry-json-files

Datasets with complex or heterogeneous per-record structures (e.g. LLM workflow evaluation sets, Q&A pairs, input → expected_output pairs) MUST use one JSON file per entry, placed inside the `data/` subfolder. Each file MUST conform to the schema defined in `dataset.schema.json`.

```
/[name-of-dataset]/
    data/
        case-001.json
        case-002.json
    dataset.schema.json    (schema defining the structure of each entry file)
    README.md
```

Each entry file MUST include a top-level `$schema` property whose value is the correct relative path to the dataset's root `dataset.schema.json`, accounting for subdirectory depth (e.g. `"$schema": "../dataset.schema.json"` at one level, `"../../dataset.schema.json"` at two levels), validated by rule `06`.

Subdirectories inside `data/` are allowed for grouping entries by collection source, time period, actor, or similar dimensions when the number of files warrants it. ALL files in one dataset MUST conform to the SAME `dataset.schema.json` — if a project needs a different schema for a different set of entries, that MUST be a separate dataset (its own folder, README, and `dataset.schema.json`), not multiple schemas inside one dataset.

#### 05-referenced-files-must-live-in-data-folder

When any dataset type (tabular, per-entry JSON, or annotation-pair) contains references to external files as part of the data (e.g. an entry record that includes a file path), those referenced files MUST be stored inside the `data/` subfolder of the dataset. Paths inside data records MUST be relative to the dataset root.

#### 06-datasets-must-be-lint-validated-against-schema

Every dataset MUST expose a `make lint` target (in the Makefile of the project/component that owns the dataset) that validates its data against `dataset.schema.json` using the Python [`jsonschema`](https://pypi.org/project/jsonschema/) library:

- Per-entry JSON files (rule `04`) and annotation-pair `.json` siblings (rule `02`) MUST each be validated against `dataset.schema.json`, and their `$schema` property MUST be present and resolve to the dataset's actual schema file.
- CSV rows (rule `03`) MUST each be converted to a JSON object (column header → value) and validated against the same `dataset.schema.json`.
- `make lint` MUST list every violation found across all files/rows before exiting with a non-zero status (not fail-fast on the first violation).
- `jsonschema` MUST be declared as a normal project dependency per [agentme-edr-014](../application/014-python-project-tooling.md); no special-casing.

## References

- [JSON Schema specification](https://json-schema.org/)
- [jsonschema (Python library)](https://pypi.org/project/jsonschema/)
- [agentme-edr-014](../application/014-python-project-tooling.md) — Python project tooling and dependency conventions
