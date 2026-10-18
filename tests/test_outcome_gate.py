"""The commit gate, run as pre-commit runs it: over a scratch repository, with claude stood in
for by a script that records each prompt with its input and answers, and exits, as the test
says. Every ending of the gate is crossed: the message refused before any review, nothing
staged, each agent failing to run or answering nothing, a verdict that is neither, FAIL, and
PASS.

The subprocess rules S603 and S607 are silenced here because their purpose, injection through
untrusted input and a hijacked PATH, does not apply: every argument is a literal this test
writes, and finding `git` and `claude` on PATH is the point, since the stub claude is a PATH
substitution, exactly as pre-commit finds the real one."""

import os
import subprocess
import textwrap
from pathlib import Path

import pytest

GATE = Path(__file__).parents[1] / "scripts" / "outcome-gate"
REFUSAL = (
    "These findings are symptoms of one skipped step of the loop, not items to clear. "
    "Do not patch each where it points: that leaves the model wrong and the gate green, "
    "and ships code that passes every check and does not do what it claims. Name the "
    "step, return to it, reprint the noun list, change what it changes. It is the smaller "
    "job: one corrected noun dissolves every finding it caused, nothing is patched twice, "
    "and it is the one move after which you are done."
)
OUTCOME = "something a party outside the system can newly do"
MESSAGE = f"chore: x\n\nbody\n\nOutcome: {OUTCOME}\n\n# a template comment\n# Outcome: not this\n"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A repository with one commit and a staged change, and a claude that records each prompt
    it is given with its standard input, and answers and exits as INFER, INFER_EXIT, REVIEW and
    REVIEW_EXIT say; unless a test says otherwise, both agents run and the verdict is PASS."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "test")
    (repo / "a.txt").write_text("one\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "a")
    (repo / "a.txt").write_text("changed\n")
    git(repo, "add", ".")
    stub = tmp_path / "bin"
    stub.mkdir()
    (stub / "claude").write_text(
        textwrap.dedent("""\
            #!/usr/bin/env bash
            { printf '%s\\n' "$*"; cat; printf '\\n'; } >> "$CLAUDE_LOG"
            case "$*" in
              *outcome-review*) printf '%s' "$REVIEW"; exit "$REVIEW_EXIT" ;;
              *) printf '%s' "$INFER"; exit "$INFER_EXIT" ;;
            esac
        """)
    )
    (stub / "claude").chmod(0o755)
    monkeypatch.setenv("PATH", f"{stub}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("CLAUDE_LOG", str(tmp_path / "claude.log"))
    monkeypatch.setenv("INFER", "an outcome\nits evidence\n")
    monkeypatch.setenv("INFER_EXIT", "0")
    monkeypatch.setenv("REVIEW", "PASS\n")
    monkeypatch.setenv("REVIEW_EXIT", "0")
    (tmp_path / "msg").write_text(MESSAGE)
    return repo


def gated(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [str(GATE), str(repo.parent / "msg")],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def asked(repo: Path) -> str:
    log = repo.parent / "claude.log"
    return log.read_text() if log.exists() else ""


def refused(repo: Path, reason: str) -> subprocess.CompletedProcess[str]:
    result = gated(repo)
    assert result.returncode == 1
    assert f"commit refused: {reason}" in result.stderr
    return result


def test_a_pass_commits_with_the_reviewer_given_the_whole_commit(repo: Path) -> None:
    assert gated(repo).returncode == 0
    inference, review = asked(repo).split("--agent outcome-review")
    assert "--agent outcome-inference" in inference
    assert "+changed" in inference
    expected = (
        f"Commit message:\nchore: x\n\nbody\n\nOutcome: {OUTCOME}\n\n"
        "Staged diff under packages/python/*/src, governed by the skill:\n\n\n"
        "Staged diff elsewhere, judged by the outcome and the message:\n"
        "diff --git a/a.txt b/a.txt\n"
    )
    assert expected in review
    assert "template comment" not in review
    assert "not this" not in review
    assert "+changed" in review
    assert review.index("+changed") < review.index("Inferred outcome:\nan outcome\nits evidence\n")
    assert review.index("Inferred outcome:") < review.index(f"Intended outcome:\n{OUTCOME}\n")


def test_a_wrapped_outcome_reaches_the_reviewer_whole(repo: Path) -> None:
    (repo.parent / "msg").write_text(
        "chore: x\n\nbody\n\nOutcome: a party outside the system can newly do\n"
        "something that takes two lines to say\n\n# a comment\n"
    )
    assert gated(repo).returncode == 0
    assert (
        "Intended outcome:\na party outside the system can newly do something that takes two "
        "lines to say\n"
    ) in asked(repo)


@pytest.mark.parametrize("verdict", ["PASS\n", "**PASS**\n"])
def test_a_pass_alone_on_the_first_line_commits(
    repo: Path, monkeypatch: pytest.MonkeyPatch, verdict: str
) -> None:
    monkeypatch.setenv("REVIEW", verdict + "\nwhatever follows\n")
    assert gated(repo).returncode == 0


def test_the_reviewer_is_handed_the_governed_source_apart_from_the_rest(repo: Path) -> None:
    source = repo / "packages" / "python" / "pkg" / "src" / "pkg" / "value.py"
    source.parent.mkdir(parents=True)
    source.write_text("x = 1\n")
    git(repo, "add", ".")
    assert gated(repo).returncode == 0
    review = asked(repo).split("--agent outcome-review")[1]
    governed = review.index("governed by the skill:")
    elsewhere = review.index("judged by the outcome and the message:")
    assert governed < review.index("+x = 1") < elsewhere < review.index("+changed")


@pytest.mark.parametrize("verdict", ["FAIL\n", "**FAIL**\n"])
def test_a_fail_refuses_the_commit_with_the_step_before_its_findings(
    repo: Path, monkeypatch: pytest.MonkeyPatch, verdict: str
) -> None:
    monkeypatch.setenv("REVIEW", verdict + "\nthe finding\n")
    stderr = refused(repo, "Outcome Review found the failures above").stderr
    assert stderr.startswith(REFUSAL)
    assert stderr.index(REFUSAL) < stderr.index("the finding")


@pytest.mark.parametrize(
    "verdict",
    [
        "Probably fine.\n",
        "Pass\n",
        "P A S S\n",
        "PASS, with reservations\n",
        "**Verdict: FAIL**\n",
        "\nPASS\n",
    ],
)
def test_a_verdict_that_is_neither_refuses_the_commit_with_the_review_after_the_step(
    repo: Path, monkeypatch: pytest.MonkeyPatch, verdict: str
) -> None:
    monkeypatch.setenv("REVIEW", verdict + "the finding\n")
    stderr = refused(repo, "Outcome Review gave no PASS or FAIL").stderr
    assert stderr.startswith(REFUSAL)
    assert stderr.index(REFUSAL) < stderr.index(verdict.strip() or "PASS")
    assert "the finding" in stderr


def test_a_reviewer_that_does_not_run_refuses_the_commit(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("REVIEW_EXIT", "1")
    refused(repo, "Outcome Review did not run")


def test_an_inference_that_does_not_run_refuses_the_commit_before_review(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("INFER_EXIT", "1")
    refused(repo, "Outcome Inference did not run")
    assert "outcome-review" not in asked(repo)


def test_an_inference_that_answers_nothing_refuses_the_commit_before_review(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("INFER", "")
    refused(repo, "Outcome Inference returned nothing")
    assert "outcome-review" not in asked(repo)


def test_nothing_staged_is_refused_before_any_agent_runs(repo: Path) -> None:
    git(repo, "reset", "-q")
    refused(repo, "nothing is staged")
    assert asked(repo) == ""


@pytest.mark.parametrize(
    "message",
    [
        "chore: x\n\nOutcome: <what a party outside the system can newly do>\n",
        "chore: x\n\nOutcome:\n",
        "chore: x\n\nbody\n",
        "chore: x\n\nbody\n\n# Outcome: only in a comment\n",
        "# only comments\n# Outcome: in a comment\n",
        "",
    ],
)
def test_a_message_without_an_outcome_is_refused_before_any_agent_runs(
    repo: Path, message: str
) -> None:
    (repo.parent / "msg").write_text(message)
    refused(repo, "fill the Outcome: line from .gitmessage")
    assert asked(repo) == ""
