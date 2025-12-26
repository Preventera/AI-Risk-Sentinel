# 🚀 Guide de Démarrage Rapide - AI Risk Sentinel

## Prérequis

### Windows (VS Code)
```powershell
# 1. Python 3.11+
winget install Python.Python.3.11

# 2. Git
winget install Git.Git

# 3. Docker Desktop
winget install Docker.DockerDesktop

# 4. VS Code
winget install Microsoft.VisualStudioCode
```

### Extensions VS Code Recommandées
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Docker (ms-azuretools.vscode-docker)
- GitLens (eamodio.gitlens)
- Thunder Client (rangav.vscode-thunder-client)

---

## 🔧 Installation Locale (Windows)

### Étape 1: Cloner le Repository

```powershell
# Ouvrir PowerShell et naviguer vers votre dossier projets
cd C:\Users\Mario\Documents\PROJECTS_NEW

# Cloner depuis GitHub
git clone https://github.com/Preventera/AI-Risk-Sentinel.git
cd "AI Risk Sentinel"
```

### Étape 2: Créer l'Environnement Virtuel

```powershell
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Si erreur de politique d'exécution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Étape 3: Installer les Dépendances

```powershell
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer le projet en mode développement
pip install -e ".[dev]"
```

### Étape 4: Configurer l'Environnement

```powershell
# Copier le fichier d'exemple
Copy-Item .env.example .env

# Ouvrir dans VS Code pour éditer
code .env
```

**Variables essentielles à configurer:**
```env
# Hugging Face (obligatoire pour HF_Crawler)
HF_TOKEN=hf_votre_token_ici

# Anthropic Claude (optionnel, pour classification LLM)
ANTHROPIC_API_KEY=sk-ant-votre_cle_ici

# Base de données locale
POSTGRES_USER=ars_user
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_DB=ai_risk_sentinel
```

### Étape 5: Lancer les Services Docker

```powershell
# S'assurer que Docker Desktop est démarré

# Lancer PostgreSQL et Redis
docker-compose up -d db redis

# Vérifier que les services sont actifs
docker-compose ps
```

### Étape 6: Initialiser la Base de Données

```powershell
# Créer les tables
python scripts/init_db.py

# Charger les taxonomies MIT/DeepMind
python scripts/load_taxonomies.py
```

### Étape 7: Lancer l'API en Mode Développement

```powershell
# Démarrer le serveur FastAPI
uvicorn ai_risk_sentinel.api:app --reload --port 8000

# L'API sera disponible sur http://localhost:8000
# Documentation Swagger: http://localhost:8000/docs
```

---

## 🧪 Tester l'Installation

### Test Rapide Python

```python
# Ouvrir Python interactif
python

# Tester l'import
>>> from ai_risk_sentinel import GapDetector
>>> detector = GapDetector()
>>> report = detector.analyze()
>>> print(f"Blind Spot Index Global: {report.global_bsi}")
>>> print(f"Catégories à haut risque: {report.high_risk_categories}")
```

### Test API avec curl/Thunder Client

```bash
# Health check
curl http://localhost:8000/health

# Obtenir le Blind Spot Index
curl http://localhost:8000/api/v1/metrics/bsi
```

### Lancer les Tests Unitaires

```powershell
# Tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=src/ai_risk_sentinel --cov-report=html
```

---

## 📁 Structure du Projet dans VS Code

```
AI Risk Sentinel/
├── .venv/                    # Environnement virtuel (ignoré git)
├── .vscode/                  # Configuration VS Code
│   └── settings.json
├── src/
│   └── ai_risk_sentinel/
│       ├── __init__.py
│       ├── agents/           # Agents N1-N5
│       ├── api/              # FastAPI endpoints
│       ├── core/             # Logique métier
│       │   ├── gap_detector.py
│       │   └── compliance_checker.py
│       ├── models/           # Schémas Pydantic
│       └── utils/            # Utilitaires
├── tests/                    # Tests pytest
├── data/
│   ├── taxonomies/           # MIT, DeepMind taxonomies
│   └── samples/              # Données exemple
├── docs/                     # Documentation
├── frontend/                 # Dashboard React
├── scripts/                  # Scripts utilitaires
├── .env                      # Variables d'environnement (ignoré git)
├── .env.example              # Template environnement
├── docker-compose.yml        # Services Docker
├── pyproject.toml            # Configuration projet Python
└── README.md
```

---

## 🔄 Workflow Git Quotidien

### Créer une Branche Feature

```powershell
# Créer et basculer sur une nouvelle branche
git checkout -b feature/nom-de-la-feature

# Faire vos modifications...

# Ajouter les fichiers modifiés
git add .

# Commit avec message conventionnel
git commit -m "feat: description de la feature"

# Pousser vers GitHub
git push origin feature/nom-de-la-feature
```

### Conventions de Commit

| Préfixe | Usage |
|---------|-------|
| `feat:` | Nouvelle fonctionnalité |
| `fix:` | Correction de bug |
| `docs:` | Documentation |
| `refactor:` | Refactoring sans changement fonctionnel |
| `test:` | Ajout/modification de tests |
| `chore:` | Maintenance, dépendances |

---

## 🐛 Dépannage

### Erreur: "Module not found"
```powershell
# S'assurer que l'environnement est activé
.\.venv\Scripts\Activate.ps1

# Réinstaller en mode développement
pip install -e ".[dev]"
```

### Erreur: "Connection refused" (PostgreSQL)
```powershell
# Vérifier que Docker est démarré
docker-compose ps

# Redémarrer les services
docker-compose down
docker-compose up -d db redis
```

### Erreur: "Permission denied" (PowerShell)
```powershell
# Autoriser l'exécution de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Réinitialiser Complètement

```powershell
# Supprimer l'environnement virtuel
Remove-Item -Recurse -Force .venv

# Supprimer les volumes Docker
docker-compose down -v

# Recommencer depuis l'étape 2
```

---

## 📞 Support

- **Documentation**: [docs/](./docs/)
- **Issues GitHub**: [github.com/Preventera/AI-Risk-Sentinel/issues](https://github.com/Preventera/AI-Risk-Sentinel/issues)
- **Équipe**: team@genaisafety.com

---

*GenAISafety • Preventera • SquadrAI*
