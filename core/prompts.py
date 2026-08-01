"""Example prompts shown on the finish page for quick copy."""

from __future__ import annotations

from pathlib import Path
import re

from .config import project_root

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
