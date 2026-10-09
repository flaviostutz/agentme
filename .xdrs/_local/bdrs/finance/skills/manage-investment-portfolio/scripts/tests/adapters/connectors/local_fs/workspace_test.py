"""Work dir store safety: path confinement, deterministic JSON, lock, raw copies."""

from pathlib import Path

import pytest

from portfolio_manager.adapters.connectors.local_fs.workspace import Workspace, collect_sources, resolve_tmp, work_dir
from portfolio_manager.shared.errors import PmError
from portfolio_manager.shared.values import dumps


def test_resolve_tmp_only_allows_paths_inside_tmp(tmp_path):
    (tmp_path / ".tmp").mkdir()
    assert resolve_tmp(".tmp/x", tmp_path) == (tmp_path / ".tmp" / "x").resolve()
    for bad in ("x", "../.tmp/x", "/etc", ".tmp/../x"):
        with pytest.raises(PmError):
            resolve_tmp(bad, tmp_path)


def test_work_dir_name_validation(tmp_path):
    (tmp_path / ".tmp").mkdir()
    assert work_dir("my-run-1", tmp_path) == (tmp_path / ".tmp" / "manage-investment-portfolio" / "my-run-1").resolve()
    for bad in ("", "a/b", "a b", "My_Run", "-a", "a--b", ".work"):
        with pytest.raises(PmError):
            work_dir(bad, tmp_path)


def test_cache_lives_in_the_skill_work_folder_apart_from_the_run_folder(tmp_path):
    ws = Workspace(tmp_path / ".tmp" / "manage-investment-portfolio" / "p1")
    assert ws.read_cache("x.json") is None
    ws.write_cache("x.json", {"k": 1})
    assert ws.read_cache("x.json") == {"k": 1}
    assert ws.cache_path("x.json") == tmp_path / ".tmp" / "manage-investment-portfolio" / ".work" / "p1" / "x.json"
    assert not ws.path("cache").exists()
    ws.cache_path("x.json").write_text("{broken", encoding="utf-8")
    assert ws.read_cache("x.json") is None


def test_dumps_is_deterministic_and_workspace_roundtrips(tmp_path):
    assert dumps({"b": 1, "a": [2]}) == dumps({"a": [2], "b": 1})
    ws = Workspace(tmp_path / "ws")
    assert ws.init() is True and ws.init() is False
    ws.write("data/x.json", {"k": 1})
    assert ws.read("data/x.json") == {"k": 1} and ws.read("data/none.json", "dflt") == "dflt"
    ws.write_text("reports/a.md", "hi\n")
    assert ws.path("reports/a.md").read_text(encoding="utf-8") == "hi\n"
    assert isinstance(ws.root, Path)


def test_lock_excludes_a_second_holder(tmp_path):
    ws = Workspace(tmp_path / "ws")
    ws.init()
    with ws.lock(), pytest.raises(PmError), ws.lock():
        pass
    with ws.lock():
        pass


def test_import_raw_copies_once_and_keeps_names_safe(tmp_path):
    ws = Workspace(tmp_path / "ws")
    ws.init()
    src = tmp_path / "my statement (1).pdf"
    src.write_bytes(b"data")
    name, info = ws.import_raw(src)
    assert name.endswith("-my_statement_1_.pdf") and info["original_name"] == src.name
    assert ws.import_raw(src)[0] == name
    assert ws.file_sha256(f"raw/{name}") == info["sha256"] and ws.is_file(f"raw/{name}")


def test_clean_outputs_removes_only_stale_files(tmp_path):
    ws = Workspace(tmp_path / "ws")
    ws.init()
    ws.write_text("reports/keep.md", "k")
    ws.write_text("reports/old.md", "o")
    ws.clean_outputs("reports", "*.md", {"reports/keep.md"})
    assert ws.is_file("reports/keep.md") and not ws.is_file("reports/old.md")
    assert ws.text_sha256("reports/keep.md")


def test_collect_sources_accepts_a_file_or_a_folder_of_pdfs(tmp_path):
    (tmp_path / "a.pdf").write_bytes(b"x")
    (tmp_path / "b.txt").write_text("x")
    assert collect_sources(tmp_path / "a.pdf") == [tmp_path / "a.pdf"]
    assert collect_sources(tmp_path) == [tmp_path / "a.pdf"]
    with pytest.raises(PmError):
        collect_sources(tmp_path / "missing")
