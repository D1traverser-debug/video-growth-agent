from video_growth_agent.continuity import (
    ContinuityLedger,
    ContinuityLink,
    ContinuityRule,
    ContinuitySnapshot,
    assess_continuity,
)


def test_hard_preserve_detects_identity_drift():
    before = ContinuitySnapshot("S1", {"character_face": "canon-v3", "light": "warm"})
    after = ContinuitySnapshot("S2", {"character_face": "canon-v4", "light": "cool"})
    link = ContinuityLink(
        "S1",
        "S2",
        (
            ContinuityRule("character_face", "HARD", "PRESERVE", reason="same continuous action"),
            ContinuityRule("light", "SOFT", "ALLOW_CHANGE"),
        ),
    )
    result = assess_continuity(before, after, link)
    assert result.hard_pass is False
    assert result.violations[0].dimension == "character_face"


def test_intentional_change_is_not_mislabeled_as_continuity_failure():
    before = ContinuitySnapshot("S1", {"wardrobe": "coat-a", "location": "lab"})
    after = ContinuitySnapshot("S2", {"wardrobe": "coat-b", "location": "street"})
    link = ContinuityLink(
        "S1",
        "S2",
        (
            ContinuityRule("wardrobe", "SOFT", "ALLOW_CHANGE", reason="time jump"),
            ContinuityRule("location", "SOFT", "EXPECT", expected_value="street"),
        ),
    )
    result = assess_continuity(before, after, link)
    assert result.hard_pass
    assert result.violations == ()


def test_ledger_requires_explicit_snapshot_for_linked_shots():
    ledger = ContinuityLedger(
        snapshots=(ContinuitySnapshot("S1", {"prop": "p1"}),),
        links=(ContinuityLink("S1", "S2", (ContinuityRule("prop", "HARD", "PRESERVE"),)),),
    )
    try:
        ledger.validate()
    except Exception as exc:
        assert "missing shot snapshot" in str(exc)
    else:
        raise AssertionError("expected missing snapshot failure")
