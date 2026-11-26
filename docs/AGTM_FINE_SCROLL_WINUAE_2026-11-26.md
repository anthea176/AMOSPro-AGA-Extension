# AGTM — scrolling fin WinUAE, résultats reçus le 26/11/2026

**Statut : prototype AMOS B Runtime et C Compiler PASS.** Pas de moteur AGTM natif qualifié.

## Sources et preuves originales

[AGTM_FINE_SCROLL_BENCH.asc](../tests/proto/agtm_prototype/AGTM_FINE_SCROLL_BENCH.asc), Git blob `678b97867cfdd4485ea2a0517ab6c882150324f6`, SHA256 `a2d2de907f69e70a1dc86d0e7550dc5312d65a8a5ba6d6e648458be7ce70c3d6`. Source inchangée.

| Journal original (CRLF préservés) | Octets | SHA256 |
|---|---:|---|
| [Runtime](evidence/AGTM_FINE_RUNTIME_2026-11-26.TXT) | 1062 | `7fb865f0629a084ad12af7cca5e5b3501f4ff3f8535c01ee1217a01b1185110f` |
| [Compiler](evidence/AGTM_FINE_COMPILED_2026-11-26.TXT) | 1063 | `67349f8aba1e2bd305291863e61823ca23482124bf02773adbf903ddba709b1e` |

L'identité des journaux après archivage est vérifiée contre les blobs des fichiers originaux. La cible déclarée est P2d-L2b (`LIBRARY_EXPECTED`), mais la SHA de la Lib effectivement chargée, le CPU, la fréquence, le JIT et la version du Compiler ne sont pas présents dans les journaux. Ne pas assimiler une référence attendue à une preuve de configuration.

## Conformité

Les deux modes donnent RESULT=1, ERR=0, CHECKS=12, COMPARE_BYTES=983040, BYTE_MISMATCH=0, ORACLE_CHECKS=1008, ORACLE_BAD=0, BENCH_RUNS=12, LOW_TICK_RUNS=0, SWAPS=1, SAFE_WAITS=0, SWAP_WAITS=0, CLOSE_RETURNED=1. Les compteurs d'appels correspondent à la source. Chip/Fast avant et après identiques dans chaque mode ; aucune perte observée sur ces deux exécutions.

## Temps mesurés

320×256, 8 plans, une couche opaque, caméra horizontale. Deux passes AB/BA de huit déplacements par méthode, soit 16 mises à jour par cellule du tableau cumulé. Pas de 1, 8, 16 px, déplacements dans les deux sens, franchissement des limites de tuiles. Initialisations, captures, vérification et Swap/VBL hors chrono.

| Pas | FULL Runtime p0/p1 | SCROLL Runtime p0/p1 | Rapport | FULL Compiler p0/p1 | SCROLL Compiler p0/p1 | Rapport |
|---|---|---|---:|---|---|---:|
| 1 px | 214/222 = 436 | 39/39 = 78 | 5,59 | 162/162 = 324 | 35/35 = 70 | 4,63 |
| 8 px | 206/197 = 403 | 38/38 = 76 | 5,30 | 148/147 = 295 | 34/34 = 68 | 4,34 |
| 16 px | 187/187 = 374 | 35/34 = 69 | 5,42 | 138/139 = 277 | 31/31 = 62 | 4,47 |

Les valeurs sont des ticks Timer. Si le Timer est effectivement à 50 Hz (hypothèse PAL à confirmer), le coût SCROLL compilé moyen est de 87,5 / 85 / 77,5 ms par déplacement. Cela représente environ 11,4 / 11,8 / 12,9 mises à jour de décor par seconde hors présentation et logique de jeu, **pas des FPS de jeu mesurés ni une mesure sur A1200 physique**.

Le gain est celui des stratégies complètes : 2656 / 2624 / 2560 appels FULL contre 128 icônes + 8 copies SCROLL par série de huit déplacements. Le trafic réel Chip et le coût individuel du Blitter ne sont pas isolés.

## Suite expérimentale

Valider l'alternance effective des pages, les caméras/révisions indépendantes, les déplacements 2D, les edits et les overlays transparents. Mesurer séparément dessin et série présentée. Garder les ASC validés inchangés ; prototypes exclusivement dans tests/proto/. M20 natif reste après M21 et distinct du chantier Sprite. Gate D non testée. Aucune modification de la Lib ou de LAST_GOOD.
