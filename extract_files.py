import re
import os

with open('instruction.idc', 'r', encoding='utf-8') as f:
    lines = f.readlines()

current_file = None
current_content = []
in_code_block = False

for line in lines:
    file_match = re.search(r'^### \d+\.\d+ `([^`]+)`', line)
    if file_match:
        if current_file and current_content:
            os.makedirs(os.path.dirname(current_file), exist_ok=True)
            with open(current_file, 'w', encoding='utf-8') as cf:
                cf.write("".join(current_content))
            print(f"Created {current_file}")
            
        current_file = file_match.group(1)
        current_content = []
        in_code_block = False
        continue

    if current_file:
        if line.startswith('```python') or line.startswith('```javascript') or line.startswith('```json') or line.startswith('```env'):
            in_code_block = True
            continue
        elif line.startswith('```') and in_code_block:
            in_code_block = False
            os.makedirs(os.path.dirname(current_file), exist_ok=True)
            with open(current_file, 'w', encoding='utf-8') as cf:
                cf.write("".join(current_content))
            print(f"Created {current_file}")
            current_file = None
            current_content = []
            continue
            
        if in_code_block:
            current_content.append(line)

if current_file and current_content:
    os.makedirs(os.path.dirname(current_file), exist_ok=True)
    with open(current_file, 'w', encoding='utf-8') as cf:
        cf.write("".join(current_content))
    print(f"Created {current_file}")

