# CDC - TruthMarket AI

## Objectif
Construire une application de comparaison entre probabilites de marche (Polymarket) et probabilites modelisees (ELO + historique + forme recente), avec une interface web rapide et partageable.

## Exigences fonctionnelles
- Afficher les signaux pour `worldcup`, `nba`, `ucl`.
- Proposer un mode clair/sombre avec persistance locale.
- Permettre le partage d'un signal individuel.
- Permettre le partage d'une comparaison multi-equipes (2 a 4 selections).
- Afficher des metriques globales (nombre de marches, signaux follow/against, heure de MAJ).

## Exigences performance
- Le chargement initial doit prioriser `worldcup`.
- Les rechargements repetes doivent utiliser un cache serveur a TTL court.
- Le parsing des marches ne doit pas introduire de delai par equipe.

## Exigences techniques
- Backend Flask avec endpoint `GET /api/analyze?sport=...`.
- Frontend HTML/CSS/JS vanilla (sans framework).
- Cache de fetch API cote collecte + cache de payload d'analyse cote API.
- Diagramme d'architecture genere automatiquement via script Python.

## Exigences UX
- Interface lisible sur desktop/mobile.
- Boutons de partage robustes:
  - API de partage natif si disponible.
  - fallback presse-papiers sinon.
- Retour visuel apres copie (etat "Copied").

## Livrables
- Application web fonctionnelle.
- Endpoint API documente.
- CDC a jour.
- Script de generation d'architecture et fichier de sortie Mermaid.
