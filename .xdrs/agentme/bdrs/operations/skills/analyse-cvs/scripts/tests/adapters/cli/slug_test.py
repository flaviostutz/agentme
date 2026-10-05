# Python 3.11+ pytest suite; run with: make test
import json

from analyse_cvs.adapters.cli import slug


def test_text_output(capsys):
    assert slug.main(["Anna Silva", "Anna Silva", "José Álvarez"]) == 0
    assert capsys.readouterr().out.split() == ["anna-silva", "anna-silva-2", "jose-alvarez"]


def test_json_output_with_existing(capsys):
    assert slug.main(["Bo", "--existing", "bo, other", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == [{"name": "Bo", "slug": "bo-2"}]


def test_error_without_letters(capsys):
    assert slug.main(["???"]) == 1
    assert capsys.readouterr().err.startswith("error: no slug")
