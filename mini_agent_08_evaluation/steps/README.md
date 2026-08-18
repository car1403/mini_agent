# Evaluation Steps

메뉴 8-1부터 8-5까지는 외부 API 없이 순서대로 실행합니다.

```powershell
python .\01_why_evaluate.py
python .\02_one_scenario.py
python .\03_multiple_scenarios.py
python .\04_trace_failure.py
python .\05_regression.py
```

Backend와 Provider 설정을 마친 경우에만 선택 확장을 실행합니다.

```powershell
python .\06_provider_comparison_optional.py
```

그다음 `frontend`에서 같은 평가가 실제 API 결과로 표시되는지 확인합니다.
