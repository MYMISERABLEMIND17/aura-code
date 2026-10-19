from fastapi import APIRouter, HTTPException, status
import hashlib
from src.schemas.aura import AuraProfileResponse
from src.services.calculator import AuraCalculatorService
from src.services.roaster import RoasterService
from src.services.github_client import GitHubClient

router = APIRouter()
calculator = AuraCalculatorService()
roaster = RoasterService()
github_client = GitHubClient()

@router.get("/{username}", response_model=AuraProfileResponse)
async def get_user_aura(username: str):
    # 1. Fetch user github info
    gh_data = await github_client.fetch_user_data(username)
    avatar_url = gh_data.get("avatar_url", f"https://github.com/identicons/{username}.png")

    # 2. Compute dynamic metrics using deterministic seed from username
    user_hash = int(hashlib.md5(username.encode("utf-8")).hexdigest()[:8], 16)
    commits_count = (user_hash % 800) + 50
    test_coverage = 40.0 + (user_hash % 60)
    force_pushes = (user_hash % 5)
    massive_prs = (user_hash % 4)
    night_ratio = 0.1 + ((user_hash % 70) / 100.0)

    # 3. Calculate Aura
    calc_result = calculator.calculate(
        commits_count=commits_count,
        test_coverage=test_coverage,
        force_pushes=force_pushes,
        massive_prs=massive_prs,
    )
    score = calc_result["aura_score"]

    # 4. Roast
    archetype, roast_comment = roaster.roast(
        aura_score=score,
        night_ratio=night_ratio,
        churn_ratio=calc_result.get("churn_ratio", 0.15),
        force_pushes=force_pushes,
    )

    version_hash = hashlib.sha256(f"{username}-{score}".encode("utf-8")).hexdigest()[:12]

    return AuraProfileResponse(
        username=username,
        avatar_url=avatar_url,
        aura_score=score,
        archetype=archetype,
        roast_commentary=roast_comment,
        version_hash=version_hash,
    )

