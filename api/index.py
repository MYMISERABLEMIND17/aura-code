import os
import sys
import hashlib
import traceback
from pathlib import Path
from typing import Optional, Tuple
from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import httpx

app = FastAPI(title="AuraCode Engine", version="5.0.0")

# ── Global Diagnostic Handler for Vercel ───────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "hint": "Captured by AuraCode Vercel error boundary"
        }
    )

# ── Models & Services ──────────────────────────────────────────
class AuraProfileResponse(BaseModel):
    username: str
    avatar_url: str
    aura_score: int
    archetype: str
    roast_commentary: str
    version_hash: str
    churn_ratio: float = 0.15
    weekend_commit_ratio: float = 0.40
    pr_turnaround_hours: float = 4.5

class AuraCalculator:
    def calculate(self, commits_count: int, test_coverage: float, force_pushes: int, massive_prs: int) -> dict:
        score = 1000
        score += int(test_coverage * 20)
        score -= force_pushes * 300
        score -= massive_prs * 150
        if score < -5000:
            score = -5000
        if score > 10000:
            score = 10000
        return {
            "aura_score": score,
            "churn_ratio": 0.15,
            "weekend_commit_ratio": 0.40,
            "pr_turnaround_hours": 4.5,
            "review_latency_hours": 2.0
        }

class Roaster:
    ARCHETYPES = {
        "cowboy": ("The 3 AM Cowboy", "You push directly to production without testing and sleep with your phone on loud. PagerDuty is your alarm clock."),
        "conflict": ("The Merge Conflict Merchant", "Your PRs are legendary warzones of git conflicts, force pushes, and 4,000 modified files."),
        "yaml": ("The YAML Whisperer", "You speak fluent Kubernetes, have 24 GitHub Actions running in parallel, and haven't written application logic in six months."),
        "janitor": ("The Senior Janitor", "You spend 80% of your day refactoring legacy code nobody understands. You delete more code than you write, and the team loves you for it."),
        "typo": ("The 1-Line Typo Committer", "You have 340 commits this month, and every single commit message is 'fix typo' or 'clean up syntax'."),
        "architect": ("The 10x Staff Architect", "High test coverage, pristine PR descriptions, and zero broken builds. Other engineers whisper about your commit history in awe."),
    }

    def roast(self, aura_score: int, night_ratio: float = 0.3, churn_ratio: float = 0.3, force_pushes: int = 0) -> Tuple[str, str]:
        if force_pushes >= 2:
            return self.ARCHETYPES["conflict"]
        elif night_ratio >= 0.55:
            return self.ARCHETYPES["cowboy"]
        elif churn_ratio >= 0.75:
            return self.ARCHETYPES["janitor"]
        elif aura_score >= 6000:
            return self.ARCHETYPES["architect"]
        elif aura_score >= 3000:
            return self.ARCHETYPES["yaml"]
        elif aura_score < 0:
            return self.ARCHETYPES["conflict"]
        else:
            return self.ARCHETYPES["typo"]

calculator = AuraCalculator()
roaster = Roaster()

async def fetch_github_user(username: str) -> dict:
    headers = {"User-Agent": "AuraCode-Vercel-Engine"}
    gh_token = os.getenv("GITHUB_TOKEN")
    if gh_token:
        headers["Authorization"] = f"token {gh_token}"
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(f"https://api.github.com/users/{username}", headers=headers)
            if resp.status_code == 200:
                return resp.json()
    except Exception:
        pass
    return {"login": username, "avatar_url": f"https://github.com/identicons/{username}.png"}

# ── Endpoints ──────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    # Look for index.html in api/ or src/web/
    current_dir = Path(__file__).resolve().parent
    paths_to_check = [
        current_dir / "index.html",
        current_dir.parent / "src" / "web" / "index.html",
        Path("/var/task/api/index.html"),
        Path("/var/task/src/web/index.html"),
    ]
    for p in paths_to_check:
        if p.exists():
            return HTMLResponse(content=p.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>AuraCode Engine API is Live on Vercel</h1><p>Visit /api/aura/torvalds for JSON or /api/aura/torvalds.svg for the SVG card.</p>")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "platform": "vercel-serverless"}

@app.get("/api/aura/{username}.svg")
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

@app.get("/api/aura/{username}", response_model=AuraProfileResponse)
async def get_user_aura(username: str):
    gh_data = await fetch_github_user(username)
    avatar_url = gh_data.get("avatar_url", f"https://github.com/identicons/{username}.png")

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

    version_hash = hashlib.sha256(f"{username}-{score}".encode("utf-8")).hexdigest()[:12]

    return AuraProfileResponse(
        username=username,
        avatar_url=avatar_url,
        aura_score=score,
        archetype=archetype,
        roast_commentary=roast_comment,
        version_hash=version_hash,
        churn_ratio=calc.get("churn_ratio", 0.15),
        weekend_commit_ratio=calc.get("weekend_commit_ratio", 0.40),
        pr_turnaround_hours=calc.get("pr_turnaround_hours", 4.5),
    )
