#!/usr/bin/env python3
"""
Macro Weather Dashboard V5.0 — Data Fetcher
Appelle Claude API + web_search pour récupérer les données macro actuelles
et génère data.json qui alimente le dashboard.
"""

import anthropic
import json
import datetime
import os
import sys
import re

# ═══════════════════════════════════════════════════════════════
#  PROMPT — Instructs Claude to research and return structured JSON
# ═══════════════════════════════════════════════════════════════
SYSTEM = """Tu es un analyste macro-financier expert.
Tu vas rechercher les données actuelles sur le web et retourner UNIQUEMENT un JSON valide.
Pas de texte avant, pas de texte après, pas de backticks markdown. Juste le JSON brut."""

PROMPT = """Recherche les données macro-financières les plus récentes et retourne ce JSON:

{
  "date": "DD Mois YYYY en français (ex: 15 Juillet 2026)",
  "blocs": [
    {"key":"croissance", "label":"Croissance",       "pct":20, "score":X.X, "trend":"↗/→/↘", "val":"PMI XX.X",         "sub":"S&P Global / BLS"},
    {"key":"inflation",  "label":"Inflation",         "pct":15, "score":X.X, "trend":"↗/→/↘", "val":"CPI X.X% YoY",    "sub":"BLS / FRED"},
    {"key":"tauxReels",  "label":"Taux Réels",        "pct":10, "score":X.X, "trend":"↗/→/↘", "val":"10Y TIPS X.X%",   "sub":"FRED"},
    {"key":"liquidite",  "label":"Liquidité",         "pct":15, "score":X.X, "trend":"↗/→/↘", "val":"M2 X.X% YoY",    "sub":"OECD / Fed / BCE"},
    {"key":"condFin",    "label":"Conditions Fin.",   "pct":10, "score":X.X, "trend":"↗/→/↘", "val":"NFCI X.XX",       "sub":"Chicago Fed"},
    {"key":"credit",     "label":"Crédit",            "pct":10, "score":X.X, "trend":"↗/→/↘", "val":"HY X.X%",         "sub":"ICE BofA"},
    {"key":"anticip",    "label":"Anticipations",     "pct":10, "score":X.X, "trend":"↗/→/↘", "val":"2Y X.X% / Curve", "sub":"FRED"},
    {"key":"energie",    "label":"Énergie / Géo",     "pct": 5, "score":X.X, "trend":"↗/→/↘", "val":"Brent $XX/bbl",   "sub":"ICE / GPR"},
    {"key":"largeur",    "label":"Largeur Marché",    "pct": 5, "score":X.X, "trend":"↗/→/↘", "val":"XX% > MM200",     "sub":"S&P / MSCI"}
  ],
  "quality": {
    "strength": X,
    "consensus": X,
    "inertie": X,
    "fatigue": X,
    "transitionRisk": X,
    "regimeAge": X
  },
  "favoris": [
    {"name":"Actif 1", "score":X.X, "note":"Raison courte"},
    {"name":"Actif 2", "score":X.X, "note":"Raison courte"},
    {"name":"Actif 3", "score":X.X, "note":"Raison courte"},
    {"name":"Actif 4", "score":X.X, "note":"Raison courte"},
    {"name":"Actif 5", "score":X.X, "note":"Raison courte"}
  ],
  "penalises": [
    {"name":"Actif 1", "score":X.X, "note":"Raison courte"},
    {"name":"Actif 2", "score":X.X, "note":"Raison courte"},
    {"name":"Actif 3", "score":X.X, "note":"Raison courte"}
  ],
  "donut": [
    {"label":"Catégorie 1", "pct":XX, "color":"#F59E0B"},
    {"label":"Catégorie 2", "pct":XX, "color":"#EF4444"},
    {"label":"Catégorie 3", "pct":XX, "color":"#60A5FA"},
    {"label":"Catégorie 4", "pct":XX, "color":"#22C55E"},
    {"label":"Catégorie 5", "pct":XX, "color":"#8B5CF6"},
    {"label":"Catégorie 6", "pct":XX, "color":"#94A3B8"}
  ],
  "inflChart": {
    "labels":  ["M-5","M-4","M-3","M-2","M-1","M actuel"],
    "cpi":         [X.X, X.X, X.X, X.X, X.X, X.X],
    "coreCpi":     [X.X, X.X, X.X, X.X, X.X, X.X],
    "expectations":[X.X, X.X, X.X, X.X, X.X, X.X]
  },
  "confirms":   ["Signal 1","Signal 2","Signal 3","Signal 4"],
  "contradicts":["Signal 1","Signal 2","Signal 3"],
  "risks":      ["Risque 1","Risque 2","Risque 3","Risque 4"],
  "calendar": [
    {"date":"DD Mois", "ev":"Événement macro important", "hi":true},
    {"date":"DD Mois", "ev":"Événement macro important", "hi":false},
    {"date":"DD Mois", "ev":"Événement macro important", "hi":true},
    {"date":"DD Mois", "ev":"Événement macro important", "hi":true},
    {"date":"DD Mois", "ev":"Événement macro important", "hi":false}
  ]
}

RÈGLES DE SCORING (−2 à +2):
─ Croissance  : PMI>53 → +1.5/+2  |  PMI 51-53 → +0.5/+1  |  PMI~50 → 0  |  PMI 48-50 → -0.5  |  PMI<48 → -1.5/-2
─ Inflation   : score NÉGATIF si inflation HAUTE (mauvais pour actifs). CPI>4% → -1.5/-2  |  CPI 3-4% → -1/-1.5  |  CPI~2.5% → 0  |  CPI<2% → +0.5
─ Taux réels  : TIPS>2.5% → -1.5  |  TIPS 1-2% → -0.5/-1  |  TIPS 0-1% → 0  |  TIPS<0 → +1/+2
─ Liquidité   : M2>4% → +1.5  |  M2 2-4% → +0.5/+1  |  M2~0% → 0  |  M2<0% → -1/-2
─ Cond. Fin.  : NFCI<-0.5 (très accommodant) → +1.5  |  NFCI~0 → 0  |  NFCI>0.3 (restrictif) → -1/-2
─ Crédit      : HY<300bp → +1  |  HY 300-450bp → 0/+0.5  |  HY 450-600bp → -0.5/-1  |  HY>600bp → -2
─ Anticipations: courbe pentue → +1  |  plate → 0  |  inversée → -0.5/-1  |  très inversée + spreads → -2
─ Énergie/Géo : Brent stable → 0  |  +10%YoY → -0.5  |  +15-20% → -1/-1.5  |  choc>25% → -2
─ Largeur     : >70% above MM200 → +1.5  |  55-70% → +0.5/+1  |  45-55% → 0  |  30-45% → -1  |  <30% → -2

Qualité (0-10):
─ strength: force du régime (10 = régime très clair)
─ consensus: % indicateurs concordants (10 = 100%)
─ inertie: persistance du régime (10 = très stable)
─ fatigue: signes d'essoufflement (10 = très fatigué)
─ transitionRisk: risque de bascule de régime (10 = très élevé)
─ regimeAge: nombre de mois depuis le début du régime actuel

Actifs favoris /10: 8-10 = très favorisé | 6-7 = favorisé. Colle avec le régime identifié.
Actifs pénalisés /10: 0-2 = très pénalisé | 3-4 = pénalisé.
Total donut = 100% exactement. Alloue selon le régime identifié.
inflChart: derniers mois réels en % (ex CPI 3.1, 3.2…). Labels = abréviations mois français.
Événements calendrier: prochains 4-6 événements macro importants (NFP, CPI, FOMC, BCE, PMI flash...).

Recherche maintenant les données actuelles et remplis le JSON."""


