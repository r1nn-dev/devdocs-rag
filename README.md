# devdocs-rag

공식 기술 문서 RAG (Retrieval-Augmented Generation) 기반 개발 학습 질의응답 플랫폼

## 프로젝트 개요

- 공식 문서를 검색 소스로 고정한 버전 인식 RAG Q&A 플랫폼.
- 사용자가 프레임워크와 버전을 선택한 뒤 자연어로 질문하면, 해당 버전의 공식 문서에서만 검색하여 출처 URL과 함께 답변을 반환한다.

## 기술 스택

| 구분 | 기술 |
|------|------|
| AI 서버 | FastAPI (Python) |
| 메인 백엔드 | Spring Boot (Java) |
| 프론트엔드 | React |
| RAG 프레임워크 | LangChain |
| Vector DB | Chroma |
| LLM | GPT-4o-mini (OpenAI API) |
| 임베딩 | text-embedding-3-small |
| RDB | PostgreSQL |
| 인프라 | Docker Compose |

## 디렉토리 구조
```
devdocs-rag/
├── scripts/         # 문서 수집 파이프라인 스크립트
│   ├── fetch_sitemap.py        # 문서 URL 수집
│   ├── parse_page.py           # 문서 파싱 및 구조화
│   ├── chunking_experiment.py  # 청킹 전략 비교
│   └── store_and_search.py     # 벡터 저장 및 검색
├── data/            # 수집된 URL 및 원문 데이터
│   ├── urls.txt
│   ├── url_mapping.json
│   ├── parsed_sections.json
│   ├── chunks_strategy_a.json
│   └── chunks_strategy_b.json
├── chroma_db/                  # 벡터 DB (git 제외)
├── .env             # 환경변수 (git 제외)
├── .gitignore
└── requirements.txt
```

## 실행 방법

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
``` 

---

## 현재 구현 상태 (Phase 1 ~ 4 완료)

### 1. 문서 수집 파이프라인

- LangChain 공식 문서 GitHub 저장소를 기준으로 `.mdx` 파일 수집
- 총 **1,852개 문서 URL 확보**
- GitHub 경로 ↔ 실제 문서 URL 매핑 구조 생성

```json
{
  "github_path": "src/oss/langchain/rag.mdx",
  "url": "https://python.langchain.com/docs/langchain/rag/"
}