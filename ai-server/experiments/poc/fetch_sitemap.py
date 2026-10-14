"""
LangChain 공식 문서 GitHub 레포에서 .mdx 파일 목록을 수집합니다.
GitHub API를 사용하여 src/oss/ 폴더의 전체 파일 목록을 재귀적으로 가져옵니다.
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_API_BASE = "https://api.github.com"
REPO_OWNER = "langchain-ai"
REPO_NAME = "docs"
DOCS_PATH = "src/oss"
BRANCH = "main"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


def get_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def get_tree(owner, repo, branch):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    print(f"[INFO] GitHub API 요청 중: {url}")

    response = requests.get(url, headers=get_headers())

    if response.status_code == 403:
        print("[ERROR] Rate limit 초과. GITHUB_TOKEN을 .env에 추가하거나 잠시 후 다시 시도하세요.")
        return None

    if response.status_code != 200:
        print(f"[ERROR] API 요청 실패: {response.status_code}")
        return None

    return response.json()


def filter_mdx_files(tree_data, target_path):
    mdx_files = []
    for item in tree_data.get("tree", []):
        path = item.get("path", "")
        if path.startswith(target_path) and path.endswith(".mdx"):
            mdx_files.append(path)
    return mdx_files


def convert_to_doc_url(github_path):
    """
    GitHub 파일 경로를 공식 문서 URL로 변환합니다.
    예: src/oss/concepts/memory.mdx
     -> https://python.langchain.com/docs/concepts/memory/
    """
    # src/oss/ 제거
    relative_path = github_path.replace("src/oss/", "")
    # .mdx 제거
    relative_path = relative_path.replace(".mdx", "")
    # index 파일 처리
    if relative_path.endswith("/index"):
        relative_path = relative_path[:-6]

    doc_url = f"https://python.langchain.com/docs/{relative_path}/"
    return doc_url


def main():
    print("=" * 50)
    print("LangChain 공식 문서 URL 수집 시작")
    print("=" * 50)

    tree_data = get_tree(REPO_OWNER, REPO_NAME, BRANCH)
    if not tree_data:
        return

    total_files = len(tree_data.get("tree", []))
    print(f"[INFO] 전체 파일 수: {total_files}")

    mdx_files = filter_mdx_files(tree_data, DOCS_PATH)
    print(f"[INFO] 수집된 .mdx 파일 수: {len(mdx_files)}")

    results = []
    for github_path in mdx_files:
        doc_url = convert_to_doc_url(github_path)
        results.append({
            "github_path": github_path,
            "doc_url": doc_url
        })

    os.makedirs("data", exist_ok=True)

    urls = [r["doc_url"] for r in results]
    with open("data/urls.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(urls))

    with open("data/url_mapping.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 50)
    print(f"✅ 수집 완료")
    print(f"   - 총 문서 수: {len(results)}")
    print(f"   - 저장 위치: data/urls.txt, data/url_mapping.json")
    print("=" * 50)

    print("\n[샘플 5개]")
    for r in results[:5]:
        print(f"  GitHub: {r['github_path']}")
        print(f"  DocURL: {r['doc_url']}")
        print()


if __name__ == "__main__":
    main()