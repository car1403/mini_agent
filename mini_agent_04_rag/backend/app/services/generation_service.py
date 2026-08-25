"""일반 텍스트 생성 유스케이스를 Provider 레지스트리에 연결합니다."""

from app.providers.models import ProviderResult
from app.providers.registry import get_provider

def generate(provider:str,system_prompt:str,message:str)->ProviderResult:
    return get_provider(provider).generate(system_prompt,message)
