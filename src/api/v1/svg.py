from fastapi import APIRouter, Response
import hashlib
from src.services.calculator import AuraCalculatorService
from src.services.roaster import RoasterService

router = APIRouter()
calculator = AuraCalculatorService()
roaster = RoasterService()

@router.get("/{username}.svg")
async def get_aura_svg(username: str):
    user_hash = int(hashlib.md5(username.encode("utf-8")).hexdigest()[:8], 16)
    commits_count = (user_hash % 800) + 50
    test_coverage = 40.0 + (user_hash % 60)
    force_pushes = (user_hash % 5)
    massive_prs = (user_hash % 4)
    night_ratio = 0.1 + ((user_hash % 70) / 100.0)

    calc = calculator.calculate(
        commits_count=commits_count,
        test_coverage=test_coverage,
        force_pushes=force_pushes,
        massive_prs=massive_prs,
    )
    score = calc["aura_score"]
    archetype, roast_comment = roaster.roast(
        aura_score=score,
        night_ratio=night_ratio,
        churn_ratio=calc.get("churn_ratio", 0.15),
        force_pushes=force_pushes,
    )

    score_color = "#27ae60" if score >= 3000 else ("#f39c12" if score >= 0 else "#ff6363")
    score_sign = "+" if score > 0 else ""

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 240" width="480" height="240">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f0f10"/>
      <stop offset="100%" stop-color="#07080a"/>
    </linearGradient>
    <linearGradient id="aura-glow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{score_color}" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="{score_color}" stop-opacity="0.0"/>
    </linearGradient>
    <clipPath id="card-clip">
      <rect width="480" height="240" rx="14"/>
    </clipPath>
  </defs>
  <g clip-path="url(#card-clip)">
    <rect width="480" height="240" fill="url(#bg)" stroke="#26282c" stroke-width="2"/>
    <rect x="0" y="0" width="480" height="4" fill="{score_color}"/>
    <rect x="0" y="4" width="480" height="40" fill="url(#aura-glow)"/>

    <text x="24" y="38" fill="#8e8e93" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif" font-size="11" font-weight="600" letter-spacing="1.5">AURACODE // DEV SPOTIFY WRAPPED</text>
    <circle cx="452" cy="34" r="5" fill="{score_color}"/>

    <text x="24" y="74" fill="#f4f4f6" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif" font-size="20" font-weight="700">@{username}</text>
    <rect x="24" y="86" width="220" height="24" rx="6" fill="#1c1c1e" stroke="#26282c" stroke-width="1"/>
    <text x="34" y="102" fill="#f4f4f6" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif" font-size="12" font-weight="600">{archetype}</text>

    <text x="320" y="82" fill="#8e8e93" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif" font-size="11" font-weight="600">AURA SCORE</text>
    <text x="320" y="112" fill="{score_color}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, monospace" font-size="28" font-weight="800">{score_sign}{score:,}</text>

    <rect x="24" y="126" width="134" height="42" rx="6" fill="#1c1c1e"/>
    <text x="34" y="144" fill="#8e8e93" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="10">CHURN RATIO</text>
    <text x="34" y="160" fill="#f4f4f6" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', monospace" font-size="12" font-weight="700">{int(calc.get('churn_ratio', 0.15)*100)}%</text>

    <rect x="172" y="126" width="134" height="42" rx="6" fill="#1c1c1e"/>
    <text x="182" y="144" fill="#8e8e93" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="10">WEEKEND COMMIT</text>
    <text x="182" y="160" fill="#f4f4f6" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', monospace" font-size="12" font-weight="700">{int(calc.get('weekend_commit_ratio', 0.40)*100)}%</text>

    <rect x="320" y="126" width="136" height="42" rx="6" fill="#1c1c1e"/>
    <text x="330" y="144" fill="#8e8e93" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="10">PR TURNAROUND</text>
    <text x="330" y="160" fill="#f4f4f6" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', monospace" font-size="12" font-weight="700">{calc.get('pr_turnaround_hours', 4.5)}h</text>

    <line x1="24" y1="182" x2="456" y2="182" stroke="#26282c" stroke-width="1"/>
    <text x="24" y="206" fill="#8e8e93" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="11" font-style="italic">"{roast_comment[:62]}..."</text>
    <text x="24" y="224" fill="#55575e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="10">auracode.dev • Raycast Dark Titanium Edition</text>
  </g>
</svg>"""

    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400",
            "Content-Disposition": f"inline; filename={username}-aura.svg",
        }
    )

