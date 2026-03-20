import sys

with open('phase6_fact_correction.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_func = '''
def correct_misinformation_with_chain(claim, sources, misinformation_analysis, proof_chain_input=None):
    \"\"\"
    Wrapper for Phase 6 that handles proof_chain accumulation
    \"\"\"
    print("🩺 Phase 6: Fact-Checking with Proof Chain...")

    # Initialize proof_chain if not provided
    proof_chain = proof_chain_input.copy() if proof_chain_input else []

    # Call existing Phase 6 logic
    corrected_facts = gemini_fact_correction(claim, sources, misinformation_analysis)

    # Add Phase 6 completion to proof_chain
    if misinformation_analysis:
        proof_chain.append({
            "node": f"Fact-Check: {misinformation_analysis.get('verdict', 'uncertain').replace('_', ' ').title()}",
            "type": "fact_check",
            "verdict": misinformation_analysis.get('verdict', 'uncertain'),
            "risk_level": misinformation_analysis.get('risk_level', 'medium')
        })

    print("✅ Fact-check completed with proof chain")

    return {
        'corrected_fact': corrected_facts,
        'proof_chain': proof_chain
    }

def gemini_fact_correction'''

if 'def correct_misinformation_with_chain' not in text:
    text = text.replace('def gemini_fact_correction', new_func)
    
    with open('phase6_fact_correction.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated phase 6")
else:
    print("Already updated phase 6")
