# -*- coding: utf-8 -*-
"""
GeoCapital — « Connaître le passé pour anticiper le futur »
Application Streamlit : carte du monde interactive à esprit financier.
10 pays : histoire, institutions, indicateurs, Score GeoCapital (/100),
rendement exigé Ke (méthode Damodaran), verdict d'investissement,
décodeur d'actualité, portefeuille fictif, quiz / carte mentale.

Lancement :  streamlit run app.py
Les données chiffrées sont des données de DÉMONSTRATION (ordres de grandeur
2024) : à vérifier et sourcer avant tout usage réel.
L'IA (Claude Haiku) est OPTIONNELLE : sans clé API, l'app utilise des
textes de repli générés à partir des données.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="GeoCapital — Connaître le passé pour anticiper le futur",
                   page_icon="🌍", layout="wide")

st.markdown("""
<style>
.main-title {font-size:2.4rem; font-weight:800; color:#0b5345;}
.slogan {font-size:1.2rem; font-style:italic; color:#b7950b;}
.verdict-box {padding:14px; border-radius:12px; font-size:1.1rem; font-weight:700; text-align:center;}
.small-note {font-size:0.8rem; color:#666;}
.chain-step {background:#eafaf1; border:1px solid #0b5345; border-radius:10px; padding:10px; min-height:110px;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 1. DONNÉES — 10 PAYS (démonstration, ordres de grandeur 2024)
# cds_bps = None  -> donnée manquante = signal de risque (note 0 + drapeau)
# erp = prime de risque totale type Damodaran (%), contient déjà la prime pays
# ============================================================
COUNTRIES = [
 dict(iso="USA", nom="États-Unis", region="Amérique du Nord", categorie="Développé",
      devise="Dollar (USD)", banque_centrale="Réserve fédérale (Fed)",
      regime="République fédérale présidentielle",
      institutions="Démocratie fédérale, banque centrale indépendante, marché financier le plus profond du monde (Wall Street).",
      croissance=2.8, inflation=2.9, dette=121, taux=4.50, chomage=4.1, reserves="~8 mois (or + devises, émetteur du dollar)",
      notation="AA+", cds=35, erp=4.33, bourse="S&P 500 / Nasdaq", devise_5ans="+8 % (dollar fort)",
      stabilite=9, liquidite=10, bourse_dev=5, facilite=10,
      secteurs=["Technologie / IA", "Finance", "Santé", "Énergie"],
      allies=["Union européenne", "Japon", "Royaume-Uni"], rivaux=["Chine (rivalité technologique et commerciale)", "Russie"],
      dependances=["Consommation intérieure (70 % du PIB)", "Dette publique financée par le monde entier"]),
 dict(iso="FRA", nom="France", region="Europe", categorie="Développé",
      devise="Euro (EUR)", banque_centrale="Banque de France / BCE",
      regime="République semi-présidentielle, membre de l'Union européenne et de la zone euro",
      institutions="État centralisé, protection sociale élevée, dette publique importante mais marché obligataire profond (OAT).",
      croissance=1.1, inflation=2.0, dette=113, taux=3.00, chomage=7.3, reserves="Zone euro (BCE)",
      notation="AA-", cds=40, erp=5.20, bourse="CAC 40 (Euronext Paris)", devise_5ans="Euro : -5 % vs USD",
      stabilite=7, liquidite=9, bourse_dev=5, facilite=9,
      secteurs=["Luxe", "Aéronautique", "Énergie / nucléaire", "Banques"],
      allies=["Allemagne et Union européenne", "USA (OTAN)"], rivaux=["Tensions commerciales ponctuelles avec les USA"],
      dependances=["Dette publique > 110 % du PIB", "Énergie importée"]),
 dict(iso="JPN", nom="Japon", region="Asie", categorie="Développé",
      devise="Yen (JPY)", banque_centrale="Banque du Japon (BoJ)",
      regime="Monarchie constitutionnelle, démocratie parlementaire",
      institutions="État très stable, dette publique la plus élevée du monde développé mais détenue par les Japonais eux-mêmes et la BoJ.",
      croissance=0.1, inflation=2.5, dette=255, taux=0.25, chomage=2.5, reserves="Parmi les plus élevées du monde (~1 200 Mds USD)",
      notation="A+", cds=25, erp=5.10, bourse="Nikkei 225", devise_5ans="Yen : -30 % vs USD (monnaie devenue bon marché)",
      stabilite=9, liquidite=9, bourse_dev=5, facilite=9,
      secteurs=["Automobile", "Robotique / électronique", "Finance"],
      allies=["USA (alliance militaire)"], rivaux=["Chine (rivalité régionale)"],
      dependances=["Vieillissement de la population", "Importations d'énergie quasi totales"]),
 dict(iso="CHN", nom="Chine", region="Asie", categorie="Superpuissance émergente",
      devise="Yuan renminbi (CNY)", banque_centrale="Banque populaire de Chine (PBoC)",
      regime="République à parti unique (Parti communiste chinois)",
      institutions="Capitalisme d'État planifié : l'État contrôle les grandes banques, le taux de change et les flux de capitaux.",
      croissance=5.0, inflation=0.2, dette=60, taux=3.10, chomage=5.1, reserves="Les plus élevées du monde (~3 200 Mds USD)",
      notation="A+", cds=60, erp=5.20, bourse="Shanghai Composite / Hong Kong", devise_5ans="Yuan : -12 % vs USD (géré par la PBoC)",
      stabilite=7, liquidite=7, bourse_dev=4, facilite=5,
      secteurs=["Industrie / véhicules électriques", "Technologie", "Énergies renouvelables"],
      allies=["Russie (partenariat)", "Pays des BRICS"], rivaux=["USA (guerre commerciale et technologique)", "Taïwan (tension majeure)"],
      dependances=["Immobilier en crise depuis 2021", "Exportations vers les USA et l'Europe"]),
 dict(iso="SAU", nom="Arabie Saoudite", region="Moyen-Orient / Golfe", categorie="Golfe",
      devise="Riyal (SAR, arrimé au dollar)", banque_centrale="SAMA (Banque centrale saoudienne)",
      regime="Monarchie absolue",
      institutions="État rentier du pétrole en pleine diversification (Vision 2030) : fonds souverain PIF parmi les plus grands du monde.",
      croissance=1.3, inflation=1.7, dette=29, taux=5.50, chomage=7.1, reserves="Élevées (~400 Mds USD) + fonds PIF",
      notation="A+", cds=65, erp=5.00, bourse="Tadawul (la plus grande bourse arabe)", devise_5ans="Stable (peg au dollar)",
      stabilite=7, liquidite=7, bourse_dev=4, facilite=6,
      secteurs=["Pétrole / Aramco", "Tourisme et méga-projets", "Finance islamique"],
      allies=["Émirats et pays du Golfe", "USA (partenaire sécuritaire)"], rivaux=["Iran (rivalité régionale, en détente récente)"],
      dependances=["Recettes encore dominées par le pétrole", "Prix du baril décidé à l'international"]),
 dict(iso="ARE", nom="Émirats Arabes Unis", region="Moyen-Orient / Golfe", categorie="Golfe",
      devise="Dirham émirien (AED, arrimé au dollar)", banque_centrale="Banque centrale des Émirats",
      regime="Fédération de 7 émirats (Abou Dhabi, Dubaï...)",
      institutions="Modèle de diversification le plus avancé du Golfe : hub financier (DIFC), commercial, logistique et technologique mondial.",
      croissance=4.0, inflation=1.7, dette=32, taux=4.40, chomage=2.7, reserves="Élevées + fonds souverains (ADIA, Mubadala)",
      notation="AA-", cds=55, erp=4.70, bourse="DFM (Dubaï) / ADX (Abou Dhabi)", devise_5ans="Stable (peg au dollar)",
      stabilite=8, liquidite=8, bourse_dev=4, facilite=8,
      secteurs=["Finance / Fintech", "Immobilier", "Logistique et commerce", "Tourisme"],
      allies=["Arabie Saoudite", "USA", "Inde"], rivaux=["Concurrence régionale avec le Qatar et l'Arabie Saoudite"],
      dependances=["Main-d'œuvre étrangère (~90 % de la population)", "Réexportations et flux mondiaux"]),
 dict(iso="MAR", nom="Maroc", region="Afrique", categorie="Émergent intermédiaire",
      devise="Dirham marocain (MAD)", banque_centrale="Bank Al-Maghrib",
      regime="Monarchie constitutionnelle",
      institutions="Économie émergente diversifiée (automobile, aéronautique, phosphates, tourisme), change administré en voie d'assouplissement graduel.",
      croissance=3.2, inflation=0.9, dette=69, taux=2.75, chomage=13.3, reserves="~5 mois d'importations",
      notation="BB+", cds=151, erp=7.67, bourse="MASI (Casablanca)", devise_5ans="Dirham : bande de fluctuation élargie progressivement",
      stabilite=8, liquidite=5, bourse_dev=3, facilite=6,
      secteurs=["Automobile", "Phosphates (OCP)", "Aéronautique", "Tourisme / énergies renouvelables"],
      allies=["Union européenne (1er partenaire)", "USA", "Pays du Golfe (investisseurs)"], rivaux=["Tension régionale avec l'Algérie (frontière fermée)"],
      dependances=["Pluviométrie / agriculture et stress hydrique", "Énergie importée (~90 %)"]),
 dict(iso="ZAF", nom="Afrique du Sud", region="Afrique", categorie="Émergent (BRICS)",
      devise="Rand (ZAR)", banque_centrale="SARB (Banque de réserve sud-africaine)",
      regime="République parlementaire, membre des BRICS",
      institutions="Marché financier le plus développé d'Afrique et banque centrale crédible, mais crise électrique (délestages) et chômage record.",
      croissance=0.6, inflation=4.4, dette=75, taux=7.75, chomage=32.0, reserves="~4 mois d'importations",
      notation="BB-", cds=240, erp=8.50, bourse="JSE (Johannesburg, 1ère d'Afrique)", devise_5ans="Rand : -25 % vs USD (très volatile)",
      stabilite=5, liquidite=7, bourse_dev=4, facilite=6,
      secteurs=["Mines (or, platine)", "Banques", "Télécoms"],
      allies=["BRICS (Chine, Inde...)", "Union européenne et USA (commerce)"], rivaux=["—"],
      dependances=["Électricité (Eskom) et logistique ferroviaire/portuaire", "Prix des matières premières"]),
 dict(iso="LBN", nom="Liban", region="Moyen-Orient", categorie="Fragile",
      devise="Livre libanaise (LBP)", banque_centrale="Banque du Liban (BDL)",
      regime="République parlementaire confessionnelle (répartition par communauté)",
      institutions="Ancien hub bancaire régional effondré depuis 2019 : défaut souverain (2020), monnaie dévaluée de plus de 95 %, dépôts bancaires bloqués.",
      croissance=-0.7, inflation=45.0, dette=140, taux=0.0, chomage=30.0, reserves="Très faibles, en partie illiquides",
      notation="D (défaut)", cds=None, erp=18.0, bourse="Bourse de Beyrouth (très peu liquide)", devise_5ans="Effondrement : -98 % vs USD (marché parallèle)",
      stabilite=2, liquidite=1, bourse_dev=1, facilite=1,
      secteurs=["Services et diaspora (transferts)", "Tourisme (avant la crise)", "Agroalimentaire"],
      allies=["Pays du Golfe (soutien historique, refroidi)", "France (lien historique)"], rivaux=["Israël (conflit frontalier récurrent)"],
      dependances=["Transferts de la diaspora (pilier de l'économie)", "Importations de carburant et de blé"]),
 dict(iso="SYR", nom="Syrie", region="Moyen-Orient", categorie="Fragile",
      devise="Livre syrienne (SYP)", banque_centrale="Banque centrale de Syrie",
      regime="En transition politique depuis la chute du régime Assad (décembre 2024)",
      institutions="Économie détruite par 13 ans de guerre civile et de sanctions : infrastructures, monnaie et système bancaire à reconstruire.",
      croissance=-1.5, inflation=90.0, dette=0, taux=0.0, chomage=55.0, reserves="Quasi nulles / non publiées",
      notation="Non noté", cds=None, erp=25.0, bourse="Bourse de Damas (marginale)", devise_5ans="Effondrement continu de la livre",
      stabilite=1, liquidite=1, bourse_dev=0, facilite=0,
      secteurs=["Reconstruction (potentiel futur)", "Agriculture", "Pétrole (champs de l'Est)"],
      allies=["Pays arabes (normalisation en cours)", "Turquie (influence au nord)"], rivaux=["Sanctions occidentales (en voie d'allègement partiel)"],
      dependances=["Aide internationale et levée des sanctions", "Retour des réfugiés et des capitaux de la diaspora"]),
]

HISTORY = {
 "USA": [(1776,"Indépendance","Naissance des États-Unis : la future première économie mondiale part d'une république agricole."),
         (1929,"Krach et Grande Dépression","La crise bancaire américaine devient mondiale : naissance de la régulation financière moderne (SEC)."),
         (1944,"Bretton Woods","Le dollar devient la monnaie du monde : c'est encore le socle du système financier actuel."),
         (1971,"Fin de l'étalon-or","Le dollar flotte : début de l'ère des changes flottants et des crises monétaires modernes."),
         (2008,"Crise des subprimes","La crise financière partie des USA secoue la planète : les banques centrales deviennent des acteurs majeurs."),
         (2020,"Ère de la tech et de l'IA","Les géants technologiques américains dominent la capitalisation mondiale.")],
 "FRA": [(1789,"Révolution française","L'État moderne français se construit : centralisation qui marque encore l'économie."),
         (1957,"Traité de Rome","La France co-fonde l'Europe : son destin économique devient européen."),
         (1958,"Ve République","Stabilité politique retrouvée sous de Gaulle, grands programmes industriels et nucléaires."),
         (1999,"Naissance de l'euro","La France abandonne le franc : sa politique monétaire est désormais celle de la BCE."),
         (2008,"Crise financière puis crise des dettes","La dette publique française dépasse durablement 100 % du PIB dans les années 2010-2020."),
         (2020,"Plan de relance et réindustrialisation","L'État investit massivement (France 2030) tout en consolidant ses finances publiques.")],
 "JPN": [(1868,"Restauration Meiji","Le Japon se modernise à marche forcée et devient la première puissance industrielle d'Asie."),
         (1945,"Défaite et reconstruction","Détruit, le Japon se reconstruit avec l'aide américaine : le 'miracle japonais' commence."),
         (1973,"Choc pétrolier surmonté","Le Japon devient le modèle mondial d'efficacité industrielle (Toyota...)."),
         (1990,"Éclatement de la bulle","Bourse et immobilier s'effondrent : début des 'décennies perdues' et de la déflation."),
         (2013,"Abenomics","Relance monétaire massive : la BoJ rachète la dette de l'État et maintient des taux négatifs."),
         (2024,"Fin des taux négatifs","La BoJ relève ses taux pour la première fois en 17 ans : tournant historique.")],
 "CHN": [(1949,"Fondation de la RPC","Mao fonde la République populaire : économie planifiée, fermée au monde."),
         (1978,"Réforme et ouverture","Deng Xiaoping lance le capitalisme d'État : zones économiques spéciales, le décollage commence."),
         (2001,"Entrée à l'OMC","La Chine devient 'l'usine du monde' : exportations et réserves de change explosent."),
         (2010,"2e économie mondiale","La Chine dépasse le Japon : le centre de gravité économique bascule vers l'Asie."),
         (2021,"Crise de l'immobilier","La chute d'Evergrande révèle la fragilité du modèle : dette locale et immobilier pèsent sur la croissance."),
         (2023,"Rivalité technologique avec les USA","Restrictions américaines sur les semi-conducteurs : la géopolitique entre dans la finance.")],
 "SAU": [(1932,"Unification du royaume","Ibn Saoud unifie l'Arabie : un État, bientôt assis sur un océan de pétrole."),
         (1938,"Découverte du pétrole","Le pétrole transforme un pays désertique en puissance énergétique mondiale."),
         (1973,"Premier choc pétrolier","L'embargo de l'OPEP multiplie les prix : l'Arabie devient un acteur financier mondial."),
         (2016,"Vision 2030","Plan de diversification post-pétrole : tourisme, tech, sport, méga-projets (NEOM)."),
         (2019,"Introduction d'Aramco","La plus grande IPO de l'histoire à l'époque : le royaume ouvre son capital au monde."),
         (2023,"Détente avec l'Iran","Accord sous médiation chinoise : la stabilité régionale devient un argument d'investissement.")],
 "ARE": [(1971,"Création de la fédération","7 émirats s'unissent : les revenus du pétrole financent les infrastructures."),
         (1985,"Dubai parie sur le commerce","Port de Jebel Ali et zones franches : Dubaï se rêve en hub mondial, pas en émirat pétrolier."),
         (2004,"Centre financier DIFC","Dubaï crée une place financière de droit anglais : les banques mondiales s'installent."),
         (2009,"Crise de la dette de Dubaï","Le sauvetage par Abou Dhabi rappelle que la fédération est un filet de sécurité."),
         (2020,"Accords d'Abraham et Expo","Normalisation avec Israël et vitrine mondiale : ouverture économique maximale."),
         (2023,"COP28 et hub IA/crypto","Les Émirats se positionnent sur la finance verte, l'IA et les actifs numériques.")],
 "MAR": [(1956,"Indépendance","Le Maroc moderne se construit : dirham, banque centrale, grands barrages et phosphates."),
         (1983,"Ajustement structurel","Crise de la dette : libéralisation et ouverture qui préparent l'économie actuelle."),
         (1999,"Règne de Mohammed VI","Grands chantiers : port Tanger Med, autoroutes, solaire, industrie automobile."),
         (2011,"Nouvelle Constitution","Stabilité politique renforcée après le Printemps arabe, atout majeur face aux voisins."),
         (2018,"Flexibilité du dirham (étape 1)","Élargissement graduel de la bande de fluctuation : réforme monétaire prudente et progressive."),
         (2023,"Coupe du Monde 2030 annoncée","Co-organisation avec l'Espagne et le Portugal : vague d'investissements d'infrastructures.")],
 "ZAF": [(1948,"Début de l'apartheid","L'exclusion raciale institutionnalisée isole progressivement le pays des marchés mondiaux."),
         (1994,"Fin de l'apartheid, Mandela président","Réintégration mondiale : euphorie des investisseurs, le rand et la Bourse de Johannesburg décollent."),
         (2010,"Coupe du Monde et BRICS","L'Afrique du Sud rejoint les BRICS : symbole de l'Afrique émergente."),
         (2018,"Départ de Zuma","Après des années de corruption d'État, le pays tente de restaurer sa crédibilité budgétaire."),
         (2023,"Crise électrique aiguë","Les délestages (load-shedding) coûtent plusieurs points de croissance : le risque pays bondit."),
         (2024,"Gouvernement d'union nationale","L'ANC perd la majorité absolue : coalition inédite, mieux accueillie par les marchés.")],
 "LBN": [(1943,"Indépendance","Le Liban devient la place bancaire et commerciale du Moyen-Orient : la 'Suisse du Levant'."),
         (1975,"Début de la guerre civile","15 ans de guerre détruisent le pays et sa place financière."),
         (1993,"Reconstruction et ancrage au dollar","La livre est arrimée au dollar (1 507 LBP) : la stabilité monétaire repose sur les dépôts et la dette."),
         (2005,"Assassinat de Rafic Hariri","Le choc politique rouvre l'instabilité chronique des institutions confessionnelles."),
         (2019,"Effondrement financier","Crise de liquidités : les banques bloquent les dépôts, la livre parallèle s'effondre."),
         (2020,"Explosion du port et défaut souverain","Le Liban fait défaut sur sa dette en dollars : la crise devient l'une des pires au monde depuis 1850 (Banque mondiale).")],
 "SYR": [(1946,"Indépendance","La Syrie moderne naît du mandat français, instabilité politique chronique."),
         (1970,"Prise de pouvoir d'Hafez el-Assad","Début de plus de 50 ans de régime Assad : État centralisé, économie contrôlée."),
         (2000,"Arrivée de Bachar el-Assad","Libéralisation partielle ('économie sociale de marché') vite interrompue."),
         (2011,"Début de la guerre civile","Le conflit détruit environ la moitié du PIB, les infrastructures et la monnaie."),
         (2020,"Loi César (sanctions américaines)","Les sanctions ferment presque totalement l'accès aux financements internationaux."),
         (2024,"Chute du régime Assad (décembre)","Fin du régime : transition politique et enjeu immense de reconstruction et de levée des sanctions.")],
}

EVENTS = [
 dict(titre="Forte hausse du prix du pétrole", chaine=["Un choc d'offre ou une tension au Moyen-Orient fait bondir le baril.",
      "Les pays exportateurs encaissent des recettes record ; les importateurs voient leur facture énergétique exploser.",
      "Les devises des exportateurs se renforcent, leurs bourses montent ; le CDS des importateurs fragiles se dégrade.",
      "Secteurs gagnants : énergie et banques du Golfe. Perdants : transport, chimie, pays importateurs endettés."],
      gagnants=["Arabie Saoudite","Émirats Arabes Unis"], perdants=["Liban","Maroc","Japon"],
      passe="En 1973, le choc pétrolier a transféré une richesse massive vers le Golfe et plongé les pays importateurs en stagflation."),
 dict(titre="Tension régionale majeure au Moyen-Orient", chaine=["Un conflit ou une escalade menace les détroits et les infrastructures énergétiques.",
      "Le pétrole et l'or montent (valeurs refuges), le tourisme et l'investissement régional chutent.",
      "Les CDS de toute la région se tendent, d'abord ceux des pays fragiles ; les capitaux fuient vers le dollar et le franc suisse.",
      "Les pays du Golfe résistent grâce à leurs réserves ; Liban et Syrie absorbent le choc de plein fouet."],
      gagnants=["États-Unis (dollar refuge)"], perdants=["Liban","Syrie","Émirats Arabes Unis (tourisme)"],
      passe="En 1990-91, la guerre du Golfe a fait flamber le pétrole puis l'a fait rechuter après la victoire rapide de la coalition : la durée du choc fait tout."),
 dict(titre="Nouvelle salve de la guerre commerciale USA – Chine", chaine=["Washington relève les droits de douane ou restreint les exportations de technologies.",
      "Les chaînes d'approvisionnement se réorganisent vers le Vietnam, l'Inde ou le Maroc (nearshoring).",
      "Les bourses tech des deux camps corrigent ; le yuan se déprécie ; les pays 'connecteurs' attirent les usines délocalisées.",
      "Gagnants relatifs : pays d'accueil des délocalisations. Perdants : exportateurs pris entre les deux blocs."],
      gagnants=["Maroc","Émirats Arabes Unis"], perdants=["Chine","Japon"],
      passe="Depuis 2018, chaque salve tarifaire a accéléré la diversification des chaînes de valeur hors de Chine — un mouvement structurel, pas un accident."),
 dict(titre="Une grande banque centrale relève fortement ses taux", chaine=["La Fed (ou la BCE) durcit sa politique pour combattre l'inflation.",
      "Le dollar se renforce et les capitaux quittent les pays émergents pour les bons du Trésor américain.",
      "Les devises émergentes chutent, le service de la dette en dollars des pays fragiles explose, leurs CDS grimpent.",
      "Les pays à réserves solides et faible dette externe traversent ; les autres négocient avec le FMI."],
      gagnants=["États-Unis"], perdants=["Afrique du Sud","Liban","Maroc (coût d'emprunt)"],
      passe="En 1980-82, le 'choc Volcker' a déclenché la crise de la dette des pays en développement pour une décennie entière."),
 dict(titre="Crise de la dette dans un pays fragile", chaine=["Un État ne peut plus refinancer sa dette : les marchés se ferment pour lui.",
      "La monnaie chute, l'inflation s'emballe, les banques locales (pleines de dette publique) vacillent.",
      "Défaut ou restructuration : les porteurs d'obligations perdent une partie de leur capital (haircut).",
      "L'effet de contagion reste limité si le pays est petit, mais les voisins voient aussi leur prime de risque monter."],
      gagnants=["Aucun directement — les fonds 'vautours' achètent la dette décotée"], perdants=["Liban","Syrie (accès aux marchés)"],
      passe="Le Liban (2020) et l'Argentine (à répétition) montrent qu'un défaut détruit d'abord l'épargne des habitants du pays lui-même."),
 dict(titre="Boom mondial de l'intelligence artificielle", chaine=["Les investissements dans les data centers et les semi-conducteurs explosent.",
      "Les pays qui fournissent puces, énergie bon marché et capitaux captent la vague ; les autres deviennent clients.",
      "Les indices tech (Nasdaq en tête) surperforment ; les fonds souverains du Golfe investissent massivement dans l'IA.",
      "Le risque : une bulle sur les valorisations, comme en 2000 avec internet."],
      gagnants=["États-Unis","Émirats Arabes Unis","Arabie Saoudite"], perdants=["Pays sans infrastructure numérique ni énergie compétitive"],
      passe="Comme l'électricité au XXe siècle, l'IA est une technologie 'à usage général' : les gagnants durables sont souvent les fournisseurs d'infrastructures."),
]

def make_quiz():
    q = {}
    for c in COUNTRIES:
        hist = HISTORY[c["iso"]]
        q[c["iso"]] = [
            (f"Quel événement fondateur figure dans la frise du pays « {c['nom']} » ?",
             [f"{hist[0][0]} — {hist[0][1]}", f"{hist[-1][0]} — {hist[-1][1]}", "Les deux événements ci-dessus"],
             2, "Les deux événements ouvrent et ferment la frise historique du pays dans l'application."),
            (f"Quelle est la banque centrale de « {c['nom']} » ?",
             [c["banque_centrale"], "La Réserve fédérale (Fed)", "La Banque centrale européenne uniquement"],
             0, f"C'est bien : {c['banque_centrale']}."),
            (f"Quel est l'indice boursier de référence cité pour « {c['nom']} » ?",
             [c["bourse"], "Le S&P 500", "Le CAC 40"],
             0, f"Réponse : {c['bourse']}."),
        ]
    return q
QUIZ = make_quiz()

# ============================================================
# 2. CALCULS — Score GeoCapital, Ke (Damodaran), verdict
# ============================================================
def pts_croissance(v):
    return 20 if v >= 5 else 16 if v >= 3 else 12 if v >= 1.5 else 8 if v >= 0 else 3

def pts_inflation(v):
    return 10 if v <= 2 else 8 if v <= 4 else 6 if v <= 7 else 3 if v <= 12 else 0

def pts_dette(v):
    if v == 0:  # donnée inconnue (Syrie) : traitée comme risque maximal
        return 0
    return 10 if v <= 40 else 8 if v <= 70 else 6 if v <= 100 else 3 if v <= 150 else 1

RATING_PTS = {"AAA": 10, "AA+": 9.5, "AA": 9, "AA-": 9, "A+": 8, "A": 8, "A-": 7.5,
              "BBB+": 7, "BBB": 7, "BB+": 5, "BB": 5, "BB-": 4, "B": 3,
              "CCC": 1, "D (défaut)": 0, "Non noté": 0}

def pts_cds(v):
    if v is None:
        return 0  # donnée manquante = signal de risque
    return 10 if v < 75 else 8 if v <= 200 else 6 if v <= 400 else 3 if v <= 700 else 1

def components(c):
    """Retourne dict critère -> (points, maximum)."""
    return {
        "Croissance": (pts_croissance(c["croissance"]), 20),
        "Stabilité macro (inflation + dette)": (pts_inflation(c["inflation"]) + pts_dette(c["dette"]), 20),
        "Risque souverain (notation + CDS)": (RATING_PTS.get(c["notation"], 0) + pts_cds(c["cds"]), 20),
        "Stabilité politique & historique": (round(c["stabilite"] * 1.5, 1), 15),
        "Marché financier": (c["liquidite"] + c["bourse_dev"], 15),
        "Facilité d'investir": (c["facilite"], 10),
    }

def adjusted_score(c, profil):
    comp = components(c)
    weights = {k: mx for k, (pt, mx) in comp.items()}
    if profil == "Prudent":
        weights["Risque souverain (notation + CDS)"] *= 2
        weights["Stabilité politique & historique"] *= 2
    elif profil == "Audacieux":
        weights["Croissance"] *= 2
        weights["Marché financier"] *= 2
    num = sum((pt / mx) * weights[k] for k, (pt, mx) in comp.items())
    return round(100 * num / sum(weights.values()), 1)

def ke_pays(c, rf, beta):
    """Ke = Rf + beta x ERP totale du pays (Damodaran). Le CDS n'est PAS
    rajouté : l'ERP totale contient déjà la prime de risque pays."""
    return round(rf + beta * c["erp"], 2)

def verdict(score):
    if score >= 75: return "✅ INVESTIR", "#1e8449"
    if score >= 60: return "🟡 INVESTIR AVEC PRUDENCE", "#b7950b"
    if score >= 45: return "🟠 ATTENDRE", "#ca6f1e"
    return "🔴 ÉVITER", "#c0392b"

def feu(valeur, seuils):
    """seuils = (max vert, max orange) pour un indicateur 'plus bas = mieux'."""
    return "🟢" if valeur <= seuils[0] else "🟠" if valeur <= seuils[1] else "🔴"

def build_df(profil, rf, beta):
    rows = []
    for c in COUNTRIES:
        s = adjusted_score(c, profil)
        v, _ = verdict(s)
        rows.append({**c, "score": s, "ke": ke_pays(c, rf, beta), "verdict": v})
    return pd.DataFrame(rows)

def ai_text(kind, payload):
    """IA optionnelle (Claude Haiku 5.5) si une clé est présente dans les
    secrets ; sinon texte de repli construit à partir des données.
    La clé ne doit JAMAIS être écrite dans le code."""
    key = None
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        key = None
    if key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=key)
            msg = client.messages.create(
                model="claude-haiku-5-5", max_tokens=300,
                system=("Tu expliques uniquement les données fournies. Tu n'inventes aucun chiffre, "
                        "aucune date, aucune notation. Si une donnée est absente, dis-le. "
                        "Français simple, 120 mots maximum."),
                messages=[{"role": "user", "content": payload}])
            return msg.content[0].text
        except Exception:
            pass  # repli silencieux : l'app ne doit jamais planter à cause de l'IA
    return None

# ============================================================
# 3. INTERFACE
# ============================================================
if "visited" not in st.session_state: st.session_state.visited = set()
if "quiz_score" not in st.session_state: st.session_state.quiz_score = 0
if "quiz_done" not in st.session_state: st.session_state.quiz_done = set()

st.sidebar.title("🌍 GeoCapital")
st.sidebar.markdown("*Connaître le passé pour anticiper le futur*")
profil = st.sidebar.selectbox("Profil d'investisseur", ["Équilibré", "Prudent", "Audacieux"])
rf = st.sidebar.slider("Taux sans risque mondial Rf (%)", 0.0, 8.0, 4.0, 0.25)
beta = st.sidebar.slider("Bêta (sensibilité au marché)", 0.5, 1.5, 1.0, 0.05)
page = st.sidebar.radio("Navigation", ["🗺️ Carte Vivante", "📄 Fiche Pays", "⚖️ Comparateur",
                                       "📰 Décodeur d'Actualité", "💼 Portefeuille Mondial", "🧠 Carte Mentale & Quiz"])
with st.sidebar.expander("📖 Glossaire express"):
    st.markdown("""
    - **CDS** : assurance contre le défaut d'un État ; cher = État jugé risqué.
    - **Notation souveraine** : note (AAA à D) donnée à un État par les agences.
    - **ERP** : prime de risque totale exigée pour investir dans un pays (Damodaran).
    - **Ke** : rendement minimum exigé par un investisseur : Ke = Rf + β × ERP.
    - **HHI** : indice de concentration d'un portefeuille (proche de 1 = concentré).
    """)
df = build_df(profil, rf, beta)

st.markdown('<div class="main-title">🌍 GeoCapital</div>', unsafe_allow_html=True)
st.markdown('<div class="slogan">« Connaître le passé pour anticiper le futur » — Clique sur un pays. Comprends son histoire. Mesure son risque. Décide comme un investisseur.</div>', unsafe_allow_html=True)

# ---------- PAGE 1 : CARTE VIVANTE ----------
if page == "🗺️ Carte Vivante":
    mode = st.selectbox("Colorer la carte par :", ["Score GeoCapital", "Rendement exigé Ke", "Croissance du PIB"])
    col = {"Score GeoCapital": "score", "Rendement exigé Ke": "ke", "Croissance du PIB": "croissance"}[mode]
    fig = px.choropleth(df, locations="iso", color=col, hover_name="nom",
                        hover_data={"score": True, "ke": True, "verdict": True, "iso": False},
                        color_continuous_scale="RdYlGn" if mode != "Rendement exigé Ke" else "RdYlGn_r",
                        title=f"Carte mondiale — {mode} (profil : {profil})")
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Classement des 10 pays")
    st.dataframe(df.sort_values("score", ascending=False)[["nom", "categorie", "score", "ke", "verdict", "notation", "erp"]]
                 .rename(columns={"nom": "Pays", "categorie": "Catégorie", "score": "Score /100",
                                  "ke": "Ke exigé (%)", "verdict": "Verdict", "notation": "Notation", "erp": "ERP (%)"}),
                 use_container_width=True, hide_index=True)
    st.info("💡 Lecture : un score élevé = pays attractif. Un Ke élevé n'est pas une promesse de gain : c'est le prix du risque, exigé par les investisseurs.")

# ---------- PAGE 2 : FICHE PAYS ----------
elif page == "📄 Fiche Pays":
    nom = st.selectbox("Choisir un pays", df["nom"].tolist())
    c = next(x for x in COUNTRIES if x["nom"] == nom)
    row = df[df["nom"] == nom].iloc[0]
    st.session_state.visited.add(c["iso"])
    vtxt, vcol = verdict(row["score"])
    a, b, cc = st.columns(3)
    a.metric("Score GeoCapital (profil " + profil + ")", f"{row['score']} / 100")
    b.metric("Rendement exigé Ke", f"{row['ke']} %", help="Ke = Rf + β × ERP totale (Damodaran)")
    cc.markdown(f'<div class="verdict-box" style="background:{vcol}22; border:2px solid {vcol};">{vtxt}</div>', unsafe_allow_html=True)
    st.markdown(f"**Catégorie :** {c['categorie']} · **Région :** {c['region']} · **Devise :** {c['devise']} · **Banque centrale :** {c['banque_centrale']}")
    st.markdown(f"**Régime :** {c['regime']}. {c['institutions']}")

    st.subheader("📜 Frise historique — comment ce pays s'est construit")
    for annee, titre, texte in HISTORY[c["iso"]]:
        st.markdown(f"**{annee} — {titre}** : {texte}")

    st.subheader("🤝 Relations avec le monde")
    c1, c2, c3 = st.columns(3)
    c1.markdown("**Alliés / partenaires**\n" + "\n".join(f"\n- {x}" for x in c["allies"]))
    c2.markdown("**Rivaux / tensions**\n" + "\n".join(f"\n- {x}" for x in c["rivaux"]))
    c3.markdown("**Dépendances clés**\n" + "\n".join(f"\n- {x}" for x in c["dependances"]))

    st.subheader("📊 Tableau de bord financier (données de démonstration 2024)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"{feu(c['inflation'], (3, 7))} Inflation", f"{c['inflation']} %", help="Inflation faible et stable = épargne protégée.")
    m2.metric(f"{feu(c['dette'] if c['dette'] else 999, (70, 110))} Dette publique / PIB", f"{c['dette']} %" if c["dette"] else "Non publiée", help="Dette élevée = l'État paie cher pour emprunter = risque pour l'investisseur.")
    m3.metric("Notation souveraine", c["notation"], help="Note de l'État par les agences : AAA = le plus sûr, D = défaut.")
    m4.metric("CDS souverain", f"{c['cds']} bps" if c["cds"] else "⚠️ Non disponible", help="Prime d'assurance contre le défaut de l'État. Absent = signal de risque.")
    m5, m6, m7, m8 = st.columns(4)
    m5.metric("Croissance du PIB", f"{c['croissance']} %")
    m6.metric("Taux directeur", f"{c['taux']} %")
    m7.metric("Chômage", f"{c['chomage']} %")
    m8.metric("Prime de risque ERP (Damodaran)", f"{c['erp']} %")
    st.markdown(f"**Bourse :** {c['bourse']} · **Devise sur 5 ans :** {c['devise_5ans']} · **Réserves :** {c['reserves']}")
    st.markdown(f"**Note méthodologique Ke :** Ke = {rf} % (Rf) + {beta} × {c['erp']} % (ERP) = **{row['ke']} %**. Le CDS n'est pas rajouté : l'ERP totale contient déjà la prime de risque pays (éviter le double comptage). Traduction : un investisseur rationnel doit exiger au moins {row['ke']} % dans ce pays — en dessous, le risque n'est pas payé.")
    if c["cds"] is None:
        st.warning("⚠️ Donnée manquante (CDS / notation) : dans GeoCapital, une donnée manquante est un signal de risque en soi — elle vaut 0 point sur ce critère.")

    st.subheader("🎯 Détail du Score GeoCapital")
    comp = components(c)
    figb = go.Figure(go.Bar(x=[pt for pt, mx in comp.values()], y=list(comp.keys()), orientation="h",
                            text=[f"{pt}/{mx}" for pt, mx in comp.values()], textposition="outside",
                            marker_color="#0b5345"))
    figb.update_layout(height=300, xaxis=dict(range=[0, 21]), margin=dict(l=10, r=40, t=10, b=10))
    st.plotly_chart(figb, use_container_width=True)
    best = max(comp, key=lambda k: comp[k][0] / comp[k][1]); worst = min(comp, key=lambda k: comp[k][0] / comp[k][1])
    st.markdown(f"**Secteurs porteurs :** {' · '.join(c['secteurs'])}")
    if st.button("🤖 Expliquer ce verdict simplement"):
        prompt = (f"Explique le verdict d'investissement pour {c['nom']} : score {row['score']}/100, "
                  f"Ke exigé {row['ke']} %, notation {c['notation']}, inflation {c['inflation']} %, dette {c['dette']} % du PIB. "
                  f"Point fort : {best}. Point faible : {worst}.")
        txt = ai_text("verdict", prompt) or (
            f"**{c['nom']}** obtient {row['score']}/100 (profil {profil}). Son point fort : *{best}*. "
            f"Son point faible : *{worst}*. Le rendement exigé de {row['ke']} % reflète ce risque : "
            f"plus il est élevé, plus l'investisseur doit être payé pour accepter l'incertitude de ce pays. "
            f"Verdict : {vtxt}.")
        st.success(txt)

# ---------- PAGE 3 : COMPARATEUR ----------
elif page == "⚖️ Comparateur":
    presets = {"USA vs Chine": ["États-Unis", "Chine"], "Arabie Saoudite vs Émirats": ["Arabie Saoudite", "Émirats Arabes Unis"],
               "Liban vs Syrie": ["Liban", "Syrie"], "France vs Japon": ["France", "Japon"],
               "Maroc vs Afrique du Sud": ["Maroc", "Afrique du Sud"]}
    choix_preset = st.selectbox("Comparaisons pédagogiques", list(presets.keys()))
    sel = st.multiselect("Pays à comparer (2 ou 3)", df["nom"].tolist(), default=presets[choix_preset], max_selections=3)
    if len(sel) >= 2:
        sub = df[df["nom"].isin(sel)]
        st.dataframe(sub[["nom", "score", "ke", "verdict", "croissance", "inflation", "dette", "notation", "erp"]]
                     .rename(columns={"nom": "Pays", "score": "Score", "ke": "Ke (%)", "verdict": "Verdict",
                                      "croissance": "Croissance %", "inflation": "Inflation %", "dette": "Dette/PIB %",
                                      "notation": "Notation", "erp": "ERP %"}),
                     use_container_width=True, hide_index=True)
        cats = list(components(COUNTRIES[0]).keys())
        figr = go.Figure()
        for _, r in sub.iterrows():
            co = components(next(x for x in COUNTRIES if x["iso"] == r["iso"]))
            figr.add_trace(go.Scatterpolar(r=[100 * pt / mx for pt, mx in co.values()] + [100 * list(co.values())[0][0] / list(co.values())[0][1]],
                                           theta=cats + [cats[0]], fill="toself", name=r["nom"]))
        figr.update_layout(height=460, polar=dict(radialaxis=dict(range=[0, 100])))
        st.plotly_chart(figr, use_container_width=True)
        safest = sub.loc[sub["score"].idxmax(), "nom"]; highke = sub.loc[sub["ke"].idxmax(), "nom"]
        st.info(f"🏆 Le plus sûr du groupe : **{safest}**. 💰 Le rendement exigé le plus élevé (donc le risque le mieux payé sur le papier) : **{highke}**. "
                "Attention : un Ke élevé ne veut pas dire un bon investissement — il veut dire un risque élevé qu'il faut être payé pour porter.")

# ---------- PAGE 4 : DÉCODEUR D'ACTUALITÉ ----------
elif page == "📰 Décodeur d'Actualité":
    ev_titres = [e["titre"] for e in EVENTS]
    ev = next(e for e in EVENTS if e["titre"] == st.selectbox("Choisir un événement", ev_titres))
    st.subheader("🔗 La chaîne causale : de l'événement à ton portefeuille")
    cols = st.columns(4)
    labels = ["1️⃣ Événement", "2️⃣ Conséquence économique", "3️⃣ Conséquence financière", "4️⃣ Gagnants / Perdants"]
    for col, lab, txt in zip(cols, labels, ev["chaine"]):
        col.markdown(f'<div class="chain-step"><b>{lab}</b><br>{txt}</div>', unsafe_allow_html=True)
    g, p = st.columns(2)
    g.success("**Pays / acteurs gagnants :** " + ", ".join(ev["gagnants"]))
    p.error("**Pays / acteurs perdants :** " + ", ".join(ev["perdants"]))
    st.markdown(f"**🕰️ Le passé éclaire :** {ev['passe']}")
    if st.button("🤖 Décrypter avec l'IA"):
        txt = ai_text("event", f"Décrypte cet événement pour un étudiant non expert : {ev['titre']}. Chaîne : {' → '.join(ev['chaine'])}") or \
              ("En résumé : cet événement se propage toujours par la même mécanique — prix et flux d'abord, "
               "devises et taux ensuite, décisions d'investissement enfin. Les pays à réserves et faible dette absorbent le choc ; "
               "les pays fragiles le paient en prime de risque.")
        st.success(txt)

# ---------- PAGE 5 : PORTEFEUILLE MONDIAL ----------
elif page == "💼 Portefeuille Mondial":
    st.subheader("Répartis 100 000 (fictifs) entre les 10 pays")
    devise_pf = st.selectbox("Devise du portefeuille", ["USD", "MAD"])
    weights = {}
    cols = st.columns(2)
    for i, (_, r) in enumerate(df.iterrows()):
        with cols[i % 2]:
            weights[r["iso"]] = st.slider(f"{r['nom']} — score {r['score']}, Ke {r['ke']} %", 0, 100, 0, key="w_" + r["iso"])
    total = sum(weights.values())
    st.progress(min(total, 100) / 100, text=f"Total réparti : {total} %")
    if total != 100:
        st.warning("Le total doit faire exactement 100 % pour calculer le portefeuille.")
    else:
        w = {k: v / 100 for k, v in weights.items() if v > 0}
        exp_ret = sum(w[k] * df.loc[df["iso"] == k, "ke"].iloc[0] for k in w)
        risk = sum(w[k] * (100 - df.loc[df["iso"] == k, "score"].iloc[0]) for k in w)
        hhi = sum(v * v for v in w.values()); div = (1 - hhi) * 100
        a, b, cc = st.columns(3)
        a.metric("Rendement espéré (pondéré par les Ke)", f"{exp_ret:.2f} %")
        b.metric("Risque du portefeuille (/100)", f"{risk:.1f}")
        cc.metric("Score de diversification", f"{div:.0f} / 100", help="HHI = somme des carrés des parts. Proche de 100 = bien diversifié.")
        pf = pd.DataFrame({"Pays": [df.loc[df["iso"] == k, "nom"].iloc[0] for k in w], "Part (%)": [v * 100 for v in w.values()]})
        st.plotly_chart(px.pie(pf, names="Pays", values="Part (%)", title=f"Répartition du portefeuille (100 000 {devise_pf} fictifs)"), use_container_width=True)
        fragile = sum(v for k, v in w.items() if df.loc[df["iso"] == k, "categorie"].iloc[0] == "Fragile")
        msg = ("Portefeuille très concentré : un seul choc peut tout emporter." if div < 40 else
               "Portefeuille équilibré." if div < 75 else "Portefeuille bien diversifié.")
        if fragile > 0:
            msg += f" ⚠️ {fragile*100:.0f} % du portefeuille est placé dans des pays fragiles : le rendement exigé y est élevé parce que le risque de perte y est réel."
        st.info("🧠 Commentaire : " + msg)

# ---------- PAGE 6 : CARTE MENTALE & QUIZ ----------
else:
    st.subheader("🧠 Ta carte mentale du monde financier")
    st.progress(len(st.session_state.visited) / len(COUNTRIES),
                text=f"Pays explorés : {len(st.session_state.visited)} / {len(COUNTRIES)} — visite les fiches pays pour remplir ta carte.")
    if len(st.session_state.visited) == len(COUNTRIES):
        st.balloons(); st.success("🎉 Tu as exploré les 10 pays : ta carte mentale est complète !")
    nom = st.selectbox("Quiz — choisis un pays", [c["nom"] for c in COUNTRIES])
    c = next(x for x in COUNTRIES if x["nom"] == nom)
    for i, (qtxt, choix, bonne, expl) in enumerate(QUIZ[c["iso"]]):
        key = f"{c['iso']}_{i}"
        rep = st.radio(qtxt, choix, key="q_" + key, index=None)
        if st.button("Vérifier", key="b_" + key) and rep is not None:
            if rep == choix[bonne]:
                st.success("✅ Bonne réponse ! " + expl)
                if key not in st.session_state.quiz_done:
                    st.session_state.quiz_done.add(key); st.session_state.quiz_score += 1
            else:
                st.error("❌ Pas tout à fait. " + expl)
    st.metric("Score quiz cumulé", f"{st.session_state.quiz_score} bonnes réponses")

st.markdown("---")
st.markdown('<div class="small-note">GeoCapital — prototype pédagogique Streamlit. Données de démonstration (ordres de grandeur 2024) à vérifier et sourcer avant usage réel. '
            'Le Score GeoCapital et le Ke sont des outils d\'apprentissage, pas des conseils d\'investissement.</div>', unsafe_allow_html=True)
