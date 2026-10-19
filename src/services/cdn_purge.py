import httpx

class CDNPurgeService:
    async def purge_edge(self, username: str):
        async with httpx.AsyncClient() as client:
            try:
                await client.post("https://api.cloudflare.com/client/v4/zones/dummy/purge_cache", json={"files": [f"https://cdn.auracode-assets.dev/api/aura/{username}.svg"]})
            except Exception:
                pass
