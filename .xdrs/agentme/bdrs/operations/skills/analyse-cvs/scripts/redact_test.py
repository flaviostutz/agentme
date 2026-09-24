# Python 3.9+ pytest suite; run with: uv run --no-project --with pytest pytest scripts
import json

import pytest
import redact

LABELLED = [
    ("date_of_birth", "Date of birth", "12 March 1990"),
    ("date_of_birth", "Geboortedatum", "12-03-1990"),
    ("date_of_birth", "Data de nascimento", "12/03/1990"),
    ("date_of_birth", "Geburtsdatum", "12.03.1990"),
    ("date_of_birth", "Date de naissance", "12/03/1990"),
    ("date_of_birth", "Fecha de nacimiento", "12/03/1990"),
    ("date_of_birth", "Age", "34"),
    ("date_of_birth", "Âge", "34 ans"),
    ("gender", "Gender", "Female"),
    ("gender", "Geslacht", "Vrouw"),
    ("gender", "Sexo", "Feminino"),
    ("gender", "Geschlecht", "weiblich"),
    ("gender", "Sexe", "Féminin"),
    ("gender", "Género", "Femenino"),
    ("nationality", "Nationality", "Brazilian"),
    ("nationality", "Nationaliteit", "Nederlandse"),
    ("nationality", "Nacionalidade", "Brasileira"),
    ("nationality", "Staatsangehörigkeit", "deutsch"),
    ("nationality", "Nationalité", "française"),
    ("nationality", "Nacionalidad", "española"),
    ("ethnicity", "Ethnicity", "Hispanic"),
    ("marital_status", "Marital status", "Married"),
    ("marital_status", "Burgerlijke staat", "Gehuwd"),
    ("marital_status", "Estado civil", "Casada"),
    ("marital_status", "Familienstand", "verheiratet"),
    ("marital_status", "Situation familiale", "Mariée"),
    ("children", "Children", "2"),
    ("children", "Kinderen", "2"),
    ("children", "Filhos", "2"),
    ("children", "Kinder", "2"),
    ("children", "Enfants", "2"),
    ("children", "Hijos", "2"),
    ("religion", "Religion", "Catholic"),
    ("religion", "Religie", "Katholiek"),
    ("religion", "Religião", "Católica"),
    ("religion", "Konfession", "katholisch"),
    ("religion", "Religión", "Católica"),
    ("health", "Health", "Diabetic"),
    ("health", "Gezondheid", "Goed"),
    ("health", "Deficiência", "Nenhuma"),
    ("health", "Behinderung", "keine"),
    ("health", "Santé", "Bonne"),
    ("health", "Discapacidad", "Ninguna"),
    ("political", "Political affiliation", "Green party"),
    ("political", "Politieke voorkeur", "GroenLinks"),
    ("political", "Filiação política", "Nenhuma"),
    ("political", "Parteizugehörigkeit", "keine"),
    ("political", "Affiliation politique", "Aucune"),
    ("political", "Afiliación política", "Ninguna"),
]


@pytest.mark.parametrize("category,label,value", LABELLED)
def test_labelled_field_redacted(category, label, value):
    text, counts = redact.redact(f"{label}: {value}\n")
    assert text == f"{label}: [REDACTED]\n"
    assert counts[category] == 1


@pytest.mark.parametrize("line,expected", [
    ("- **Date of birth:** 12 March 1990", "- **Date of birth:** [REDACTED]"),
    ("**Nationality**: Dutch", "**Nationality**: [REDACTED]"),
    ("| Marital status | Married |", "| Marital status | [REDACTED] |"),
    ("* Gender: Male", "* Gender: [REDACTED]"),
    ("DOB: 1990-03-12", "DOB: [REDACTED]"),
])
def test_label_formats(line, expected):
    assert redact.redact(line)[0] == expected


@pytest.mark.parametrize("image", [
    "![photo](data:image/png;base64,AAAA)",
    "![](images/jane.jpg)",
    "![Jane][photo-ref]",
    '<img src="jane.png" alt="Jane">',
])
def test_images_removed(image):
    text, counts = redact.redact(f"# Jane Doe\n\n{image}\n")
    assert text == "# Jane Doe\n\n[REDACTED]\n"
    assert counts["images"] == 1


KEPT = """# Jane Doe

Location: Amsterdam, NL
Work permit: EU citizen, no visa needed
Languages: Portuguese (native), English (C2), Dutch (B1)
Page: 1

## Experience

- 2019 - 2024: Business Analyst, Acme (Health insurance domain)
- Managed stakeholder workshops; age of data pipelines reduced by 30%

## Education

- 2008 - 2012: BSc Information Systems
"""


def test_job_relevant_fields_kept():
    text, counts = redact.redact(KEPT)
    assert text == KEPT
    assert sum(counts.values()) == 0


def test_mixed_document():
    source = "# Jane Doe\n![photo](p.png)\nDate of birth: 1990\nLocation: Amsterdam\nMarital status: Married\n"
    text, _ = redact.redact(source)
    assert text == "# Jane Doe\n[REDACTED]\nDate of birth: [REDACTED]\nLocation: Amsterdam\nMarital status: [REDACTED]\n"


def test_empty_value_untouched():
    assert redact.redact("| Gender |  |")[0] == "| Gender |  |"


def test_redacted_file_matches_confirmed_example():
    source = (
        "# Joost de Vries\n"
        "![photo](img.png) | Amsterdam | EU work permit | Dutch C2, English C1\n"
        "Born: 04-05-1988 · Marital status: Married\n"
        "## Experience\n"
        "2019-2026 Business Analyst, ExampleBank\n"
    )
    expected = (
        "# Joost de Vries\n"
        "[REDACTED] | Amsterdam | EU work permit | Dutch C2, English C1\n"
        "Born: [REDACTED] · Marital status: [REDACTED]\n"
        "## Experience\n"
        "2019-2026 Business Analyst, ExampleBank\n"
    )
    assert redact.redact(source)[0] == expected


def test_idempotent(tmp_path, capsys):
    path = tmp_path / "cv.md"
    path.write_text("Date of birth: 1990\n![x](y.png)\n", encoding="utf-8")
    assert redact.main([str(path), "--json"]) == 0
    first = json.loads(capsys.readouterr().out)
    once = path.read_text(encoding="utf-8")
    assert redact.main([str(path), "--json"]) == 0
    second = json.loads(capsys.readouterr().out)
    assert first["total"] == 2
    assert second["total"] == 0
    assert path.read_text(encoding="utf-8") == once


def test_missing_file(tmp_path, capsys):
    assert redact.main([str(tmp_path / "nope.md")]) == 1
    assert "not found" in capsys.readouterr().err


def test_human_readable_output(tmp_path, capsys):
    path = tmp_path / "cv.md"
    path.write_text("Gender: Male\n", encoding="utf-8")
    assert redact.main([str(path)]) == 0
    assert "1 redaction(s) (gender=1)" in capsys.readouterr().out
