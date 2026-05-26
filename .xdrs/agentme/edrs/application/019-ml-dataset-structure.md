---
name: agentme-edr-policy-019-ml-dataset-structure
description: Defines the standard folder layout and file conventions for ML datasets used in AI/ML projects. Use when creating, organizing, or consuming datasets for machine learning tasks such as image labeling, document extraction, tabular data, LLM evaluation, and Q&A sets.
apply-to: ML and AI projects that produce or consume datasets
valid-from: 2026-05-27
---

# agentme-edr-policy-019: ML dataset structure

## Context and Problem Statement

ML projects accumulate datasets of different shapes: file-paired annotations, tabular CSVs, and structured JSONL records. Without a shared layout convention, tooling and agents cannot reliably discover schema files, consume data programmatically, or understand what a dataset contains.

How should ML datasets be organized on disk so they are self-describing, easy to consume, and consistent across dataset types?

## Decision Outcome

**A standard root layout with mandatory README.md and dataset.schema.json, plus type-specific conventions for data files**

Every dataset must live in its own named folder and include a README and a JSON Schema file. Data files are organized according to three dataset types, each with its own placement rule.

### Details

#### 01-root-structure-is-mandatory

Every dataset must follow this root layout:

```
/[name-of-dataset]/
    README.md
    dataset.schema.json
    data/              (present when dataset files are referenced by other data, or for file+annotation pairs)
    ...                (additional files depending on dataset type)
```

- `README.md` must explain what the dataset is about, the procedures used to create it, remarks on data quality, and instructions on how to consume it with examples.
- `dataset.schema.json` must be a valid [JSON Schema](https://json-schema.org/) document describing the structure of the dataset's primary data.
- The dataset folder name must be lowercase, using hyphens as separators.

#### 02-file-annotation-pairs-must-use-data-folder

Datasets where each item is a file paired with structured JSON output (e.g. image labeling, document data extraction, medical records with known features) must store all files inside the `data/` subfolder. Each data file must have a sibling JSON annotation file named with the same filename suffixed with `.json`.

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

Subdirectories inside `data/` are allowed when the number of files warrants grouping, but the `.json` sibling convention must be preserved at each level.

#### 03-tabular-datasets-must-use-csv-files-at-root

Datasets composed of column-oriented tabular data must place CSV files at the root of the dataset folder. All tabular files must conform to the schema defined in `dataset.schema.json`, which must describe columns as named attributes with their types.

```
/[name-of-dataset]/
    samples-special.csv
    samples-simple.csv
    dataset.schema.json    (column definitions with types for all tabular files)
    README.md
```

Multiple CSV files are allowed when they represent different slices or splits of the same schema (e.g. train/test splits, subsets by source). All files in the same dataset must share the same column schema.

#### 04-complex-structured-datasets-must-use-jsonl

Datasets with complex or heterogeneous per-record structures (e.g. LLM workflow evaluation sets, Q&A pairs, input → expected_output pairs) must use JSONL files (one JSON object per line) placed at the root of the dataset folder. Each line must conform to the schema defined in `dataset.schema.json`.

```
/[name-of-dataset]/
    simple-cases-test.jsonl
    edge-cases-test.jsonl
    dataset.schema.json    (schema defining the structure of each line in the JSONL files)
    README.md
```

Multiple JSONL files are allowed when they represent different splits or categories (e.g. easy vs. edge cases). All files in the same dataset must conform to the same line schema.

#### 05-referenced-files-must-live-in-data-folder

When any dataset type (tabular, JSONL, or annotation-pair) contains references to external files as part of the data (e.g. a JSONL record that includes a file path), those referenced files must be stored inside the `data/` subfolder of the dataset. Paths inside data records must be relative to the dataset root.

## References

- [JSON Schema specification](https://json-schema.org/)
- [JSONL format](https://jsonlines.org/)
