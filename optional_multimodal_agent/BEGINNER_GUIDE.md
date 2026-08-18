# 선택 심화 · Multimodal Agent

이 자료는 01~08을 완료한 학생을 위한 선택 심화입니다.

```text
이미지
→ TravelImageAnalysis
→ Python 또는 LangGraph Agent
→ Human Approval
→ 최종 텍스트
→ 선택적 TTS
```

## 오늘 볼 파일

1. `learning_unit/08_image_to_python_agent.py`
2. `learning_unit/09_image_to_langgraph.py`
3. `learning_unit/10_agent_result_to_tts.py`
4. `backend_langgraph/app/workflows/langgraph_travel_workflow.py`
5. `frontend/app_pages/08_multimodal.py`

이미지 원본은 State에 넣지 않고 분석 결과만 저장합니다. TTS가 실패해도 Agent
결과와 승인 기록은 유지합니다.
