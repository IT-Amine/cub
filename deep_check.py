import os
import re
from pathlib import Path

docs_dir = Path('docs')

print("--- RECHERCHE DE CHECKBOX NON COCHEES (Recettes non validées) ---")
for md in docs_dir.rglob('*.md'):
    with open(md, 'r', encoding='utf-8') as f:
        content = f.read()
    if '[ ]' in content:
        print(f"⚠️ {md} contient des cases '[ ]'")

print("\n--- RECHERCHE DE BLOCS DE CODE SANS LANGAGE ---")
for md in docs_dir.rglob('*.md'):
    with open(md, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip() == '```':
            print(f"⚠️ {md} Ligne {i+1} : bloc de code sans langage")

print("\n--- RECHERCHE DE TODO / A FAIRE ---")
for md in docs_dir.rglob('*.md'):
    with open(md, 'r', encoding='utf-8') as f:
        content = f.read()
    if re.search(r'(?i)TODO|A FAIRE|XXX', content):
        print(f"⚠️ {md} contient un TODO")

print("\n--- VERIFICATION DES ADRESSES IP DANS CISCO ---")
import glob
for txt in glob.glob('docs/ressources/configurations/*.txt'):
    with open(txt, 'r', encoding='utf-8') as f:
        print(f"\nConfiguration: {txt}")
        lines = f.readlines()
        for line in lines:
            if 'ip address' in line.lower() or 'vlan' in line.lower():
                print(line.strip())

