import os
import re
from pathlib import Path

def replace_in_file(filepath, old, new):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = content.replace(old, new)
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

docs_path = Path("docs")

# Fix schemas.md
replace_in_file(docs_path / "ressources/schemas.md", 
                "./schemas/cub-schema-physique-gp4.pdf", 
                "./schemas/cub-schema-physique-gp4.drawio.pdf")
replace_in_file(docs_path / "ressources/schemas.md", 
                "./schemas/cub-schema-logique-gp4.pdf", 
                "./schemas/cub-schema-logique-gp4.drawio.pdf")
replace_in_file(docs_path / "ressources/schemas.md", 
                "./schemas/cub-schema-brassage-gp4.pdf", 
                "./schemas/cub-schema-brassage-gp4.drawio.pdf")

# Fix communs
replace_in_file(docs_path / "services/communs/installation-paquets-commun-debian.md",
                "../../../assets/communs/motd.txt",
                "../../assets/communs/motd.txt")

# Fix windows core
replace_in_file(docs_path / "windows/core/configuration-windows-core.md",
                "../../../assets/windows-core/",
                "../../assets/windows-core/")

# Fix windows wac
replace_in_file(docs_path / "windows/wac/installation-wac.md",
                "../../../assets/windows-wac/",
                "../../assets/windows-wac/")

replace_in_file(docs_path / "windows/wac/ajout-serveur-wac.md",
                "../../../assets/windows-wac/",
                "../../assets/windows-wac/")

# Fix stormshield
replace_in_file(docs_path / "securite/stormshield/problemes/resolution-erreur-derives-ethernet.md",
                "../../../../assets/stormshield-problemes/",
                "../../../assets/stormshield-problemes/")

