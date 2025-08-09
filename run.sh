#!/bin/bash

cd "$(dirname "$0")"

VENV_DIR="venv"

# Vérifie si le venv existe
if [ ! -d "$VENV_DIR" ]; then
    echo "⚙️  Création du venv..."
    python3 -m venv "$VENV_DIR" || {
        echo "❌ Échec de la création du venv."
        exit 1
    }
fi

# Mise à jour de pip
"$VENV_DIR/bin/pip" install --upgrade pip

# Installer les dépendances depuis requirements.txt
if [ -f "requirements.txt" ]; then
    echo "📦 Installation des dépendances..."
    "$VENV_DIR/bin/pip" install -r requirements.txt
else
    echo "⚠️ Aucun fichier requirements.txt trouvé. Dépendances non installées."
fi

# Lancer le programme principal
echo "🚀 Lancement de main.py..."
"$VENV_DIR/bin/python" main.py



