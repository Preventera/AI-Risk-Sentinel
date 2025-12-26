# 🛡️ AI Risk Sentinel

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![AgenticX5](https://img.shields.io/badge/Architecture-AgenticX5-purple.svg)](https://github.com/Preventera)

**Système Multi-Agents pour l'Analyse et la Correction Proactive des Angles Morts dans la Documentation des Risques IA**

> 🎯 Basé sur le [AI Model Risk Catalog](https://social-dynamics.net/ai-risks/catalog) (Rao et al., AAAI 2025) et l'architecture AgenticX5

---

## 📋 Table des Matières

- [Problème](#-problème)
- [Solution](#-solution)
- [Architecture](#-architecture-agenticx5)
- [Installation](#-installation)
- [Démarrage Rapide](#-démarrage-rapide)
- [API Reference](#-api-reference)
- [Roadmap](#-roadmap)
- [Contribution](#-contribution)
- [Licence](#-licence)

---

## 🚨 Problème

L'analyse de **460 000 model cards** Hugging Face révèle des écarts critiques entre les risques documentés par les développeurs et les incidents réels:

| Catégorie de Risque | Documenté | Incidents Réels | Écart |
|---------------------|-----------|-----------------|-------|
| Acteurs malveillants & mésusage | 4% | **22.4%** | -18 pts |
| Désinformation | 10.2% | 12.9% | -3 pts |
| Socioéconomique & environnemental | 0.5% | 3.6% | -3 pts |

**85% des model cards n'ont pas de section risques substantielle.**

Les risques liés à l'**interaction humaine** et au **social engineering** sont massivement sous-documentés, créant des angles morts dangereux pour les déploiements IA en environnement SST (Santé-Sécurité au Travail).

---

## 💡 Solution

**AI Risk Sentinel** est un système multi-agents qui:

1. **Collecte** les données de 3 sources complémentaires (Hugging Face, MIT Risk Repository, AI Incident Database)
2. **Normalise** les risques selon les taxonomies MIT (7 catégories) et DeepMind (6 catégories + 3 couches)
3. **Analyse** les écarts via le **Blind Spot Index** (ratio risques non-documentés / incidents réels)
4. **Recommande** des corrections avec evidence packs pour audit
5. **Orchestre** des agents de correction proactive avec **validation humaine obligatoire**

---

## 🏗️ Architecture AgenticX5

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI RISK SENTINEL                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  N5 - ORCHESTRATION                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐│
│  │ RiskDoc      │ │ Incident     │ │ Compliance   │ │ Blind Spot  ││
│  │ Filler       │ │ Correlator   │ │ Checker      │ │ Alert       ││
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬──────┘│
│         │                │                │                │       │
│  ───────┴────────────────┴────────────────┴────────────────┴────── │
│                                                                     │
│  N4 - RECOMMANDATION                                                │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  Checklist Generator │ Compliance Reporter │ Action Prioritizer ││
│  └────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  N3 - ANALYSE                                                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────────┐ │
│  │ Gap         │ │ Risk        │ │ SST Impact  │ │ Mitigation    │ │
│  │ Detector    │ │ Propagation │ │ Scorer      │ │ Matcher       │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────────┘ │
│                                                                     │
│  N2 - NORMALISATION                                                 │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  MIT Classifier │ DeepMind Mapper │ Deduplicator │ SST Mapper  ││
│  └────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  N1 - COLLECTE                                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                   │
│  │ HF_Crawler  │ │ Incident    │ │ Regulatory  │                   │
│  │             │ │ Monitor     │ │ Tracker     │                   │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘                   │
│         │               │               │                          │
└─────────┼───────────────┼───────────────┼──────────────────────────┘
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │ Hugging   │   │ AI        │   │ EU AI Act │
    │ Face Hub  │   │ Incident  │   │ NIST RMF  │
    │           │   │ Database  │   │ ISO 45001 │
    └───────────┘   └───────────┘   └───────────┘
```

### Niveaux AgenticX5

| Niveau | Rôle | Composants Clés |
|--------|------|-----------------|
| **N1** | Collecte & Ingestion | HF_Crawler, Incident_Monitor, Regulatory_Tracker |
| **N2** | Normalisation | Classifieur MIT/DeepMind, Déduplicateur, Mapper SST |
| **N3** | Analyse & Intelligence | Gap_Detector, Risk_Propagation, SST_Impact_Scorer |
| **N4** | Recommandations | Checklist Generator, Compliance Reporter, Prioritizer |
| **N5** | Orchestration | RiskDoc_Filler, Incident_Correlator, Compliance_Checker |

---

## 🚀 Installation

### Prérequis

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (ou via Docker)
- Node.js 18+ (pour le frontend)

### Installation Locale

```bash
# Cloner le repository
git clone https://github.com/Preventera/AI-Risk-Sentinel.git
cd AI-Risk-Sentinel

# Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -e ".[dev]"

# Copier et configurer l'environnement
cp .env.example .env
# Éditer .env avec vos clés API

# Lancer les services (PostgreSQL, Redis)
docker-compose up -d db redis

# Initialiser la base de données
python scripts/init_db.py

# Charger les taxonomies
python scripts/load_taxonomies.py
```

### Installation Docker (Recommandé)

```bash
# Cloner et configurer
git clone https://github.com/Preventera/AI-Risk-Sentinel.git
cd AI-Risk-Sentinel
cp .env.example .env

# Lancer tous les services
docker-compose up -d

# L'API sera disponible sur http://localhost:8000
# Le dashboard sur http://localhost:3000
```

---

## ⚡ Démarrage Rapide

### 1. Calculer le Blind Spot Index

```python
from ai_risk_sentinel import GapDetector

detector = GapDetector()

# Analyser un type de modèle spécifique
report = detector.analyze(model_type="vision")
print(f"Blind Spot Index: {report.blind_spot_index}")
print(f"Catégories à risque: {report.high_risk_categories}")
```

### 2. Crawler des Model Cards

```python
from ai_risk_sentinel.agents import HFCrawler

crawler = HFCrawler()

# Extraire les 100 derniers models avec sections risques
models = crawler.fetch_recent(limit=100, with_risks=True)
print(f"Models avec risques documentés: {len(models)}")
```

### 3. Générer un Rapport de Conformité

```python
from ai_risk_sentinel import ComplianceChecker

checker = ComplianceChecker()

# Analyser un modèle spécifique
report = checker.check_model(
    model_id="meta-llama/Llama-3.1-8B",
    frameworks=["EU_AI_ACT", "NIST_AI_RMF"]
)
report.export_evidence_pack("./evidence/")
```

### 4. API REST

```bash
# Lancer l'API
uvicorn ai_risk_sentinel.api:app --reload

# Endpoints principaux
GET  /api/v1/risks                    # Liste des risques
GET  /api/v1/risks/{risk_id}          # Détail d'un risque
GET  /api/v1/models/{model_id}/gaps   # Analyse des angles morts
POST /api/v1/models/{model_id}/check  # Vérification conformité
GET  /api/v1/metrics/blind-spot-index # KPIs globaux
```

---

## 📊 API Reference

### Endpoints Principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/v1/risks` | Liste paginée des risques catalogués |
| `GET` | `/api/v1/risks/{id}` | Détail d'un risque avec taxonomies |
| `GET` | `/api/v1/incidents` | Flux des incidents récents |
| `POST` | `/api/v1/analyze/model` | Analyse complète d'un modèle |
| `GET` | `/api/v1/metrics/bsi` | Blind Spot Index par catégorie |
| `POST` | `/api/v1/compliance/check` | Vérification conformité |
| `GET` | `/api/v1/agents/status` | Statut des agents N1-N5 |

### Exemple de Réponse

```json
{
  "blind_spot_index": {
    "global": 0.18,
    "by_category": {
      "malicious_actors_misuse": 0.42,
      "misinformation": 0.21,
      "discrimination_toxicity": 0.08
    }
  },
  "recommendations": [
    {
      "priority": "HIGH",
      "category": "malicious_actors_misuse",
      "action": "Document deepfake generation risks",
      "evidence_required": true
    }
  ]
}
```

---

## 🗺️ Roadmap

### MVP (3 mois)
- [x] Structure projet et CI/CD
- [ ] HF_Crawler agent
- [ ] Classification MIT automatique
- [ ] Dashboard Blind Spot Index
- [ ] API REST v1

### V2 (6 mois)
- [ ] Agents N5 opérationnels
- [ ] Compliance Checker EU AI Act
- [ ] Intégration LEANN RAG
- [ ] Alertes temps réel

### V3 (12 mois)
- [ ] Prédiction risques émergents
- [ ] Intégration SquadrAI complète
- [ ] Audit trail certifiable
- [ ] Certification ISO 27001

---

## 🤝 Contribution

Les contributions sont les bienvenues! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

```bash
# Fork le repo
# Créer une branche feature
git checkout -b feature/amazing-feature

# Commit avec conventional commits
git commit -m "feat: add amazing feature"

# Push et créer une PR
git push origin feature/amazing-feature
```

### Standards de Code

- **Python**: Black, isort, ruff
- **TypeScript**: ESLint, Prettier
- **Commits**: Conventional Commits
- **Tests**: pytest (coverage > 80%)

---

## 📜 Licence

MIT License - voir [LICENSE](LICENSE) pour les détails.

---

## 🏢 Organisation

<p align="center">
  <strong>GenAISafety • Preventera • SquadrAI</strong>
</p>

<p align="center">
  <em>Advancing AI Safety in Occupational Health & Safety</em>
</p>

---

## 📚 Références

- Rao, P. S. B., et al. (2025). "The AI Model Risk Catalog: What Developers and Researchers Miss About Real-World AI Harms." *AAAI 2025*.
- Slattery, P., et al. (2024). "The AI Risk Repository." MIT.
- McGregor, S. (2021). "AI Incident Database."
- Weidinger, L., et al. (2022). "Taxonomy of Risks posed by Language Models." *DeepMind*.

---

<p align="center">
  Made with ❤️ for safer AI deployments
</p>
