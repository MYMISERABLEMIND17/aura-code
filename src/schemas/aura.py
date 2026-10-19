from pydantic import BaseModel

class AuraProfileResponse(BaseModel):
    username: str
    avatar_url: str
    aura_score: int
    archetype: str
    roast_commentary: str
    version_hash: str

    class Config:
        from_attributes = True
