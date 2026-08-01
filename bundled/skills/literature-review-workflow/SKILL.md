---
name: literature-review-workflow
description: |
  AI-based literature review workflow guide (search → verify → Excel review → approve → lawful PDF download → Zotero).
  Use when the user asks how to run a literature review with academic-search and sciencedirect-live-session-fetcher,
  needs standardised search/download prompts, screening categories (Core / Background / Pending Verification),
  or the AI_Based_Literature_Review_Workflow process.
metadata:
  version: "1.0.0"
---

# AI-Based Literature Review Workflow

A practical step-by-step template for searching, checking, downloading, and organising academic literature.

Companion skills:

1. `academic-search` — verified literature search and structured Excel export
2. `sciencedirect-live-session-fetcher` — lawful serial PDF download through a live browser session

## Overview

Keep the process simple:

1. Install an AI coding assistant (Codex / Claude Code / Cursor)
2. Install the literature-search and download skills
3. Run a verified literature search
4. Review the Excel output and mark `Approved = Yes/No`
5. Download approved papers you can lawfully access
6. Organise into Zotero and reconcile

Replace bracketed placeholders with your own review requirements.

## Step 1 — Install Codex, Claude Code, or Cursor

- Install and sign in to your preferred coding assistant
- Open or create a project folder for literature-review files
- Confirm the assistant can create, read, and edit files in this folder

## Step 2 — Add skills

Install:

- Literature search: `academic-search`
- Automatic literature downloading: `sciencedirect-live-session-fetcher`
- This workflow guide: `literature-review-workflow`

## Step 3 — Run the literature search

Invoke `$academic-search` with a structured prompt covering topic, scope, keywords, inclusion rules, verification rules, and output fields.

### Standard search prompt

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

### Output groups

| Group | Meaning |
|-------|---------|
| Core Literature | Directly addresses the research question and is sufficiently verified for the main evidence table |
| Background Literature | Provides theory, definitions, models, methods, or context but does not answer the main question |
| Pending Verification | Appears relevant, but details still need checking |

## Step 4 — Review and adjust the Excel output

Human quality-control gate:

- Open the DOI / official URL and confirm title, authors, year, journal, version
- Check topic match and inclusion criteria
- Resolve preprint / conference / journal duplicates; keep the preferred final version
- Adjust category / subsection when needed
- Mark unknowns as `Not verified` rather than guessing
- Add `Approved = Yes/No` before download

## Step 5 — Download approved PDFs and organise in Zotero

Attach the reviewed Excel, invoke `$sciencedirect-live-session-fetcher`, and process only `Approved = Yes`.

### Standard download prompt

```text
$sciencedirect-live-session-fetcher
Please process the attached Excel file. Only process records marked Approved = Yes.
Download PDFs that I can lawfully access, organise them by the category or subsection recorded in the spreadsheet, and prepare or import the approved records into Zotero.
Do not bypass paywalls or access controls. Record any unavailable, failed, or unmatched items instead of substituting another paper.
```

**Access note:** When using a university or organisational subscription, sign in through the browser yourself, then tell the assistant you are signed in. Do **not** provide your password to the assistant.

## Step 6 — Final quality check

Before detailed reading or synthesis:

- Every approved Excel record has either a matching PDF or a clear unavailable/failed note
- Zotero titles, authors, years, journals, and DOIs match the verified spreadsheet
- Duplicates are merged or removed
- Collections / folders follow the same category structure
- Excel and Zotero library are backed up

## Workflow complete

`Search → Verify → Review → Approve → Download → Organise`

Source document: `AI_Based_Literature_Review_Workflow_Refined-20260730.docx`
