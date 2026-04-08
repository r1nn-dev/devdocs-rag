"""
Phase 4. Chroma 저장 + 유사도 검색 동작 확인

입력:
- data/chunks_strategy_b.json

동작:
1. 청크 로드
2. OpenAI text-embedding-3-small로 임베딩
3. Chroma 로컬 DB에 저장
4. 테스트 질문으로 similarity search 실행
5. Top-3 청크 + 섹션명 + URL 출력
"""

import json
import os
import shutil
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

CHUNKS_PATH = "data/chunks_strategy_b.json"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "langchain_docs_phase4"
EMBEDDING_MODEL = "text-embedding-3-small"

TEST_QUERY = "What is RAG in LangChain?"


def load_chunks(path: str) -> list[dict]:
    """JSON 파일에서 청크 데이터를 로드합니다."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"청크 파일이 없습니다: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def convert_to_documents(chunks: list[dict]) -> list[Document]:
    """청크 dict 리스트를 LangChain Document 리스트로 변환합니다."""
    documents = []

    for chunk in chunks:
        text = chunk.get("text", "").strip()
        if not text:
            continue

        metadata = {
            "section": chunk.get("section", ""),
            "url": chunk.get("url", ""),
            "github_path": chunk.get("github_path", ""),
            "char_count": chunk.get("char_count", 0),
        }

        documents.append(
            Document(
                page_content=text,
                metadata=metadata,
            )
        )

    return documents


def reset_chroma_dir(path: str):
    """기존 Chroma DB를 삭제하고 새로 시작합니다."""
    if os.path.exists(path):
        shutil.rmtree(path)


def build_vectorstore(documents: list[Document]) -> Chroma:
    """문서를 임베딩하고 Chroma에 저장합니다."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME,
    )

    return vectorstore


def search_and_print(vectorstore: Chroma, query: str, k: int = 3):
    """질문으로 유사도 검색 후 Top-k 결과를 출력합니다."""
    results = vectorstore.similarity_search_with_score(query, k=k)

    print("\n" + "=" * 60)
    print("유사도 검색 결과")
    print("=" * 60)
    print(f"질문: {query}")
    print(f"Top-{k} 결과 수: {len(results)}")

    for idx, (doc, score) in enumerate(results, start=1):
        section = doc.metadata.get("section", "")
        url = doc.metadata.get("url", "")
        github_path = doc.metadata.get("github_path", "")
        char_count = doc.metadata.get("char_count", 0)
        preview = doc.page_content[:250].replace("\n", " ")

        print(f"\n--- Rank {idx} ---")
        print(f"score       : {score}")
        print(f"section     : {section}")
        print(f"url         : {url}")
        print(f"github_path : {github_path}")
        print(f"char_count  : {char_count}")
        print(f"text        : {preview!r}")


def main():
    print("=" * 60)
    print("Phase 4. Chroma 저장 + 유사도 검색 시작")
    print("=" * 60)

    # 1. 청크 로드
    chunks = load_chunks(CHUNKS_PATH)
    print(f"[INFO] 로드된 청크 수: {len(chunks)}")

    # 2. Document 변환
    documents = convert_to_documents(chunks)
    print(f"[INFO] 변환된 Document 수: {len(documents)}")

    if not documents:
        raise ValueError("저장할 Document가 없습니다.")

    # 3. 기존 Chroma 초기화
    print(f"[INFO] 기존 Chroma DB 초기화: {CHROMA_DIR}")
    reset_chroma_dir(CHROMA_DIR)

    # 4. 벡터 저장
    print(f"[INFO] 임베딩 모델: {EMBEDDING_MODEL}")
    print("[INFO] Chroma에 문서 저장 중...")
    vectorstore = build_vectorstore(documents)

    print("[INFO] 저장 완료")
    print(f"[INFO] 저장 위치: {CHROMA_DIR}")
    print(f"[INFO] 컬렉션명: {COLLECTION_NAME}")

    # 5. 검색 테스트
    search_and_print(vectorstore, TEST_QUERY, k=3)

    print("\n✅ Phase 4 완료")
    print("   - Chroma 저장 성공")
    print("   - 유사도 검색 결과 출력 성공")


if __name__ == "__main__":
    main()