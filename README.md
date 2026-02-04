# Cement RAG Chatbot v2 (cement-gem3-v2)

시멘트 관련 문서와 엑셀 데이터를 분석하는 AI 챗봇(RAG)입니다.

## 주요 기능
- 시멘트 및 건축 관련 기술 문서 RAG 기반 질의응답
- 엑셀 파일 기반 데이터 분석 및 시각화
- Google Gemini 2.0 및 Pinecone 벡터 DB 지원
- NotebookLM 스타일의 프리미엄 UI

## 시작하기

### 환경 설정
`.env.example` 파일을 `.env`로 복사하고 다음 API 키들을 설정하세요:
- `GEMINI_API_KEY`: Google AI Studio API 키
- `PINECONE_API_KEY`: Pinecone API 키

### 실행 방법
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 배포
이 프로젝트는 Streamlit Cloud를 통해 배포됩니다.
- GitHub 저장소 연결
- Streamlit Cloud Secrets에 API 키 설정 필수
