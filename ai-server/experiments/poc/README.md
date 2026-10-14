# PoC — 문서 수집·청킹 파이프라인 검증

> 이 폴더의 코드와 `requirements.txt`는 수정하지 않는다.
> 결론이 난 로직은 `ai-server/src/app/` 아래로 새로 구현하고, 이 폴더는 근거 기록으로만 남긴다.

## 검증한 것

| 스크립트 | 내용 | 결과 |
| --- | --- | --- |
| `fetch_sitemap.py` | `langchain-ai/docs` main의 `.mdx` URL 수집 (GitHub API) | 1,852 파일 |
| `parse_page.py` | mdx 파싱, 섹션·메타데이터 추출 | 26 섹션 |
| `chunking_experiment.py` | 청킹 전략 A·B·C 비교 | 전략 B 기준 152 청크 |
| `store_and_search.py` | Chroma 저장·유사도 검색 | 검색 동작 확인 |

## 발견 사항 → 설계 반영

- 수집 저장소가 v0.3이 아니라 v1.x 문서임을 확인 → 버전별 Source Adapter + 커밋 SHA 고정 (기획서 결정 2)
- GitHub API 파일 단위 요청은 Rate Limit에 걸림 → sparse checkout 방식으로 전환

## 재실행 (레포 루트에서)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r ai-server/experiments/poc/requirements.txt
python ai-server/experiments/poc/fetch_sitemap.py
```