def extract_json(text: str) -> str:
    """Clean and extract JSON from Claude's response."""
    text = text.strip()
    # Remove markdown code fences
    text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n?```\s*$',          '', text, flags=re.MULTILINE)
    text = text.strip()
    # If there's surrounding text, find the JSON object
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        return match.group()
    return text


def fetch() -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)
    print("🔍 Recherche des données macro via Claude + web_search...")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": PROMPT}]
    )

    # Collect all text blocks (Claude may search multiple times before answering)
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text

    if not text.strip():
        raise ValueError("Empty response from Claude API")

    raw_json = extract_json(text)
    data = json.loads(raw_json)

    # Validate minimum structure
    required = ["date", "blocs", "quality", "favoris", "penalises"]
    for field in required:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    # Add server timestamp
    data["lastUpdate"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    return data


def compute_score(data: dict) -> float:
    return sum(b["score"] * (b["pct"] / 100) for b in data["blocs"])


if __name__ == "__main__":
    try:
        data = fetch()
        score = compute_score(data)

        # Save to data.json at repo root
        out_path = os.path.join(os.path.dirname(__file__), "..", "data.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ data.json mis à jour")
        print(f"   Date     : {data['date']}")
        print(f"   Score    : {score:+.2f}")
        print(f"   Blocs    : {len(data['blocs'])} blocs remplis")
        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON : {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur : {e}", file=sys.stderr)
        sys.exit(1)
