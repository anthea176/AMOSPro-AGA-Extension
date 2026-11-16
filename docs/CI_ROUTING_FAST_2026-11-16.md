# CI AGA — controles rapides vs regressions completes (16/11/2026)

Ce document decrit les declencheurs automatises, sans modifier les Gates A/B/C/D ni les binaires.

## Matrice des controles sur `main`

| Changement | Workflow principal | Tests |
| --- | --- | --- |
| `README*.md`, `INSTALL*.md`, `examples/**` | [`aga-docs-fast.yml`](../.github/workflows/aga-docs-fast.yml) | Couverture exacte API AP20 / README FR+EN ; exemples publics ; aucune emission de Lib |
| `tools/test_readme_api_coverage.py`, `tools/test_examples.py` | `aga-docs-fast.yml` | Meme verification legere, sans batterie CPU historique |
| Source, builder ou test `tools/*m19_p0*.py` ; ASC M19 P0 | [`m19-p0a-r88-get-gate-a.yml`](../.github/workflows/m19-p0a-r88-get-gate-a.yml) | Gate A MC68020 et regressions M19 source-backed, en memoire seulement |
| `dist/AMOSPro_AGA.Lib` | Gate A M19 + [`m19-p0a-publish-github.yml`](../.github/workflows/m19-p0a-publish-github.yml) + docs rapides + politique CPU | Integrite SHA / AP20, reconstruction identique, tests natifs cibles ; **aucune publication par la CI** |
| Outils ou emetteurs historiques non-M19 P0, binaires historiques, fixtures de regression | [`artifact-integrity.yml`](../.github/workflows/artifact-integrity.yml) | Suite historique et integrite du coeur ; pas sur simples changements de README |
| `tools/**`, `src/**`, workflows et chemins proteges | [`aga-native-cpu-policy.yml`](../.github/workflows/aga-native-cpu-policy.yml) | Cible MC68020 et regles de livraison |
| Avant promotion/publication | [`artifact-regression-full.yml`](../.github/workflows/artifact-regression-full.yml) (**manuel**) | Batterie complete historique, distincte des Gates B/C WinUAE et Compiler |

`artifact-integrity.yml` conserve un controle historique complet **sur les modifications du coeur** et son declenchement manuel, ainsi que ses declencheurs particuliers de pre-release/release. Les chemins documentaires et les sources M19 P0 ont ete exclus des executions automatiques historiques (sans supprimer aucun test). Les changements M19 P0 gardent le workflow Gate A MC68020 dedie.

Les workflows automatiques rapides utilisent des groupes de concurrence separes par ref/evenement ; des commits successifs peuvent remplacer un controle automatique plus ancien devenu obsolete. Les demandes manuelles restent dans un groupe distinct. **La CI ne remplace jamais Gate B (Runtime WinUAE), Gate C (vrai AMOS Compiler) ni Gate D (materiel reel).**

## Validation et limite

- Tout nouveau .Lib passe obligatoirement par l'unique chemin `dist/AMOSPro_AGA.Lib` apres autorisation explicite, avec SHA/builder et un seul ASC dans `tests/current/`.
- Ne pas toucher a `dist/AMOSPro_AGA_LAST_GOOD.Lib`, `tests/passed/` ni aux archives.
- Pour une diffusion/release, lancer explicitement `Full artifact regression (manual pre-release)` depuis l'onglet GitHub Actions puis valider les Gates WinUAE et Compiler sur **le meme binaire**.
- Les gains en duree globale doivent etre mesures dans GitHub Actions apres les premiers commits. Les changements de declencheurs seuls ne prouvent pas une baisse du temps d'execution **d'une suite individuelle**.
