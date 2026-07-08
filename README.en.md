[繁體中文](./README.md) | **English**

> WARNING **Correction Notice (2026-05-28 OVERFIT audit)**
>
> Any conclusions further down in this document such as "V47 NOT OVERFIT", "holdout 92.7%", or "95.5% not overfit" have all been overturned.
> The scoring set has only 10 specs; the post-processing rule thresholds from V37 onward (including V44 95.5% and the final V47) were reverse-engineered spec by spec, which constitutes overfitting to the scoring set.
> See `OVERFIT_AUDIT.md` in the project root for the full per-version determination. Clean submittable versions: V23 (86 of 100 cells correct) or V31 (90 of 100 cells correct, must be noted as the ceiling without adding part-specific rules). The final submission uses the zero-overfit integrated version at 91/100.

---

# Datasheet Parameter Extraction System (NTUST AI Final Project)

Automatically extracts 11 structured spec fields from 10 electronic component datasheet PDFs, compares them against the ground truth in `data/specbook.xlsx` to compute accuracy, and provides a local webapp for upload trials.

> **Submission Package Notes**: This assignment provides two archives — the **DEMO lite version** (core program + webapp + two reports, for a quick trial run) and the **full-record version** (including the complete per-version archive `output/_archive/`, iteration scripts `experiments/`, and logs, for reproducibility verification). The "Directory Structure" below and these notes correspond to the **full-record version / GitHub**; the DEMO lite version contains only a core subset — for the complete version history, see the full-record version or GitHub.

**Final result: 91 / 100 = 91.0% (zero-overfit integrated version, every field ≥ 6/10).** Part Number is a given input for the assignment and is not scored, so the scoring range is 10 fields to extract from the PDF × 10 components = 100 cells. V44/V47 (reaching 105/110) with higher train scores during development were determined to be overfit to the scoring set and are not adopted as the final result; see `OVERFIT_AUDIT.md` for details.

For how the four tasks were completed, the supporting result data, and an honest discussion of overfitting, see **[REPORT.md](REPORT.md)**.

## Four Tasks Mapping

1. **VLM parsing of dimension drawings** — Rasterize the PDF into images and feed them to GPT-4o multimodal to read dimensions from the drawings (drawings that traditional OCR cannot capture).
2. **Enforce 100% valid JSON** — JSON mode at the API layer (Azure `response_format=json_object` / Ollama `format=json`), not prompt begging.
3. **Batch of 10, each field ≥ 50%** — Full run 91/100 (91.0%), with the lowest per-field score being 6/10 (60%), all passing the threshold; see REPORT.md for details.
4. **Local webapp** — `streamlit run app.py`, upload files for a real-time trial.

## Requirements

- Python 3.10+ (verified on 3.11.5)
- Local inference: Ollama (optional)
- Cloud inference: Azure AI Foundry subscription (required for the webapp's real-time extraction)
- camelot extraction requires Ghostscript (optional)

## Installation

```powershell
pip install -r requirements.txt
pip install streamlit          # Task 4 webapp
```

## Configuration

```powershell
Copy-Item .env.example .env
notepad .env   # fill in values
```

Key `.env` variables:

```bash
BACKEND=azure_gpt4o        # ollama / azure_gpt4o / azure_llama / azure_mistral
PDF_EXTRACTOR=multimodal   # pdfplumber / fitz / camelot / multimodal
```

Cloud models additionally require `AZURE_FOUNDRY_ENDPOINT` + `AZURE_FOUNDRY_KEY`; see `AZURE_SETUP.md` for details.

## Running

```powershell
# 1. Evaluate the final result (no LLM re-run, pure comparison of saved results, lists per-version accuracy)
python evaluate_all.py

# 2. Launch the webapp (Task 4)
streamlit run app.py          # local http://localhost:8501
```

The webapp has two sections:
- **Section 1 "10 SPEC demo results"**: Reads pre-computed results — instant, zero API, cell-by-cell comparison against ground truth (red cells are errors), collapsible.
- **Section 2 "Upload PDF and run live"**: Drag multiple files for on-the-spot end-to-end extraction (GPT-4o vision + self-check). The live version is single-model, not the full V47; requires an Azure key.

## Directory Structure

```
ntust-datasheet-extractor/
├── app.py              Task 4 webapp (Streamlit)
├── REPORT.md           Result report (four tasks + data support)
├── README.md
├── main.py             Main flow: extraction + dual-agent iteration + comparison
├── prompts.py          Centralized management of prompts and 11-field rules
├── pdf_extractor.py    PDF parsing abstraction (pdfplumber/fitz/camelot/multimodal switchable)
├── llm_backend.py      LLM backend abstraction (Ollama/Azure GPT-4o/Llama/Mistral switchable)
├── validators.py       Post-processing: unit correction, sanity check
├── qa_critic.py        critic agent (for dual-agent iteration)
├── output_schema.py    strict JSON schema definition
├── iteration_logger.py Iteration process logging
├── crop_extractor.py   Encapsulates dimension-drawing cropping
├── config.py           Paths, fields, comparison thresholds
├── evaluate_all.py     Unified evaluation of all versions' accuracy
├── evaluate_new_5.py   Extra PDF evaluation during development (ground truth not officially checked, not used for the final result)
├── .env.example        Environment variable template
├── AZURE_SETUP.md      Azure AI Foundry deployment guide
├── requirements.txt
├── data/specbook.xlsx  Ground truth
├── datasheets/         10 PDFs
├── output/_archive/    Complete archive of each version (traceable, reproducible)
├── experiments/        Iteration scripts for each version (run_v4 ~ run_v48) + extra PDF extraction
├── scripts/            One-off diagnostic and analysis tools
├── logs/               Execution logs for each version
├── docs/               Course slides and supplementary documents
└── 正式排版報告/       Formally typeset result report in paper format (REPORT_formal.md + docx + generator)
```

## Extracted Fields (11 total)

| # | Field | Type |
|---|---|---|
| 1 | Part Number | str (given part number, fill in directly) |
| 2 | Minimum Operating Temperature(°C) | int |
| 3 | Maximum Operating Temperature (°C) | int |
| 4 | Maximum Length (mm) | float |
| 5 | Maximum Width (mm) | float |
| 6 | Maximum Height (mm) | float |
| 7 | PIN Number | int |
| 8 | I_O、I_F (A) | float |
| 9 | V_F(Forward Voltage) (V) | str (multiple test conditions) |
| 10 | V_RRM(Peak Repetitive Reverse Voltage) (V) | int |
| 11 | I_R(Reverse Current) | str (multiple test conditions) |

## Comparison Rules

| Field type | Rule |
|---|---|
| Numeric (temperature, dimensions, I_O/I_F) | ±5% tolerance |
| Exact match (Part Number, V_RRM, PIN) | String exact equality |
| Text combination (V_F, I_R) | Split tokens by full-width comma, set hit rate ≥ 50% |
