# 🏥 Health Misinformation Detection System

## 🌟 Features

- **🤖 AI-Powered Detection**: Groq Llama3-70B + Gemini 1.5-Flash for medical analysis
- **💊 Drug Safety Integration**: Comprehensive drug interaction & safety database
- **🔍 Multi-Input Support**: Text claims, URLs, articles, forwarded messages
- **🏥 Authoritative Sources**: WHO, CDC, NIH, FDA, PubMed, DrugBank
- **⚡ Real-Time Analysis**: Fast processing with medical-grade accuracy

## 🚀 Quick Start

### Setup:

1. Clone the repository
2. Add your API keys to `config.py`:
   ```python
   GROQ_API_KEY = "your_groq_api_key"
   GEMINI_API_KEY = "your_gemini_api_key"
   ```

### Usage:

```bash
python simple_analyzer.py
```

### Input Examples:

- **Health Claims**: "vitamin C cures cancer"
- **Drug Queries**: "aspirin interactions with warfarin"
- **Article URLs**: "https://www.mayoclinic.org/..."

## 📊 Sample Output

```
🏥 SIMPLE HEALTH ANALYZER
📱 Analyzes health claims with AI + Medical Sources

📥 Enter your health claim:
> Natural sugar is always healthy

🤖 AI Analysis: MISINFORMATION (90% confidence)

📝 CONCISE MEDICAL ANALYSIS:
**VERDICT:** FALSE
**CORRECTION:** Excessive sugar intake, regardless of source, can contribute to health problems.
**EXPLANATION:** All sugars should be consumed in moderation for optimal health.
**SOURCES:**
• PubMed: https://pubmed.ncbi.nlm.nih.gov/31246081/
• Harvard: https://www.hsph.harvard.edu/nutritionsource/carbohydrates/
```

## 🔧 System Architecture

**Phase-Based Pipeline:**

1. **📥 Input Processing** - Handles text, URLs, and content
2. **🤖 AI Detection** - Groq-powered misinformation detection
3. **🔬 Medical Research** - Searches PubMed and drug safety databases
4. **🏥 Fact-Checking** - Gemini AI provides concise corrections with sources

## 🏥 Trusted Medical Sources

- **WHO**: World Health Organization
- **CDC**: Centers for Disease Control
- **PubMed**: Peer-reviewed medical research
- **NIH**: National Institutes of Health
- **FDA**: Food and Drug Administration

## 🚨 Risk Levels

| Level        | Description              | Action Required        |
| ------------ | ------------------------ | ---------------------- |
| **CRITICAL** | Dangerous misinformation | Immediate intervention |
| **HIGH**     | Likely misinformation    | Verify before acting   |
| **MEDIUM**   | Uncertain claims         | Consult professionals  |
| **LOW**      | Appears reasonable       | Still verify sources   |

## 📁 Key Files

```
SDGforge_hackathon-main/
├── simple_analyzer.py          # Main application
├── config.py                   # API configuration
├── phase1_user_input.py        # Input processing
├── phase4_misinformation_detection.py  # AI detection
├── phase5_trusted_source_retrieval.py # Medical sources
├── phase6_fact_correction.py   # Fact-checking
├── real_medical_apis.py        # Backend APIs
└── browser-extension/          # Chrome extension
```

## 🌐 Browser Extension

A Chrome/Edge extension is included for real-time webpage fact-checking:

- Right-click any medical text → "Verify Medical Fact"
- Color-coded banners (Green/Yellow/Red)
- Dashboard with statistics and charts

## ⚖️ Disclaimer

This software is for informational purposes only. Always consult qualified healthcare professionals for medical advice.

## 🤝 License

MIT License - Feel free to use and modify.

---

**Made with ❤️ for global health safety**
**Powered by AI for maximum accuracy** 🚀
