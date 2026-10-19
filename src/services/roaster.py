"""Archetype Roaster Service: Assigns viral developer archetypes and Staff-Engineer critique."""

from typing import Tuple, Dict, Any

class RoasterService:
    ARCHETYPES = {
        "cowboy": ("The 3 AM Cowboy", "You push directly to production without testing and sleep with your phone on loud. PagerDuty is your alarm clock."),
        "conflict": ("The Merge Conflict Merchant", "Your PRs are legendary warzones of git conflicts, force pushes, and 4,000 modified files."),
        "yaml": ("The YAML Whisperer", "You speak fluent Kubernetes, have 24 GitHub Actions running in parallel, and haven't written application logic in six months."),
        "janitor": ("The Senior Janitor", "You spend 80% of your day refactoring legacy code nobody understands. You delete more code than you write, and the team loves you for it."),
        "typo": ("The 1-Line Typo Committer", "You have 340 commits this month, and every single commit message is 'fix typo' or 'clean up syntax'."),
        "architect": ("The 10x Staff Architect", "High test coverage, pristine PR descriptions, and zero broken builds. Other engineers whisper about your commit history in awe."),
    }

    def roast(self, aura_score: int, night_ratio: float = 0.3, churn_ratio: float = 0.3, force_pushes: int = 0) -> Tuple[str, str]:
        """
        Determines the archetype and witty roast commentary based on real developer telemetry.
        """
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
