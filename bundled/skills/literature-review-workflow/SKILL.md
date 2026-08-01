---
name: literature-review-workflow
description: |
  Guide users through an AI literature-review workflow in chat: search → human review → approve →
  lawful PDF download → Zotero. Use when the user wants to start a literature review, mentions
  literature-review-workflow, academic-search, or asks how to search/download papers with the installed skills.
  Prefer interactive step-by-step guidance; do not ask users to open documentation files themselves.
metadata:
  version: "1.1.0"
---

# Literature Review Workflow (Interactive Guide)

## How you should guide the user

The user may not be technical. **Do not** ask them to open, find, or read any documentation files.
Run the workflow **in this conversation**, one clear step at a time, and wait for their confirmation before moving on.

Recommended flow:

1. Confirm their research topic (and years / scope if needed).
2. Run `$academic-search` with a filled search prompt; export a spreadsheet.
3. Ask them to review the spreadsheet and mark `Approved = Yes/No` (explain in plain language).
4. For downloads that need institutional login: ask them to sign in via their own browser first; never ask for passwords.
5. Run `$sciencedirect-live-session-fetcher` only on `Approved = Yes` rows.
6. Help organise results into Zotero and do a short final check.

At each stage, tell them **what just happened**, **what to do next**, and **what you will do after they reply**.

## Companion capabilities

1. `$academic-search` — search, verify, and export a literature spreadsheet
2. `$sciencedirect-live-session-fetcher` — download PDFs the user can lawfully access, via a live browser session

## Standard search prompt

```text
$academic-search
You are a rigorous academic literature researcher. Search for and organise real publications on <research topic>.
Scope: years <start-end>; journals <unrestricted / specified list / ranking range>; document types <articles / reviews / conference papers>.
Keywords: <core terms>; synonyms and related terms: <terms>; exclusions: <terms>; target number: <number, without lowering standards to fill quotas>.
Include only studies meeting the requirements for <scenario, research object, method, and outcomes>, and state why each study is included.
Verify every publication using an official publisher page and at least one authoritative source such as DOI/Crossref, IEEE Xplore, PubMed, Scopus, or Web of Science.
Do not invent or infer titles, authors, years, journals, DOIs, methods, or findings; mark unverified information as "Not verified".
Prefer final journal versions, identify duplicate preprint/conference/journal versions, and record explicit exclusion reasons.
Output fields: <Reference, Topic, Journal, Scenario, Model/Method, Data, Objective, Metrics, Findings, Limitations, DOI/URL>.
Separate results into Core Literature, Background Literature, and Pending Verification, and report search strings, search date, sources, and verification statistics.
```

### Result groups (explain in plain language)

| Group | Meaning for the user |
|-------|----------------------|
| Core Literature | Closely answers the research question; keep for the main table |
| Background Literature | Useful context, but not the main evidence |
| Pending Verification | Looks relevant, but still needs checking |

## Human review checkpoint

Before downloading:

- Confirm titles, authors, year, journal via the official page / DOI
- Keep the preferred final version when preprint and journal versions both exist
- Ask the user to mark keep / discard as `Approved = Yes/No` in the spreadsheet
- Mark unknowns as `Not verified` instead of guessing

## Standard download prompt

```text
$sciencedirect-live-session-fetcher
Please process the attached Excel file. Only process records marked Approved = Yes.
Download PDFs that I can lawfully access, organise them by the category or subsection recorded in the spreadsheet, and prepare or import the approved records into Zotero.
Do not bypass paywalls or access controls. Record any unavailable, failed, or unmatched items instead of substituting another paper.
```

**Access note:** If institutional access is required, the user must sign in through the browser themselves, then tell you they are signed in. Never ask for passwords.

## Final check

- Every approved row has a PDF or a clear unavailable note
- Zotero metadata matches the spreadsheet
- Duplicates removed; folders match the review categories

## Workflow

`Search → Verify → Review → Approve → Download → Organise`
