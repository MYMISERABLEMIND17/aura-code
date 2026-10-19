import pytest
from src.services.github_client import GitHubClient
from src.services.calculator import AuraCalculatorService
from src.services.roaster import RoasterService

@pytest.mark.asyncio
async def test_github_ingestion_pipeline():
    client = GitHubClient()
    calculator = AuraCalculatorService()
    roaster = RoasterService()

    # Ingest user telemetry
    user_data = await client.fetch_user_data("octocat")
    assert "login" in user_data
    assert "avatar_url" in user_data

    # Calculate metrics
    metrics = calculator.calculate(
        commits_count=120,
        test_coverage=85.0,
        force_pushes=0,
        massive_prs=1,
    )
    assert -5000 <= metrics["aura_score"] <= 10000
    assert metrics["churn_ratio"] >= 0.0

    # Roast assignment
    archetype, roast = roaster.roast(metrics["aura_score"], night_ratio=0.2)
    assert len(archetype) > 0
    assert len(roast) > 0

