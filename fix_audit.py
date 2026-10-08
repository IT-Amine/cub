import os
import re
from pathlib import Path

def fix_all():
    docs_dir = Path('docs')
    for filepath in docs_dir.rglob('*.md'):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        
        # 1. Remove ## Informations blocks
        content = re.sub(r'## Informations\n\n\*\*Auteur :.*?\n\*\*Date :.*?\n\*\*Domaine :.*?\n+', '', content)
        
        # 2. Global Typos
        content = content.replace('Résutltat', 'Résultat')
        content = content.replace('instannée', 'instantanée')
        content = content.replace('siopic.fr', 'sioplc.fr')
        content = content.replace('dortmound', 'dortmund')
        content = content.replace('vitrio', 'virtio')
        content = content.replace('personalisee', 'personnalisee')
        content = content.replace('réseaux', 'Réseaux') # For tables-nat

        # Specific fixes per file
        filename = filepath.name
        
        if filename == 'config-ad.md':
            # Fix Start-Process
            content = content.replace('Start-Process\n```', 'Start-Process -FilePath "D:\\virtio-win-guest-tools.exe"\n```')
            # Fix Get-NetFirewallProfile
            content = content.replace('Get-NetFirewallProfile\nSelect-Object Name, Enabled # Filtre l\'affichage pour confirmer que chaque profil réseau dispose du pare-feu actif.', 
                                      '')
            # Indent warning
            content = re.sub(r'(!!! warning "Action requise"\n)([^\s])', r'\1    \2', content)

        elif filename == 'configuration-windows-core.md':
            content = content.replace('"9.9.9.9", "8.8.8.8", "1.1.1.1"', '"192.168.4.11", "192.168.4.10"')
            content = content.replace('"MotDePasseBitwardenIci"', '"<MOT_DE_PASSE_BITWARDEN>"')

        elif filename == 'creation-compte-administrer-wac.md':
            content = content.replace('etudiant_007', '<MOT_DE_PASSE>')

        elif filename == 'plan-adressage.md' or filename == 'tables-nat.md':
            # Fix tables extra | at end of header
            content = re.sub(r'\|\n\|---', '\n|---', content)
            
        elif filename == 'tables-routage.md':
            content = content.replace('## 4. Tables de routage', '## 3. Tables de routage')
            
        elif filename == 'git.md':
            content = content.replace('./git-push.jpg', './git-img/git-push.jpg')
            content = content.replace('# BLOC 2 - Admin.Sys', '# BLOC 2 - Gestion de versions avec Git & GitHub')
            
        elif filename == 'exploitation-services.md':
            content = content.replace('# BLOC 2 - Installation de l\'outil htop', '# BLOC 2 - Fiche de révision : Exploitation des services Debian')
            content = content.replace('```\n', '```bash\n')
            content = content.replace('```bash\n```bash', '```bash') # fix double if already there
            content = content.replace('**gérer les versions', '**gérer les versions**')
            
        elif filename == 'installation-paquets-commun-debian.md':
            content = content.replace('sudo apt update && apt install -y', 'sudo apt update && sudo apt install -y')

        elif filename == 'guacamole-installation.md':
            # Remove empty lines between --- and # BLOC 2
            content = re.sub(r'---\n\n+# BLOC 2', '---\n\n# BLOC 2', content)

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed {filepath}")

fix_all()
