# AI for Responsible Health Information
# Simple IDC Instruction File

[PROJECT]
name = ResponsibleHealthAI
description = AI tool to detect and correct health misinformation using trusted sources.
author = YourName
version = 1.0

[DATA_INPUT]
# APIs for trusted health data
trusted_sources = WHO_API, CDC_API, PubMed_API
user_input_methods = WebForm, ChatInterface, EmailInput
optional_automation = n8n_orchestration=false

[CONTENT_EXTRACTION]
article_parser = newspaper3k
language_detection = langdetect

[NLP_PREPROCESSING]
tokenization = spacy
normalization = spacy
ner_model = spacy_medical

[MISINFORMATION_DETECTION]
# Primary detection models
model_primary = BioBERT
model_primary_source = huggingface_inference_api
# Fallback classification
model_fallback = openai_gpt_zero_shot

[RAG_FACT_RETRIEVAL]
retrieval_sources = WHO_API, CDC_API, PubMed_API
embedding_model = openai_text_embedding_ada
vector_db = local_faiss_index
chunk_size = 512
overlap = 50

[FACT_CORRECTION]
llm_model = openai_gpt_4
simplification = true
tone = easy_to_understand

[OUTPUT_DELIVERY]
channels = TelegramBot, WhatsAppCloudAPI, EmailSMTP
dashboard = flask_bootstrap
log_storage = local_json

[EXECUTION_FLOW]
1 = Fetch user content
2 = Extract and clean text
3 = Detect misinformation using model_primary
4 = If uncertain → model_fallback
5 = Retrieve authoritative info (RAG retrieval)
6 = Correct facts & simplify explanation
7 = Send output via selected channels
8 = Log results locally


Goal: Build a Chrome/Edge browser extension that integrates with my Python backend for AI-powered medical fact verification using the Llama 3 70B 8192 model.

Requirements:

Context Menu Trigger

When a user highlights text on any webpage, right-click, and select "Verify Medical Fact".

Backend Request

Send the selected text (and current page URL) via POST request to:

bash
Copy code
POST https://my-backend.com/api/verify  
Content-Type: application/json  
Body: { "text": "<selected_text>", "source_url": "<page_url>", "model": "llama3-70b-8192" }
The backend runs the Llama 3 70B 8192 model for fact verification and returns JSON like:

json
Copy code
{
  "status": "harmful" | "safe" | "caution",
  "corrected_fact": "string",
  "explanation": "string",
  "source_links": ["https://who.int", "https://cdc.gov"]
}
Banner Injection in Page

Inject a small color-coded banner over or near the highlighted text:

Green → Safe

Yellow → Caution

Red → Harmful

Use content.js to insert HTML/CSS dynamically.

Hover/Click Panel

On hover or click, open a small collapsible panel showing:

Corrected fact in simple language.

Explanation from Llama 3 70B.

Clickable trusted source links.

Popup Dashboard (popup.html)

Show total number of flags in the current session.

Pie chart of flagged health topics (Chart.js).

List of domains where misinformation was found.

Manifest v3 Setup

Permissions: "contextMenus", "activeTab", "scripting", "storage".

Background service worker in background.js for context menu + API calls.

content.js for DOM injection.

popup.js for dashboard logic.

Styling

Clean, readable CSS for banners (rounded corners, shadow, bold labels).

Dashboard with light/dark theme support.

Deliverables:

manifest.json

background.js

content.js

popup.html, popup.js, popup.css

Any necessary assets (icons, styles)

Constraints:

Full working extension ready for Chrome’s “Load unpacked” mode.

Code must be self-contained; avoid external dependencies except Chart.js.

Comment each major function for clarity.