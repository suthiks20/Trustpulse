from pydantic import BaseModel


class LoginRequest(BaseModel):
    # Plain str, not EmailStr: this is a single fixed admin identifier compared
    # against ADMIN_EMAIL in .env, not a signup form — EmailStr's reserved-TLD
    # check (e.g. rejects "*.local") has no value here and only blocks
    # legitimate internal-style admin addresses.
    email: str
    password: str


class AdminOut(BaseModel):
    email: str
