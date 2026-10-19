import httpx

class GitHubClient:
    async def fetch_user_data(self, username: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://api.github.com/users/{username}")
            if resp.status_code != 200:
                return {"login": username, "avatar_url": "https://github.com/identicons/{username}.png"}
            return resp.json()
