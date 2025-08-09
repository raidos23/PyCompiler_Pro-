© 2025 PyCompiler_Pro++
by Samuel Amen AGUE

# Dossier `utils` — Documentation détaillée

Ce dossier regroupe tous les modules utilitaires de PyCompiler Pro++. Il centralise la logique non spécifique à l’interface graphique, facilitant la maintenance, la réutilisation et l’extension du projet.

## Table des matières
- [Vue d’ensemble](#vue-densemble)
- [Description détaillée des fichiers](#description-detaillee-des-fichiers)
- [Architecture et interactions](#architecture-et-interactions)
- [Conseils d’utilisation et d’extension](#conseils-dutilisation-et-dextension)
- [Exemples d’utilisation](#exemples-dutilisation)
- [Bonnes pratiques](#bonnes-pratiques)

---

## Vue d’ensemble
Le dossier `utils` contient :
- La logique de compilation (PyInstaller, Nuitka)
- La gestion des préférences utilisateur
- L’analyse et l’installation des dépendances Python et système
- Les boîtes de dialogue personnalisées
- L’intégration de la protection PyArmor
- Des fonctions d’aide à la gestion de fichiers, logs, etc.

## Description détaillée des fichiers

### `compiler.py`
- **Rôle** : Gère toute la logique de compilation (PyInstaller, Nuitka), la file d’attente, la gestion des processus, la construction des commandes, la gestion des erreurs et des logs.
- **Fonctions clés** :
  - `compile_all(self)` : Lance la compilation de tous les fichiers sélectionnés.
  - `start_compilation_process(self, file)` : Démarre la compilation d’un fichier.
  - `handle_stdout/handle_stderr/handle_finished` : Gestion des sorties et de la fin de compilation.
  - `build_pyinstaller_command` / `build_nuitka_command` : Construction des commandes CLI.
- **Exemple d’appel** :
```python
self.compile_all()
```

### `worker.py`
- **Rôle** : Contient la classe principale de l’interface graphique (PyInstallerWorkspaceGUI). Gère les interactions utilisateur, l’activation/désactivation des contrôles, le drag & drop, etc.
- **Fonctions clés** :
  - `set_controls_enabled(self, enabled)` : Active/désactive les boutons et options.
  - `apply_language(self, lang)` : Applique la langue à l’interface.
  - `select_workspace`, `select_files_manually`, etc.
- **Exemple d’appel** :
```python
self.set_controls_enabled(False)
```

### `preferences.py`
- **Rôle** : Gère la sauvegarde, le chargement et l’application des préférences utilisateur (dossier de travail, options, langue, etc.).
- **Fonctions clés** :
  - `save_preferences(self)`
  - `load_preferences(self)`
  - `update_ui_state(self)`

### `dialogs.py`
- **Rôle** : Définit des boîtes de dialogue personnalisées (progression, messages d’erreur, etc.).
- **Exemple** :
```python
from .dialogs import ProgressDialog
progress = ProgressDialog("Titre", parent)
progress.set_message("En cours...")
progress.show()
```

### `dependency_analysis.py`
- **Rôle** : Analyse les imports des scripts Python, suggère et installe automatiquement les modules manquants.
- **Fonctions clés** :
  - `suggest_missing_dependencies(self)`
  - `_install_next_dependency(self)`

### `pyarmor_api.py`
- **Rôle** : Intègre la protection PyArmor pour l’obfuscation du code avant compilation.
- **Fonctions clés** :
  - `pre_compilation_obfuscation(self, workspace_dir)`

### `sys_dependency.py`
- **Rôle** : Vérifie et installe les dépendances système nécessaires (ex : gcc, p7zip pour Nuitka).
- **Fonctions clés** :
  - `install_gcc_and_p7zip(self)`

---

## Architecture et interactions
- Les modules utilitaires sont pensés pour être appelés depuis l’interface graphique (worker.py) ou d’autres modules.
- Les logs sont centralisés via `self.log.append()` pour un affichage unifié.
- Les préférences sont sauvegardées automatiquement après chaque modification importante.
- Les dialogues personnalisés sont utilisés pour informer l’utilisateur de la progression ou des erreurs.

## Conseils d’utilisation et d’extension
- **Ajout d’un nouvel utilitaire** : Crée un fichier dédié, documente-le avec une docstring, et ajoute un exemple d’utilisation ici.
- **Traduction** : Ajoute les nouveaux textes dans le dictionnaire de traduction de worker.py.
- **Gestion des erreurs** : Privilégie des messages clairs, en français, et propose des solutions à l’utilisateur.
- **Tests** : Place les tests unitaires dans un sous-dossier `tests/` ou dans un fichier test_utils.py.

## Exemples d’utilisation

### 1. Ajout d’un message d’erreur utilisateur
```python
try:
    # ... action risquée ...
except Exception as e:
    self.log.append(f"❌ Erreur : {e}")
    QMessageBox.critical(self, "Erreur", str(e))
```

### 2. Ajout d’une option personnalisée Nuitka
Dans l’interface, pour inclure un fichier de données :
```
--include-data-files=chemin/fichier.txt=chemin/destination
```

### 3. Utilisation d’une boîte de progression
```python
from .dialogs import ProgressDialog
progress = ProgressDialog("Traitement en cours", self)
progress.set_message("Veuillez patienter...")
progress.show()
```

### 4. Vérification des dépendances système
```python
from .sys_dependency import SysDependencyManager
sysdep = SysDependencyManager(parent_widget=self)
sysdep.install_gcc_and_p7zip()
```

## Bonnes pratiques
- **Centralise** les fonctions réutilisables ici pour éviter la duplication.
- **Documente** chaque fonction complexe avec une docstring.
- **Affiche** toujours des messages d’erreur clairs à l’utilisateur.
- **Teste** les utilitaires critiques.
- **Mets à jour** ce README à chaque ajout ou modification importante.

---

*Ce fichier est à compléter et à maintenir à jour pour faciliter la prise en main et la maintenance du projet.*
