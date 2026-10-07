import pytest
from pathlib import Path
import sys
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_github_issue_generation_basic(resolver):
    res = resolver.resolve("salve isso no projeto")
    assert res is not None
    issue = res.to_github_issue(raw_query="salve isso no projeto")

    assert "title" in issue
    assert "body" in issue
    assert "labels" in issue
    assert "command" in issue

    assert "[SRE/GOVERNANCE]: Salvar e Sincronizar Projeto com GitHub" in issue["title"]
    assert "agy_cmd project-save-sync" in issue["body"]
    assert "Zero-Token Guard" in issue["body"]
    assert "gh issue create" in issue["command"]
    assert "ops" in issue["labels"]

def test_github_issue_with_custom_repo(resolver):
    res = resolver.resolve("destrava o git")
    assert res is not None
    issue = res.to_github_issue(raw_query="destrava o git", repo="xProTorkz/antigravity-turbinado")

    assert '--repo "xProTorkz/antigravity-turbinado"' in issue["command"]
    assert "unlock-git" in issue["body"]

def test_llm_prompt_generation_basic(resolver):
    res = resolver.resolve("atualize a branch e suba as correções")
    assert res is not None
    prompt = res.to_llm_prompt(raw_query="atualize a branch e suba as correções")

    assert "### ROLE & SYSTEM DIRECTIVE" in prompt
    assert "### TASK SPECIFICATION" in prompt
    assert "### DETERMINISTIC COMMAND" in prompt
    assert "agy_cmd project-save-sync" in prompt
    assert "### OPERATIONAL CONSTRAINTS" in prompt
    assert "Zero-Token Guard" in prompt
    assert "Minimal Necessary Diff" in prompt
    assert "### EXPECTED OUTPUT & RECEIPT" in prompt

def test_llm_prompt_compound_plan(resolver):
    res = resolver.resolve("audite e corrija o projeto")
    assert res is not None
    prompt = res.to_llm_prompt(raw_query="audite e corrija o projeto")

    assert "### TASK SPECIFICATION" in prompt
    assert "agy_cmd" in prompt
    assert "STATUS: [IMPLEMENTADO / VALIDADO / SINCRONIZADO / DONE]" in prompt
