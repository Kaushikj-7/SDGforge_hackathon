# TruthLens - Progress & Architecture

## Core Mission
An AI-powered information equity platform to combat health misinformation (SDG 3: Good Health & SDG 10: Reduced Inequalities). Moves beyond simple medical checking to provide deep, accessible truth verification.

## Architecture

Our stack relies on **5 Parallel Specialized Agents**, processing claims in real-time, backed by a robust, non-blocking FastApi backend.

### 1. The Multi-Agent Swarm (Backend)
- **Agent 1: Claim Detector (Groq/Llama-3)**: Rapidly classifies if text contains a health claim, the severity of the claim, and early misinformation scores.
- **Agent 2: Authoritative RAG (NIH PubMed)**: Real-time queries to National Institutes of Health databases to fetch peer-reviewed abstracts instantly validating/debunking the claim.
- **Agent 3: Policy / Guidelines (WHO/FDA)**: MCP integration pulling live alerts and drug labels.
- **Agent 4: Compassionate Correction (Groq)**: Synthesizes evidence into an empathetic, easy-to-understand explanation to combat algorithmic anxiety.
- **Agent 5: Bias & Inequality Detector (Groq)**: Analyzes how the misinformation specifically marginalizes vulnerable populations (SDG 10 emphasis).

All agent outputs are fused using a **Bayesian P(true) Aggregator**, which computes a final confidence score and risk risk level (LOW/MEDIUM/HIGH/CRITICAL).

### 2. The Multilingual Equity Layer
Powered by langdetect and Groq LLMs:
- Auto-detects 15+ native languages.
- Translates the user's claim to English for the intensive medical reasoning swarm.
- Re-translates the final compassionate correction *back* into the user's native language.

### 3. Multimodal Analysis (Vision)
- Allows users to drag-and-drop screenshots (like WhatsApp memes or Instagram stories) directly into the browser extension popup.
- Uses llama-3.2-11b-vision-preview via Groq to extract underlying text and immediately run it through the 5-agent swarm verification.

### 4. The Extension Frontend (Manifest V3)
- Fully decoupled, Shadow DOM-isolated content script.
- Bypasses host site CSS constraints to cleanly inject validation UI over text selections.
- Real-time Server-Sent Events (SSE) streaming updates user without blocking page interactions.

---

## Progress Report (Current State)

### ✅ Completed
- [x] **Core Backend Server**: Built fully typed FastAPI backend running efficiently (relocated to port 8001 for stability).
- [x] **5-Agent Swarm**: Parallel execution of Groq and MCP components.
- [x] **Browser Extension UI/UX Rewrite**: Polished popups containing "TruthLens" SDG branding, real-time analytics integration, and dynamic Shadow DOM hover states.
- [x] **Multilingual Integration**: Native language detection and translation loops functional.
- [x] **Real-Time Database RAG**: Fully integrated live NIH PubMed evidence fetching, stripping out old placeholder logic.
- [x] **Multimodal UI & Backend**: Drag-and-drop image upload available in the popup dashboard; backend routes requests to the 11b-vision model to extract text.

### ⏳ Pending/Next Steps
- [ ] **Background Auto-Scanner**: A toggleable feature in the extension that continuously scans text nodes on a page (like Twitter/X) in the background to automatically highlight high-risk misinformation without a user prompting it.

