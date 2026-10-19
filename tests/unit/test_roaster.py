from src.services.roaster import RoasterService

def test_roaster():
    roaster = RoasterService()

    # 1. High score Staff Architect
    title, comment = roaster.roast(7500)
    assert title == "The 10x Staff Architect"
    assert "whisper" in comment.lower() or "commit history" in comment.lower()

    # 2. Mid score YAML Whisperer
    title_yaml, _ = roaster.roast(3500)
    assert title_yaml == "The YAML Whisperer"

    # 3. Night owl Cowboy
    title_cowboy, _ = roaster.roast(1500, night_ratio=0.75)
    assert title_cowboy == "The 3 AM Cowboy"

    # 4. Negative aura Conflict Merchant
    title_neg, _ = roaster.roast(-2000)
    assert title_neg == "The Merge Conflict Merchant"

    # 5. Force push penalty
    title_force, _ = roaster.roast(8000, force_pushes=3)
    assert title_force == "The Merge Conflict Merchant"

