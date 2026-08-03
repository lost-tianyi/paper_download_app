---
name: literature-review-workflow
description: |
  Guide users through the AI literature-review workflow in chat:
  project setup → structured search → Excel human review → approve →
  lawful PDF download → Zotero organise → final quality check.
  Use when the user wants to start a literature review, mentions
  literature-review-workflow / academic-search, or asks how to search
  and download papers with the installed skills.
  Prefer interactive step-by-step guidance; do not ask users to open
  documentation files themselves.
metadata:
  version: "1.2.0"
---

# Literature Review Workflow (Interactive Guide)

Source template: *AI-Based Literature Review Workflow*  
(`AI_Based_Literature_Review_Workflow_Refined-20260730.docx`)

End-to-end path:

`Install → Add skills → Search → Check Excel → Download & Zotero → Final quality check`

(The installer already covers Install + Add skills. This skill guides everything after that.)

## How you should guide the user

The user may not be technical and may not know what Markdown, Excel columns, or “skills” mean.

**Do:**

- Run the workflow **in this conversation**, one stage at a time.
- Use plain language. Prefer short numbered actions (“请做这两件事…”).
- After each stage, say **what just happened**, **what they should do next**, and **what you will do after they reply**.
- Wait for explicit confirmation before moving to the next stage.
- Fill prompts for them from their answers; do not dump a long template and ask them to edit it alone.

**Do not:**

- Ask them to open, find, or read any documentation / `.md` files.
- Skip the human Excel review / `Approved` gate.
- Ask for account passwords.
- Bypass paywalls or access controls.
- Invent or guess titles, authors, years, journals, DOIs, methods, or findings.

## Companion capabilities

1. `$academic-search` — search, verify, and export the literature spreadsheet  
2. `$sciencedirect-live-session-fetcher` — download PDFs the user can lawfully access (live browser session), then organise / prepare Zotero import

---

## Stage 0 — Workspace check (quick)

Before searching:

1. Confirm there is a project folder for literature-review files (or help create one).
2. Confirm you can create, read, and edit files in that folder.
3. Confirm their **research topic** (and years / journal scope / document types if they already know them).

If anything is missing, ask only for what you still need — one short question at a time.

---

## Stage 1 — Run the literature search

**Goal:** Produce a verified literature spreadsheet the user can review.

1. Collect or confirm: topic, year range, journal scope, document types, keywords / synonyms / exclusions, inclusion rules, target number (without lowering standards to fill quotas).
2. Invoke `$academic-search` with a **filled** prompt (replace all placeholders). Prefer the standard prompt below.
3. Require verification via an official publisher page **and** at least one authoritative source (DOI/Crossref, IEEE Xplore, PubMed, Scopus, Web of Science, etc.).
4. Export an Excel (or equivalent) table and explain the three groups in plain language.
5. Stop and ask the user to open the spreadsheet and review it before any download.

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

### Result groups (explain in plain language)

| Group | Meaning for the user |
|-------|----------------------|
| Core Literature | Directly addresses the research question and is sufficiently verified for the main evidence table |
| Background Literature | Provides theory, definitions, models, methods, or context, but does not directly answer the main question |
| Pending Verification | Appears relevant, but publication details, full text, version, or findings still need checking |

Also report: search strings, search date, sources, and verification statistics.

---

## Stage 2 — Review and adjust the Excel output (human gate)

**Goal:** Human quality control. Nothing is downloaded until this stage is done.

Tell the user clearly: this spreadsheet is the checkpoint that keeps irrelevant, duplicated, misclassified, or poorly verified records out of the final library.

Ask them to work through the file and confirm when finished. Guide them with this checklist:

1. Open the DOI or official URL; confirm title, authors, year, journal, and publication version.
2. Check that the study genuinely matches the topic and inclusion criteria.
3. Resolve preprint / conference / journal duplicates; keep the preferred final version.
4. Review the assigned category and subsection; adjust when necessary.
5. Mark missing information as `Not verified` rather than guessing.
6. Add (or fill) an approval field: `Approved = Yes` / `No` before the download step.

When they say review is done, briefly confirm:

- How many rows are `Approved = Yes`
- Whether any important rows are still `Pending Verification`
- That you will only download approved rows

Do **not** start downloading until they confirm.

---

## Stage 3 — Download approved PDFs and organise in Zotero

**Goal:** Turn the verified spreadsheet into an organised full-text library that preserves the review categories.

1. If institutional / organisational access is needed: ask the user to sign in through the open browser **themselves**, then tell you they are signed in. Never ask for a password.
2. Attach / use the reviewed Excel file.
3. Invoke `$sciencedirect-live-session-fetcher` with the standard download prompt.
4. Process **only** `Approved = Yes` records.
5. Organise PDFs by the category or subsection recorded in the spreadsheet.
6. Prepare or import the approved records into Zotero (collections/folders should mirror those categories).
7. Record unavailable, failed, or unmatched items clearly — never substitute another paper.

### Standard download prompt

```text
$sciencedirect-live-session-fetcher
Please process the attached Excel file. Only process records marked Approved = Yes.
Download PDFs that I can lawfully access, organise them by the category or subsection recorded in the spreadsheet, and prepare or import the approved records into Zotero.
Do not bypass paywalls or access controls. Record any unavailable, failed, or unmatched items instead of substituting another paper.
```

**Access note:** University or organisational subscription → user signs in via the browser, then tells the assistant they are signed in. Use only access they are authorised to use.

---

## Stage 4 — Final quality check

**Goal:** Make the collection auditable before detailed reading or synthesis.

Compare **approved Excel records**, **downloaded PDF folders**, and the **Zotero library**:

1. Every approved Excel record has either a matching PDF or a clear unavailable / failed note.
2. Zotero titles, authors, years, journals, and DOIs match the verified spreadsheet.
3. Duplicate items have been merged or removed.
4. Collections and folders follow the same category structure as the spreadsheet.
5. Remind the user to back up the Excel file and Zotero library before coding or synthesis begins.

Report a short reconciliation summary (counts: approved / downloaded / missing / failed), then say the workflow is complete.

---

## Workflow complete

`Search → Verify → Review → Approve → Download → Organise → Final check`
