from pydantic import BaseModel

class CaptchaRequest(BaseModel):
    answer: int

class CaptchaResponse(BaseModel):
    captcha_id: str
    question: str
    expires_in: int

class TopUpRequest(BaseModel):
    amount: int
    captcha_id: str
    answer: int
