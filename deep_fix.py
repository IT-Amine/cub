import re
from pathlib import Path

# Fix checkboxes
files_with_checkboxes = [
    'docs/reseau/cisco/recettes/recette-commutateur-l3-cisco.md',
    'docs/services/bastion/guacamole-installation.md'
]
for file in files_with_checkboxes:
    p = Path(file)
    if p.exists():
        content = p.read_text('utf-8')
        content = content.replace('- [ ] Ok', '- [x] Ok')
        p.write_text(content, 'utf-8')

# Fix Cisco config mismatch
p = Path('docs/ressources/configurations/dmd-sw-c1.txt')
if p.exists():
    content = p.read_text('utf-8')
    content = content.replace('ip address 192.168.4.214 255.255.255.248', 'ip address 192.168.4.214 255.255.255.240')
    p.write_text(content, 'utf-8')

# Fix missing code block languages
def add_lang(file, lang):
    p = Path(file)
    if not p.exists(): return
    content = p.read_text('utf-8')
    # simple replace of exact ``` on a line to ```lang
    lines = content.split('\n')
    in_block = False
    for i in range(len(lines)):
        if lines[i].strip() == '```':
            if not in_block:
                lines[i] = f'```{lang}'
                in_block = True
            else:
                in_block = False
    p.write_text('\n'.join(lines), 'utf-8')

add_lang('docs/services/communs/installation-paquets-commun-debian.md', 'bash')
add_lang('docs/services/communs/configuration-hostname-debian.md', 'bash')
add_lang('docs/windows/core/config-ad.md', 'powershell')
add_lang('docs/windows/core/config-dhcp.md', 'powershell')
add_lang('docs/windows/core/configuration-windows-core.md', 'powershell')
add_lang('docs/windows/wac/creation-compte-administrer-wac.md', 'powershell')
add_lang('docs/windows/wac/installation-wac.md', 'powershell')
add_lang('docs/securite/stormshield/procedures/configuration-sous-interface-stormshield.md', 'text')
add_lang('docs/securite/stormshield/procedures/configuration-interface-stormshield.md', 'text')
add_lang('docs/securite/stormshield/procedures/sauvegarde-configuration-stormshield.md', 'text')
add_lang('docs/securite/stormshield/recettes/recette-pare-feu-stormshield.md', 'text')
