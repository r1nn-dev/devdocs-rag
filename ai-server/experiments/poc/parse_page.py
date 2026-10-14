"""
LangChain 공식 문서 단일 .mdx 파일을 파싱합니다.
GitHub Raw URL로 파일을 가져와 본문 텍스트와 메타데이터를 추출합니다.
"""

import requests
import re
import json
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_OWNER = "langchain-ai"
REPO_NAME = "docs"
BRANCH = "main"


def get_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def fetch_mdx_content(github_path: str) -> str:
    """GitHub Raw URL로 .mdx 파일 원문을 가져옵니다."""
    raw_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{github_path}"
    response = requests.get(raw_url, headers=get_headers())

    if response.status_code != 200:
        print(f"[ERROR] 파일 가져오기 실패: {response.status_code} — {raw_url}")
        return ""

    return response.text


def extract_sections(mdx_content: str) -> list[dict]:
    """
    .mdx 파일에서 섹션을 추출합니다.
    각 h1/h2 헤더를 기준으로 섹션을 분리합니다.
    """
    # MDX에서 JSX import/export 제거
    content = re.sub(r'^import\s+.*$', '', mdx_content, flags=re.MULTILINE)
    content = re.sub(r'^export\s+.*$', '', content, flags=re.MULTILINE)

    # frontmatter 제거 (--- 로 감싸진 부분)
    content = re.sub(r'^---[\s\S]*?---\n', '', content, flags=re.MULTILINE)

    # MDX 컴포넌트 태그 제거 (<ComponentName ... />)
    content = re.sub(r'<[A-Z][^>]*/?>', '', content)
    content = re.sub(r'</[A-Z][^>]*>', '', content)

    # 헤더 기준으로 섹션 분리
    # h1(#), h2(##) 기준으로 자름
    sections = []
    current_section = {"heading": "Overview", "level": 0, "content": ""}

    for line in content.split('\n'):
        h1_match = re.match(r'^# (.+)', line)
        h2_match = re.match(r'^## (.+)', line)

        if h1_match:
            # 이전 섹션 저장
            if current_section["content"].strip():
                sections.append(current_section)
            current_section = {
                "heading": h1_match.group(1).strip(),
                "level": 1,
                "content": ""
            }
        elif h2_match:
            # 이전 섹션 저장
            if current_section["content"].strip():
                sections.append(current_section)
            current_section = {
                "heading": h2_match.group(1).strip(),
                "level": 2,
                "content": ""
            }
        else:
            current_section["content"] += line + "\n"

    # 마지막 섹션 저장
    if current_section["content"].strip():
        sections.append(current_section)

    return sections


def parse_page(github_path: str, doc_url: str) -> list[dict]:
    """
    단일 .mdx 파일을 파싱하여 섹션별 청크 후보를 반환합니다.
    각 항목은 {text, section, url} 형태입니다.
    """
    print(f"[INFO] 파싱 중: {github_path}")
    mdx_content = fetch_mdx_content(github_path)

    if not mdx_content:
        return []

    sections = extract_sections(mdx_content)

    results = []
    for section in sections:
        text = section["content"].strip()
        if len(text) < 50:  # 너무 짧은 섹션 제외
            continue

        results.append({
            "text": text,
            "section": section["heading"],
            "url": doc_url,
            "github_path": github_path
        })

    return results


def main():
    # 테스트용 단일 파일
    test_cases = [
        {
            "github_path": "src/oss/langchain/rag.mdx",
            "doc_url": "https://python.langchain.com/docs/langchain/rag/"
        },
        {
            "github_path": "src/oss/langchain/quickstart.mdx",
            "doc_url": "https://python.langchain.com/docs/langchain/quickstart/"
        }
    ]

    all_results = []

    for case in test_cases:
        results = parse_page(case["github_path"], case["doc_url"])
        all_results.extend(results)

        print(f"\n{'='*50}")
        print(f"파일: {case['github_path']}")
        print(f"추출된 섹션 수: {len(results)}")
        print(f"\n[섹션 샘플 3개]")
        for r in results[:3]:
            print(f"  섹션명: {r['section']}")
            print(f"  URL: {r['url']}")
            print(f"  텍스트 (앞 100자): {r['text'][:100]!r}")
            print()

    # 결과 저장
    os.makedirs("data", exist_ok=True)
    with open("data/parsed_sections.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 파싱 완료")
    print(f"   - 총 섹션 수: {len(all_results)}")
    print(f"   - 저장 위치: data/parsed_sections.json")


if __name__ == "__main__":
    main()