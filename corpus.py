"""Loads the support corpus (data/docs.txt) into structured chunks."""
from __future__ import annotations

import os
from dataclasses import dataclass

DOCS_PATH_DEFAULT = os.path.join(os.path.dirname(__file__), "data", "docs.txt")


@dataclass
class Chunk:
    company: str
    product_area: str
    title: str
    url: str
    content: str

    @property
    def header(self) -> str:
        return f"[{self.company} | {self.product_area}] {self.title}"

    @property
    def for_retrieval(self) -> str:
        return f"{self.title}\n{self.content}"


def load_corpus(path: str = DOCS_PATH_DEFAULT) -> list[Chunk]:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Corpus file not found at {path}. Expected the scraped support docs."
        )

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    chunks: list[Chunk] = []
    for block in raw.split("###CHUNK###"):
        block = block.strip()
        if not block:
            continue
        head, _, content = block.partition("###CONTENT###")
        if not content:
            continue

        meta = {}
        for line in head.strip().splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip().lower()] = v.strip()

        chunks.append(
            Chunk(
                company=meta.get("company", "NONE"),
                product_area=meta.get("product_area", "general"),
                title=meta.get("title", ""),
                url=meta.get("url", ""),
                content=content.strip(),
            )
        )
    return chunks
