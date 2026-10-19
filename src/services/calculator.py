class AuraCalculatorService:
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
