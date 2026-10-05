# Runtime: pytest; concept taxonomy contract (word limits, anchors, grouping).

import re

import pytest

from portfolio_manager.app import concepts


def words(text: str) -> int:
    return len(text.split())


def test_every_concept_respects_the_template_word_limits():
    for c in concepts.CONCEPTS:
        assert words(c.summary) < concepts.MAX_WORDS["summary"], c.key
        assert words(c.useful) < concepts.MAX_WORDS["useful"], c.key
        assert words(c.example) < concepts.MAX_WORDS["example"], c.key
        assert words(c.formula) < concepts.MAX_WORDS["formula"], c.key


def test_the_useful_line_ends_with_a_use_this_to_sentence():
    for c in concepts.CONCEPTS:
        last = re.split(r"(?<=[.!?])\s+", c.useful.strip())[-1]
        assert last.startswith("Use this to"), c.key


def test_keys_and_names_are_unique_and_groups_are_known():
    assert len({c.key for c in concepts.CONCEPTS}) == len(concepts.CONCEPTS)
    assert len({c.name for c in concepts.CONCEPTS}) == len(concepts.CONCEPTS)
    assert {c.group for c in concepts.CONCEPTS} <= set(concepts.GROUPS)
    assert len(concepts.CONCEPTS) >= 25


def test_rendered_article_groups_topics_alphabetically_and_every_link_anchor_exists():
    text = concepts.render()
    groups = re.findall(r"^## (.+)$", text, re.MULTILINE)
    assert groups == list(concepts.GROUPS)
    anchors = {concepts.slug(h) for h in re.findall(r"^### (.+)$", text, re.MULTILINE)}
    for c in concepts.CONCEPTS:
        assert re.search(r"\(concepts\.md#([^)]+)\)", concepts.link(c.key)).group(1) in anchors
    for group in concepts.GROUPS:
        names = [c.name.lower() for c in concepts.CONCEPTS if c.group == group]
        section = text.split(f"## {group}\n", 1)[1].split("\n## ", 1)[0]
        assert [h.lower() for h in re.findall(r"^### (.+)$", section, re.MULTILINE)] == sorted(names)


def test_formula_line_appears_only_for_concepts_that_have_one():
    text = concepts.render()
    assert text.count("Formula: ") == sum(1 for c in concepts.CONCEPTS if c.formula)


def test_link_uses_the_concept_name_or_a_custom_label_and_rejects_unknown_keys():
    assert concepts.link("twr") == "[TWR (natural)](concepts.md#twr-natural)"
    assert concepts.link("twr", "TWR") == "[TWR](concepts.md#twr-natural)"
    with pytest.raises(KeyError):
        concepts.link("nope")
