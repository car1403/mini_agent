from pydantic import BaseModel, Field


class TravelImageAnalysis(BaseModel):
    # TODO: summary, visible_text, travel_tips, safety_notes를 정의하세요.
    pass


def build_image_data_url(content_type: str, encoded: str) -> str:
    # TODO: data:{content_type};base64,{encoded} 형태로 반환하세요.
    raise NotImplementedError
