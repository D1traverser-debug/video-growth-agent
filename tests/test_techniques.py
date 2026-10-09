from video_growth_agent import TechniqueLibrary


def test_technique_library_routes_by_tags_and_cost():
    lib = TechniqueLibrary()
    found = lib.find({"mechanism", "scale"}, max_cost=1, validated_only=True)
    ids = [item.technique_id for item in found]
    assert "T-001" in ids
    assert "T-006" in ids
    assert "T-004" not in ids
