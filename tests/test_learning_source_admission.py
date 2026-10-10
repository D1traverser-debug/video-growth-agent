from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "skills/video-growth-agent/references/self-learning.md"


def test_ad_hoc_session_material_is_not_implicitly_a_learning_source():
    text = POLICY.read_text(encoding="utf-8")
    assert "Seeing content during a session does **not** make it a learning source." in text
    assert "outside the durable learning boundary by default" in text
    assert "The declared work packet is the learning context boundary." in text
    assert "Ambient conversation" in text


def test_external_learning_requires_explicit_import_and_authorization():
    text = POLICY.read_text(encoding="utf-8")
    assert "explicitly imported as an external learning source" in text
    assert "affirmative learning authorization" in text
    assert "If provenance or authorization cannot be proved, reject the candidate" in text


def test_no_learn_exclusion_must_not_be_implemented_as_a_content_denylist():
    text = POLICY.read_text(encoding="utf-8")
    assert "exclude it before durable serialization" in text
    assert "Do not create a topic/title/URL/fingerprint denylist" in text
    assert "that would itself persist a trace" in text
