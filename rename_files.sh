#!/bin/bash
cd docs

# BLOC 2
mv "bloc2/BLOC 2 - Commande CUB.md" "bloc2/commande-cub.md"
mv "bloc2/BLOC 2 - Exploitation des services.md" "bloc2/exploitation-services.md"
mv "bloc2/BLOC 2 - Windows Server Core Configuration.md" "bloc2/config-ad.md"

# BLOC 3
mv "bloc3/BLOC 3 - Config DNS Recursif.md" "bloc3/config-dns-recursif.md"
mv "bloc3/BLOC 3 - Cybersécurité VLSM & Table de routage CUB.md" "bloc3/vlsm-routage.md"
mv "bloc3/BLOC 3 - Cybersécurité CUB.md" "bloc3/cybersecurite-cub.md"

# Assets Schema
mv "assets/schema/dortmund-schema-physique-gp4.drawio.pdf" "assets/schema/schema-physique.pdf"
mv "assets/schema/dortmund-schema-logique-gp4.drawio.pdf" "assets/schema/schema-logique.pdf"
mv "assets/schema/dortmund-schema-brassage-gp4.pdf" "assets/schema/schema-brassage.pdf"
mv "assets/schema/schemaphysiquecub.png" "assets/schema/schema-physique-cub.png"
mv "assets/schema/schemalogiquecub.png" "assets/schema/schema-logique-cub.png"

# Assets Cisco
mv "assets/cisco/maquette_physical.jpg" "assets/cisco/maquette-physique.jpg"
mv "assets/cisco/maquette_logique.jpg" "assets/cisco/maquette-logique.jpg"

# Assets Resource
mv "assets/resource/template_procedure.md" "assets/resource/template-procedure.md"
mv "assets/resource/referentiel-competences-bts-sio.pdf" "assets/resource/referentiel-bts.pdf"

# Assets Root
mv "assets/banniere_cub.png" "assets/banniere-cub.png"

# Fix internal references in markdown files using sed (macOS sed syntax requires '' after -i)
# Replace references to banniere_cub.png
find . -type f -name "*.md" -exec sed -i '' 's/banniere_cub.png/banniere-cub.png/g' {} +

# Replace references to schema images
find . -type f -name "*.md" -exec sed -i '' 's/schemalogiquecub.png/schema-logique-cub.png/g' {} +
find . -type f -name "*.md" -exec sed -i '' 's/schemaphysiquecub.png/schema-physique-cub.png/g' {} +

# Replace references to cisco maquettes
find . -type f -name "*.md" -exec sed -i '' 's/maquette_logique.jpg/maquette-logique.jpg/g' {} +
find . -type f -name "*.md" -exec sed -i '' 's/maquette_physical.jpg/maquette-physique.jpg/g' {} +

