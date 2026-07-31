# 📊 Macro Weather Dashboard V5.0

Dashboard macro-financier auto-mis à jour via **Claude AI + web_search**.
Hébergé gratuitement sur GitHub Pages · mis à jour les 1er et 15 de chaque mois.

---

## Setup — 5 étapes (~15 min)

### Étape 1 — Créer le repository GitHub

1. Connecte-toi sur [github.com](https://github.com)
2. Clique **New repository**
3. Nom : `macro-weather-dashboard` (ou ce que tu veux)
4. **Public** (obligatoire pour GitHub Pages gratuit)
5. Clique **Create repository**
6. Upload tous les fichiers de ce ZIP (glisser-déposer dans l'interface GitHub)

---

### Étape 2 — Ajouter la clé Anthropic

Dans ton repo GitHub :
`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

| Nom | Valeur |
|---|---|
| `ANTHROPIC_API_KEY` | Ta clé `sk-ant-api03-...` (disponible sur console.anthropic.com) |

---

### Étape 3 — Configurer l'envoi de mail (Gmail)

**a) Créer un mot de passe d'application Gmail**
1. Va sur [myaccount.google.com](https://myaccount.google.com)
2. `Sécurité` → `Vérification en 2 étapes` (doit être activée)
3. `Mots de passe des applications` → Créer → Nom : "Macro Dashboard"
4. Copie le mot de passe à 16 caractères généré

**b) Ajouter 3 secrets GitHub** (même endroit que l'étape 2) :

| Nom | Valeur |
|---|---|
| `MAIL_USERNAME` | Ton adresse Gmail (ex: `ton.email@gmail.com`) |
| `MAIL_PASSWORD` | Le mot de passe à 16 caractères (pas ton mot de passe Gmail normal) |
| `MAIL_TO` | L'adresse de destination (peut être la même) |

---

### Étape 4 — Activer GitHub Pages

Dans ton repo :
`Settings` → `Pages` → `Source` : **Deploy from a branch** → Branch : **main** → Folder : **/ (root)**

Ton URL sera :
```
https://TON-USERNAME.github.io/macro-weather-dashboard
```

Remplace `TON-USERNAME` par ton nom d'utilisateur GitHub.

⚠️ La page peut prendre 1-2 minutes à apparaître la première fois.

---

### Étape 5 — Lancer la première mise à jour

`Actions` → `📊 Mise à jour Macro Dashboard` → **Run workflow** → **Run workflow**

Le workflow va :
1. Appeler Claude AI + web_search pour récupérer les données actuelles
2. Générer `data.json` avec les vraies données macro du jour
3. Committer le fichier (le dashboard se met à jour automatiquement)
4. T'envoyer un email avec le lien

**Durée : ~30-60 secondes**

---

## Fonctionnement

```
┌─────────────────────────────────────────────────────┐
│  GitHub Actions (1er et 15 de chaque mois, 7h UTC)  │
│                                                     │
│  1. python scripts/fetch_data.py                    │
│     └─ Appelle Claude API + web_search              │
│     └─ Recherche PMI, CPI, TIPS, HY, Brent...      │
│     └─ Génère data.json structuré                   │
│                                                     │
│  2. git commit data.json                            │
│     └─ GitHub Pages sert le nouveau data.json       │
│     └─ index.html le charge au prochain refresh     │
│                                                     │
│  3. Envoie un email de notification                 │
└─────────────────────────────────────────────────────┘
```

---

## Forcer une mise à jour manuelle

`Actions` → `📊 Mise à jour Macro Dashboard` → `Run workflow`

---

## Structure des fichiers

```
macro-weather-dashboard/
├── index.html                    ← Dashboard (charge data.json)
├── data.json                     ← Données générées automatiquement
├── scripts/
│   └── fetch_data.py             ← Script Python (Claude API + web_search)
└── .github/
    └── workflows/
        └── update.yml            ← GitHub Actions (planning + email)
```

---

## Modifier le contenu manuellement

Tu peux éditer `data.json` directement sur GitHub pour corriger des données ou ajouter des commentaires. Le dashboard se met à jour instantanément (après ~1 min pour GitHub Pages).

---

## Changer la fréquence de mise à jour

Dans `.github/workflows/update.yml`, modifie la ligne :
```yaml
- cron: '0 7 1,15 * *'   # 1er et 15 du mois à 7h UTC
```

Exemples :
- Toutes les semaines (lundi 7h) : `0 7 * * 1`
- Tous les dimanches : `0 7 * * 0`
- Tous les jours : `0 7 * * *`

---

## Coût estimé

- **GitHub** : gratuit (repo public + Pages + Actions)
- **Claude API** : ~0.01-0.03 € par mise à jour (web_search + génération JSON)
- **Total mensuel** : < 0.10 € pour 2 mises à jour/mois

---

*Macro Weather Dashboard V5.0 — Propulsé par Claude Sonnet + Anthropic web_search*
