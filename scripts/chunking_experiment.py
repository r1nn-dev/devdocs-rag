"""
청킹 전략 비교 실험.
전략 A: CharacterTextSplitter (Fixed-size chunking)
전략 B: RecursiveCharacterTextSplitter
동일한 파싱 결과(parsed_sections.json)에 두 전략을 각각 적용하고 결과를 비교합니다.
"""

import json
import os
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def load_parsed_sections(path: str = "data/parsed_sections.json") -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def chunk_with_strategy(sections: list[dict], splitter) -> list[dict]:
    """
    파싱된 섹션 리스트에 청킹 전략을 적용합니다.
    각 청크는 원본 섹션의 메타데이터(section, url, github_path)를 유지합니다.
    """
    chunks = []
    for section in sections:
        splits = splitter.split_text(section["text"])
        for split in splits:
            if len(split.strip()) < 30:
                continue
            chunks.append({
                "text": split.strip(),
                "section": section["section"],
                "url": section["url"],
                "github_path": section["github_path"],
                "char_count": len(split.strip())
            })
    return chunks


def print_stats(label: str, chunks: list[dict]):
    """청킹 결과 통계를 출력합니다."""
    lengths = [c["char_count"] for c in chunks]
    avg = sum(lengths) / len(lengths) if lengths else 0
    min_len = min(lengths) if lengths else 0
    max_len = max(lengths) if lengths else 0

    print(f"\n{'='*50}")
    print(f"전략: {label}")
    print(f"{'='*50}")
    print(f"  총 청크 수     : {len(chunks)}")
    print(f"  평균 청크 길이 : {avg:.0f} chars")
    print(f"  최소 청크 길이 : {min_len} chars")
    print(f"  최대 청크 길이 : {max_len} chars")


def print_sample_chunks(label: str, chunks: list[dict], n: int = 3):
    """청크 샘플을 출력합니다."""
    print(f"\n[{label} — 샘플 {n}개]")
    for i, chunk in enumerate(chunks[:n]):
        print(f"\n  --- 청크 {i+1} ---")
        print(f"  섹션명   : {chunk['section']}")
        print(f"  URL      : {chunk['url']}")
        print(f"  길이     : {chunk['char_count']} chars")
        print(f"  텍스트   : {chunk['text'][:200]!r}")


def compare_strategies(sections: list[dict]):
    """두 전략의 결과를 비교합니다."""

    # 전략 A: CharacterTextSplitter
    splitter_a = CharacterTextSplitter(
        separator="\n",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )

    # 전략 B: RecursiveCharacterTextSplitter
    splitter_b = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks_a = chunk_with_strategy(sections, splitter_a)
    chunks_b = chunk_with_strategy(sections, splitter_b)

    # 통계 출력
    print_stats("A — CharacterTextSplitter (Fixed-size)", chunks_a)
    print_stats("B — RecursiveCharacterTextSplitter", chunks_b)

    # 샘플 출력
    print_sample_chunks("A — CharacterTextSplitter", chunks_a)
    print_sample_chunks("B — RecursiveCharacterTextSplitter", chunks_b)

    # 문맥 단절 비교 (동일 섹션에서 청크가 어떻게 나뉘는지)
    print(f"\n{'='*50}")
    print("문맥 단절 비교 — 동일 섹션의 첫 2개 청크")
    print(f"{'='*50}")

    # 가장 긴 섹션 찾기 (문맥 단절이 발생할 가능성이 높은 섹션)
    longest = max(sections, key=lambda s: len(s["text"]))
    print(f"\n대상 섹션: {longest['section']} ({len(longest['text'])} chars)")

    print("\n[전략 A — 이 섹션의 청크]")
    a_section_chunks = [c for c in chunks_a if c["section"] == longest["section"]]
    for i, c in enumerate(a_section_chunks[:2]):
        print(f"  청크 {i+1} ({c['char_count']} chars): {c['text'][:150]!r}")

    print("\n[전략 B — 이 섹션의 청크]")
    b_section_chunks = [c for c in chunks_b if c["section"] == longest["section"]]
    for i, c in enumerate(b_section_chunks[:2]):
        print(f"  청크 {i+1} ({c['char_count']} chars): {c['text'][:150]!r}")

    return chunks_a, chunks_b


def main():
    print("청킹 전략 비교 실험 시작")
    print(f"설정: chunk_size={CHUNK_SIZE}, chunk_overlap={CHUNK_OVERLAP}")

    # 파싱된 섹션 로드
    sections = load_parsed_sections()
    print(f"\n로드된 섹션 수: {len(sections)}")

    # 비교 실행
    chunks_a, chunks_b = compare_strategies(sections)

    # 결과 저장
    os.makedirs("data", exist_ok=True)

    with open("data/chunks_strategy_a.json", "w", encoding="utf-8") as f:
        json.dump(chunks_a, f, ensure_ascii=False, indent=2)

    with open("data/chunks_strategy_b.json", "w", encoding="utf-8") as f:
        json.dump(chunks_b, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 실험 완료")
    print(f"   - 전략 A 결과: data/chunks_strategy_a.json")
    print(f"   - 전략 B 결과: data/chunks_strategy_b.json")

    # 판단 근거 출력
    print(f"\n{'='*50}")
    print("설계 판단 근거 요약")
    print(f"{'='*50}")
    print(f"""
전략 A (CharacterTextSplitter):
  - 단순 줄바꿈 기준으로 고정 크기 분할
  - 구현이 단순하지만 문장/코드 블록 중간에서 잘릴 수 있음
  - 마크다운 구조를 고려하지 않음

전략 B (RecursiveCharacterTextSplitter):
  - \\n\\n → \\n → . → 공백 순서로 자연스러운 경계 탐색
  - 마크다운 문서처럼 단락 구조가 있는 경우 문맥 보존에 유리
  - LangChain 공식 문서처럼 코드 블록 + 설명이 혼재하는 경우 적합
""")


if __name__ == "__main__":
    main()