from pydantic import BaseModel

class WebPage(BaseModel):
    study_goal: str
    title: str
    url: str
    content: str