# 🧪 TDD Implementation Guide: Health Misinformation Detection

This document outlines a phase-wise **Test-Driven Development (TDD)** roadmap for building and refining the Health Misinformation Detection System. Follow the **Red-Green-Refactor** cycle for each phase.

---

## 🛠 Phase 0: Testing Infrastructure
**Goal:** Set up the environment and base test classes.

1.  **Setup:** Ensure `pytest` and `pytest-mock` are installed.
2.  **Mocking Strategy:** Create a `conftest.py` to globalize mocks for external APIs (Groq, Gemini, PubMed) to avoid hitting rate limits during TDD.

---

## 📥 Phase 1: Input Classification (Phase 1)
**Goal:** Accurately categorize user input (URL, Text, Image, Forwarded Message).

### 🔴 Red (Test)
- Write tests in `tests/test_phase1.py` for:
    - `test_identify_url()`: Should recognize `https://...`
    - `test_identify_forwarded()`: Should recognize "Forwarded" headers.
    - `test_identify_short_claim()`: Should categorize 10-word text as `plain_text`.

### 🟢 Green (Implement)
- Refine `phase1_user_input.py` to pass all classification tests.

### 🔵 Refactor
- Optimize regex patterns for URL detection.

---

## 🔍 Phase 2: Content Retrieval & Vision (Phase 2)
**Goal:** Extract text from various sources including images.

### 🔴 Red (Test)
- `test_extract_text_from_html()`: Mock a requests response and verify HTML tags are stripped.
- `test_vision_fallback_mock()`: Mock Gemini Vision API to return "Extracted Claim" from a base64 string.

### 🟢 Green (Implement)
- Update `phase2_content_retrieval.py` with robust HTML cleaning and `get_gemini_vision_text` logic.

---

## 🤖 Phase 3: Multi-Agent Misinformation Detection (Phase 4)
**Goal:** Implement the Proponent/Skeptic/Adjudicator debate logic.

### 🔴 Red (Test)
- `test_debate_logic_flow()`: Verify that `detect_misinformation` calls the Proponent, then Skeptic, then Adjudicator in order.
- `test_risk_level_assignment()`: Verify "Drink Bleach" returns `risk_level: critical`.
- `test_user_profile_impact()`: Test if a profile with "Statin medication" increases risk for "Grapefruit" claims.

### 🟢 Green (Implement)
- Refine `phase4_misinformation_detection.py`. Ensure the Adjudicator prompt strictly enforces JSON output.

---

## 🔬 Phase 4: Agentic Trusted Source Retrieval (Phase 5)
**Goal:** Implement autonomous tool-calling for medical databases.

### 🔴 Red (Test)
- `test_tool_selection()`: Verify the agent chooses `fetch_via_api` for "FDA" when a drug query is detected.
- `test_source_formatting()`: Ensure returned sources have `source`, `url`, and `snippet`.

### 🟢 Green (Implement)
- Enhance `phase5_trusted_source_retrieval.py` to handle dynamic tool execution results.

---

## 🏥 Phase 5: Fact Correction & Proof Chain (Phase 6)
**Goal:** Generate the final patient-safe correction with a visible logic path.

### 🔴 Red (Test)
- `test_proof_chain_accumulation()`: Verify the `proof_chain` array grows correctly through all phases.
- `test_verdict_format()`: Ensure the output contains `**VERDICT:**`, `**CORRECTION:**`, and `**SOURCES:**`.

### 🟢 Green (Implement)
- Finalize `phase6_fact_correction.py` using `correct_misinformation_with_chain`.

---

## 🌐 Phase 6: API & Extension Integration
**Goal:** End-to-end connectivity between the Browser Extension and Flask.

### 🔴 Red (Test)
- `test_api_verify_endpoint()`: Use Flask `test_client` to send a full payload and assert a 200 OK with a `safe/harmful` status.
- `test_cors_headers()`: Ensure the extension can communicate with the backend.

### 🟢 Green (Implement)
- Finalize `simple_backend.py`.
- Update `browser-extension/content.js` to handle the `proof_chain` and display the banner.

---

## 🚀 Phase 7: Final Validation & Stress Testing
**Goal:** Production readiness.

- **Load Testing:** Run 10 simultaneous requests to `simple_backend.py`.
- **Edge Cases:** Test with empty strings, 5000-word articles, and non-English text.
- **Security:** Ensure no API keys are leaked in error responses.

---
**Note:** Always run `pytest` after every change to ensure zero regressions.
