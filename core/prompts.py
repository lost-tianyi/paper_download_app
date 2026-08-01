"""Example / topic-specific prompts for the finish page."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .config import project_root
from .i18n import get_language

EXAMPLE_SEARCH_PROMPT = """$academic-search
You are a rigorous academic literature researcher. Search for and organise real publications on <research topic>.
Scope: years <start-end>; journals <unrestricted / specified list / ranking range>; document types <articles / reviews / conference papers>.
Keywords: <core terms>; synonyms and related terms: <terms>; exclusions: <terms>; target number: <number, without lowering standards to fill quotas>.
Include only studies meeting the requirements for <scenario, research object, method, and outcomes>, and state why each study is included.
Verify every publication using an official publisher page and at least one authoritative source such as DOI/Crossref, IEEE Xplore, PubMed, Scopus, or Web of Science.
Do not invent or infer titles, authors, years, journals, DOIs, methods, or findings; mark unverified information as "Not verified".
Prefer final journal versions, identify duplicate preprint/conference/journal versions, and record explicit exclusion reasons.
Output fields: <Reference, Topic, Journal, Scenario, Model/Method, Data, Objective, Metrics, Findings, Limitations, DOI/URL>.
Separate results into Core Literature, Background Literature, and Pending Verification, and report search strings, search date, sources, and verification statistics."""

EXAMPLE_DOWNLOAD_PROMPT = """$sciencedirect-live-session-fetcher
Please process the attached Excel file. Only process records marked Approved = Yes.
Download PDFs that I can lawfully access, organise them by the category or subsection recorded in the spreadsheet, and prepare or import the approved records into Zotero.
Do not bypass paywalls or access controls. Record any unavailable, failed, or unmatched items instead of substituting another paper."""

# Placeholders aligned with AI_Based_Literature_Review_Workflow_Refined-20260730.docx
SEARCH_PROMPT_TEMPLATE = """$academic-search
You are a rigorous academic literature researcher. Search for and organise real publications on {topic}.
Scope: years {year_start}-{year_end}; journals {journals}; document types {doc_types}.
Keywords: {keywords}; synonyms and related terms: {synonyms}; exclusions: {exclusions}; target number: {target_n}.
Include only studies meeting the requirements for {scenario}, and state why each study is included.
Verify every publication using an official publisher page and at least one authoritative source such as DOI/Crossref, IEEE Xplore, PubMed, Scopus, or Web of Science.
Do not invent or infer titles, authors, years, journals, DOIs, methods, or findings; mark unverified information as "Not verified".
Prefer final journal versions, identify duplicate preprint/conference/journal versions, and record explicit exclusion reasons.
Output fields: Reference, Topic, Journal, Scenario, Model/Method, Data, Objective, Metrics, Findings, Limitations, DOI/URL.
Separate results into Core Literature, Background Literature, and Pending Verification, and report search strings, search date, sources, and verification statistics."""

ZH_WRAPPER = """请按以下英文工作流提示词执行（来自 AI-Based Literature Review Workflow）。
主题：{topic}
完成后请导出结构化 Excel，并保留 Core / Background / Pending Verification 分组。

---
{prompt}
"""


@dataclass(frozen=True)
class TopicPromptParts:
    topic: str
    year_start: str
    year_end: str
    journals: str
    doc_types: str
    keywords: str
    synonyms: str
    exclusions: str
    target_n: str
    scenario: str


def load_example_prompts() -> tuple[str, str]:
    """Prefer templates/search-prompt.md; fall back to built-in constants."""
    path = project_root() / "templates" / "search-prompt.md"
    if not path.is_file():
        return EXAMPLE_SEARCH_PROMPT, EXAMPLE_DOWNLOAD_PROMPT
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = re.findall(r"```text\n(.*?)```", text, flags=re.S)
    if len(blocks) >= 2:
        return blocks[0].strip(), blocks[1].strip()
    if len(blocks) == 1:
        return blocks[0].strip(), EXAMPLE_DOWNLOAD_PROMPT
    return EXAMPLE_SEARCH_PROMPT, EXAMPLE_DOWNLOAD_PROMPT


def _tokenize(topic: str) -> list[str]:
    cleaned = re.sub(r"[，,；;|/]+", " ", topic)
    parts = [p.strip() for p in re.split(r"\s+", cleaned) if p.strip()]
    # Keep multi-word phrases: also add the full topic as first keyword
    out: list[str] = []
    if topic.strip():
        out.append(topic.strip())
    for p in parts:
        if p.lower() not in {x.lower() for x in out} and len(p) > 1:
            out.append(p)
    return out[:8]


def _synonyms_for(topic: str, keywords: list[str]) -> list[str]:
    text = topic.lower()
    syn: list[str] = []
    mapping = [
        (("llm", "large language model", "chatgpt", "gpt"), ["large language model", "LLM", "generative AI"]),
        (("systematic review", "literature review", "meta-analysis"), ["evidence synthesis", "PRISMA", "study screening"]),
        (("screening", "study selection"), ["title abstract screening", "eligibility assessment"]),
        (("deep learning", "neural"), ["machine learning", "neural network"]),
        (("remote sensing", "卫星", "遥感"), ["earth observation", "satellite imagery"]),
        (("battery", "锂电"), ["energy storage", "lithium-ion"]),
    ]
    for keys, values in mapping:
        if any(k in text for k in keys):
            for v in values:
                if v.lower() not in text and v not in syn:
                    syn.append(v)
    # Fall back: light variants from keywords
    if not syn and len(keywords) > 1:
        syn = keywords[1:4]
    if not syn:
        syn = ["related terms derived from the topic"]
    return syn[:6]


def build_topic_parts(topic: str) -> TopicPromptParts:
    topic = (topic or "").strip()
    keywords = _tokenize(topic) or [topic or "research topic"]
    synonyms = _synonyms_for(topic, keywords)
    return TopicPromptParts(
        topic=topic or "<research topic>",
        year_start="2020",
        year_end="2026",
        journals="unrestricted",
        doc_types="articles / reviews / conference papers",
        keywords="; ".join(keywords),
        synonyms="; ".join(synonyms),
        exclusions="editorials; non-peer-reviewed blogs; unrelated domains",
        target_n="15",
        scenario=(
            f"scenario = studies on {topic}; research object and methods relevant to this topic; "
            "report outcomes / findings clearly"
        ),
    )


def build_recommended_search_prompt(topic: str, lang: str | None = None) -> str:
    """Fill the workflow search template via keyword/placeholder replacement."""
    lang = lang or get_language()
    parts = build_topic_parts(topic)
    prompt = SEARCH_PROMPT_TEMPLATE.format(
        topic=parts.topic,
        year_start=parts.year_start,
        year_end=parts.year_end,
        journals=parts.journals,
        doc_types=parts.doc_types,
        keywords=parts.keywords,
        synonyms=parts.synonyms,
        exclusions=parts.exclusions,
        target_n=parts.target_n,
        scenario=parts.scenario,
    )
    if lang == "zh":
        return ZH_WRAPPER.format(topic=parts.topic, prompt=prompt)
    return prompt
