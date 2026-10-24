# 🌍 GeoCapital — « Connaître le passé pour anticiper le futur »

Carte du monde interactive à esprit financier (Streamlit, en français).
Clique sur un pays → son histoire en frise, ses institutions, ses relations,
ses indicateurs expliqués, son **Score GeoCapital /100**, son **rendement
exigé Ke (Damodaran)** et un verdict : Investir / Prudence / Attendre / Éviter.

## Les 10 pays du MVP
USA, France, Japon, Chine, Arabie Saoudite, Émirats Arabes Unis, Maroc,
Afrique du Sud, Liban, Syrie — du plus sûr au plus fragile.

## Lancer en local
```bash
pip install -r requirements.txt
streamlit run app.py
```
L'app s'ouvre sur http://localhost:8501 — elle fonctionne **sans clé API**.

## Modules (menu de gauche)
1. **Carte Vivante** : choroplèthe mondiale colorée par score / Ke / croissance + classement
2. **Fiche Pays** : frise historique (6 dates), institutions, relations, tableau de bord
   financier à feux tricolores, détail du score, explication du verdict
3. **Comparateur** : 2-3 pays, radar des 6 critères, 5 duels pédagogiques prédéfinis
4. **Décodeur d'Actualité** : 6 événements décryptés en chaîne causale + choc historique comparable
5. **Portefeuille Mondial** : 100 000 fictifs, rendement espéré (Ke pondérés),
   risque, indice de concentration HHI et diversification
6. **Carte Mentale & Quiz** : progression des pays explorés + 3 questions par pays

## Méthode de calcul
- **Score /100** : Croissance 20 + Stabilité macro (inflation 10 + dette 10)
  + Risque souverain (notation 10 + CDS 10) + Stabilité politique/historique 15
  + Marché financier 15 + Facilité d'investir 10.
- **Profil** : Prudent double le poids du risque souverain et de la stabilité ;
  Audacieux double croissance et marché (moyenne pondérée renormalisée sur 100).
- **Ke (Damodaran)** : `Ke = Rf + β × ERP totale du pays`. Le CDS n'est PAS
  rajouté (l'ERP totale contient déjà la prime pays → pas de double comptage).
  Rf (défaut 4 %) et β (défaut 1) sont réglables dans la barre latérale.
- **Donnée manquante = risque** : Liban et Syrie n'ont pas de CDS exploitable :
  le critère vaut 0 et un drapeau s'affiche. Aucun chiffre n'est inventé.

## IA (optionnelle)
Sans clé : textes de repli générés depuis les données.
Avec clé : crée `.streamlit/secrets.toml` (voir `secrets.toml.example`)
avec la clé API du professeur → les boutons « Expliquer / Décrypter »
appellent Claude Haiku 5.5, avec interdiction d'inventer des chiffres.
**Ne pousse jamais `secrets.toml` sur GitHub** (il est dans `.gitignore`).

## Déploiement
1. Crée un repo GitHub **public** nommé `geocapital`, pousse ces fichiers.
2. Sur Streamlit Community Cloud (connexion avec GitHub) : New app →
   repo `geocapital`, branche `main`, fichier principal `app.py` → Deploy.

## Limites
Données de **démonstration** (ordres de grandeur 2024, Maroc : ERP 7,67 % et
CDS 151 bps du dataset Damodaran du cours) — à vérifier et sourcer (Banque
mondiale, FMI, Damodaran Online) avant toute présentation officielle.
Outil pédagogique, pas un conseil d'investissement.
