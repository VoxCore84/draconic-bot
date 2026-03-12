"""Knowledge base loader — reads markdown files and selects relevant snippets."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from ai.schemas import KBSnippet
from ai.settings import AI_KB_DIR

log = logging.getLogger(__name__)

_MANIFEST_PATH = AI_KB_DIR / "kb_manifest.json"


def _split_by_headings(content: str, file_key: str, file_tags: list[str]) -> list[KBSnippet]:
    """Split a markdown file into sections by ## headings.

    Each section inherits the file-level tags plus words from its heading.
    If the file has no ## headings, return the whole file as one section.
    """
    # Find all ## headings and their positions
    heading_pattern = re.compile(r"^##\s+(.+)", re.MULTILINE)
    matches = list(heading_pattern.finditer(content))

    if not matches:
        # No ## headings — return the whole file as one section
        title_match = re.match(r"^#\s+(.+)", content)
        title = title_match.group(1) if title_match else file_key
        return [KBSnippet(
            file_key=file_key,
            title=title,
            content=content,
            tags=list(file_tags),
        )]

    sections = []

    # Get the preamble (text before first ##) as a section if substantial
    preamble = content[:matches[0].start()].strip()
    if len(preamble) > 100:
        title_match = re.match(r"^#\s+(.+)", preamble)
        title = title_match.group(1) if title_match else file_key
        sections.append(KBSnippet(
            file_key=f"{file_key}/intro",
            title=title,
            content=preamble,
            tags=list(file_tags),
        ))

    # Split by ## headings
    for i, match in enumerate(matches):
        heading_title = match.group(1).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section_content = content[start:end].strip()

        if len(section_content) < 30:
            continue

        # Extract keywords from heading as additional tags
        heading_words = re.findall(r"[a-zA-Z0-9_.-]+", heading_title.lower())
        section_tags = list(set(file_tags + heading_words))

        sections.append(KBSnippet(
            file_key=f"{file_key}/{heading_title[:40]}",
            title=heading_title,
            content=section_content,
            tags=section_tags,
        ))

    return sections


class KnowledgeBase:
    """Local file-based knowledge retrieval by tag/keyword matching."""

    def __init__(self):
        self._sections: list[KBSnippet] = []
        self._manifest: dict = {}
        self.load()

    def load(self):
        """Load all knowledge files and manifest, splitting by headings."""
        self._sections = []
        self._manifest = {}

        if _MANIFEST_PATH.exists():
            try:
                with open(_MANIFEST_PATH, "r", encoding="utf-8") as f:
                    self._manifest = json.load(f)
            except Exception:
                log.exception("Failed to load kb_manifest.json")

        if not AI_KB_DIR.exists():
            log.warning("Knowledge directory does not exist: %s", AI_KB_DIR)
            return

        for md_file in sorted(AI_KB_DIR.glob("*.md")):
            file_key = md_file.stem
            meta = self._manifest.get(file_key, {})
            tags = meta.get("tags", [])

            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                log.exception("Failed to read KB file: %s", md_file)
                continue

            # Also extract inline tags if present
            tag_match = re.search(r"^Tags:\s*(.+)", content, re.MULTILINE)
            if tag_match:
                inline_tags = [t.strip().lower() for t in tag_match.group(1).split(",")]
                tags = list(set(tags + inline_tags))

            # Split into heading-based sections
            sections = _split_by_headings(content, file_key, tags)
            self._sections.extend(sections)

        log.info("Loaded %d KB sections from %s", len(self._sections), AI_KB_DIR)

    def select_snippets(self, keywords: list[str], max_snippets: int = 6, max_tokens: int = 3000) -> list[KBSnippet]:
        """Select the most relevant KB snippets for the given keywords.

        Uses simple lexical matching: score each section by how many keywords
        appear in its tags or content.
        """
        if not keywords or not self._sections:
            return []

        keywords_lower = [k.lower() for k in keywords]
        scored: list[tuple[float, KBSnippet]] = []

        for section in self._sections:
            score = 0.0
            tags_str = " ".join(section.tags).lower()
            content_lower = section.content.lower()

            for kw in keywords_lower:
                # Tag match is worth more than content match
                if kw in tags_str:
                    score += 3.0
                if kw in content_lower:
                    score += 1.0

            if score > 0:
                scored.append((score, section))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Select top snippets within token budget (rough: 1 token ~ 4 chars)
        selected = []
        total_chars = 0
        char_limit = max_tokens * 4

        for _, section in scored[:max_snippets * 3]:
            if len(selected) >= max_snippets:
                break
            section_chars = len(section.content)
            if total_chars + section_chars > char_limit:
                continue
            selected.append(section)
            total_chars += section_chars

        return selected

    def get_all_sections(self) -> list[KBSnippet]:
        return list(self._sections)

    def extract_keywords(self, text: str) -> list[str]:
        """Extract likely keywords from a user message for KB matching."""
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "can", "shall", "to", "of", "in", "for",
            "on", "with", "at", "by", "from", "as", "into", "through", "during",
            "before", "after", "above", "below", "between", "and", "but", "or",
            "not", "no", "so", "if", "then", "than", "that", "this", "these",
            "those", "it", "its", "my", "your", "his", "her", "our", "their",
            "what", "which", "who", "when", "where", "why", "how", "all", "each",
            "every", "both", "few", "more", "most", "some", "any", "just", "very",
            "really", "only", "also", "much", "many", "i", "me", "we", "you", "he",
            "she", "they", "them", "us", "im", "dont", "cant", "wont", "doesnt",
        }

        words = re.findall(r"[a-zA-Z0-9_.-]+", text.lower())
        keywords = [w for w in words if len(w) >= 3 and w not in stop_words]

        # Deduplicate while preserving order
        seen = set()
        result = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                result.append(kw)

        return result[:15]
