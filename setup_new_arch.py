import os
import shutil

dirs = [
    'backend/agent',
    'backend/phases',
    'backend/mcp',
    'backend/cache',
    'extension/icons'
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    init_file = os.path.join(d, '__init__.py')
    if 'cache' in d or 'agent' in d or 'mcp' in d:
        open(init_file, 'a').close()
open('backend/__init__.py', 'a').close()
open('backend/phases/__init__.py', 'a').close()

files_to_move = {
    'phase1_user_input.py': 'backend/phases/phase1_user_input.py',
    'phase2_content_retrieval.py': 'backend/phases/phase2_content_retrieval.py',
    'phase4_misinformation_detection.py': 'backend/phases/phase4_misinformation_detection.py',
    'phase5_trusted_source_retrieval.py': 'backend/phases/phase5_trusted_source_retrieval.py',
    'phase6_fact_correction.py': 'backend/phases/phase6_fact_correction.py',
    'real_medical_apis.py': 'backend/real_medical_apis.py',
    'config.py': 'backend/config_backup.py',
}

for src, dst in files_to_move.items():
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"Moved {src} to {dst}")

print("Architecture directories created and files moved.")
