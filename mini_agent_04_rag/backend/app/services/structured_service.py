"""구조화 여행 계획 생성 유스케이스를 Provider에 연결합니다."""

from app.providers.models import ProviderResult
from app.providers.registry import get_provider

def generate_structured(provider:str,system_prompt:str,message:str)->ProviderResult:
    return get_provider(provider).generate_structured(system_prompt,message)
