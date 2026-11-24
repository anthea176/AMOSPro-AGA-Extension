# P2d-L2 — résultats WinUAE du 24 novembre 2026

**Bibliothèque utilisée : M19 P2d-L2, 136 332 octets, SHA256 `b2811e56c12be23697f0bb3c60dbf67f01bdecae0cfb23a787e2d349070f44a1`.** L'auteur confirme explicitement avoir mis à jour la Lib pour les derniers essais. LAST_GOOD P2d reste protégée. Gate A native : 172 cas writers et 10 suites Bob PASS. Pas de nouvelle compilation manuelle demandée : Gate C des autres scénarios reportée sur décision de l'auteur.

## Preuves brutes reçues (octets CRLF conservés)

| Journal | SHA256 | Résultat |
| --- | --- | --- |
| [EDGE SAFE 20x18](evidence/P2_EDGESAFE20X18_RUNTIME_PASS_L2_2026-11-24.TXT) | `e3381b21f1fe841159581c03800290c10545b00c4e3906cf2a2c797946b2c646` | Runtime PASS, 240/240 |
| [EDGE sans pré-VBL](evidence/P2_EDGE20X18_RUNTIME_PASS_L2_2026-11-24.TXT) | `2769d99f2271b6224443ddbb3a432918d3b1bd80046e5115e21cb9e19f3d1a91` | Runtime PASS, 240/240 |
| [RPG V9](evidence/RPG_P2D_V9_RUNTIME_PASS_L2_2026-11-24.TXT) | `a55aed085e90a9769b218c867896580eeeb5794a8776511032fa94d9d39241a5` | Runtime PASS, 250 frames |

EDGE SAFE correspond au scénario `P2_EDGESAFE20X18_FROM_P2_FULL_20261123`, source historique [P2_EDGE_SWAPVBL_20X18.asc](../tests/proto/rpg_bob_dim/P2_EDGE_SWAPVBL_20X18.asc), blob `25d9960f3417f7b79f0ea978e396fda812b4bb1d`. 241 swaps, 240 VBL pré-Swap, 128 échantillons edge, dernière valeur 165 attendue 165, zéro refus/retry, ERR 0, CLOSE_RETURNED 1. Les phases collisions/Flip/Planes n'ont pas été exécutées par ce banc ciblé. Le témoin EDGE sans VBL préalable a également passé sur L2 (voir ci-dessous). Les deux variantes sont distinctes.

EDGE sans pré-VBL : scénario `P2_EDGE20X18_FROM_P2_FULL_20261123`, [P2_EDGE_20X18.asc](../tests/proto/rpg_bob_dim/P2_EDGE_20X18.asc), blob `8e14e7135548913a0367642610f86d595a763539`. Journal original 1765 octets, 103 CRLF, Git blob `49fdc2586a633a8b1d8d2effca6c9fea5ad42cfc`. RESULT 1, ERR 0, FRAME 241, VALID_SAMPLES 240, SWAPS 241, EDGE_SAMPLES 128, EDGE_VALUE_LAST=EDGE_EXPECTED=165, SWAP_REFUSALS=SWAP_RECOVERED=RETRY_VBLS=120, FIRST_REFUSAL_FRAME 2, LAST_REFUSAL_FRAME 240, LAST_REFUSAL_TRIES 1, CLOSE_RETURNED 1. Ancien FAIL frame 221 non reproduit. Phases collision/Flip/Planes non exécutées dans ce banc. Aucun patch EDGE requis à ce stade ; ne pas répéter sur les mêmes octets. Compiler non testé pour cette variante. T06 et L3 restent ouverts.

RPG V9 : `PRG_STATE 1`, `RESULT 1`, `ERR 0`, STAGE PLAY, BG0/BG1/AUTO/BG_SWAP/BOB_SWAP=1, IFF 320x256x8, planche IFF chargée, BANKLEN 720, BANKMASK 1, 250 frames, 2 flips, 251 VBL pré-Swap, 2 retries, CLOSE_RETURNED 1. `FIRST_BOB_UPDATE -2` et `EXPLICIT_BOB_UPDATE 0` sont conservés tels quels ; le source V9 exact n'est pas disponible sur main à ce checkpoint, donc aucune interprétation de la sentinelle. Le libellé P2d/SHA historique dans ce journal est conservé intégralement ; l'identité L2 est attestée par l'auteur, pas par une mesure de SHA dans le journal. Ce scénario confirme la boucle RPG fonctionnelle avec pré-VBL, pas tous les timings Safe sans VBL.

## Résultats déjà communiqués par l'auteur

| Scénario | Gate B Runtime | Gate C Compiler |
| --- | --- | --- |
| SafePort IFF / Back Fill / premier Bind B8 | PASS rapporté | PASS rapporté |
| P2 ALL IN ONE | PASS rapporté : 240 samples, 252 swaps, 120 refus tous récupérés, collisions/Flip/Planes PASS | NON TESTÉ sur L2 |
| EDGE sans pré-VBL | PASS, log original ci-dessus | NON TESTÉ sur L2 |
| EDGE SAFE 20x18 | PASS, log original ci-dessus | NON TESTÉ sur L2 |
| RPG V9 | PASS, log original ci-dessus | NON TESTÉ sur L2 |

Les journaux originaux SafePort B/C et P2 ALL IN ONE ne sont pas disponibles dans cette reprise ; ne pas recréer ces preuves. Les anciens PASS P2d restent historiques. Gate D non testée.

## Suite

L0 : terminer l'adaptation des contrôles historiques à l'identité L2 exacte et séparer exemple public / ASC actif. T06 Pattern : vérifier la cible réelle de Screen.RastPort sans provoquer d'écriture non Safe ; T10/T11/T14/T16 ressources ensuite. Aucun nouveau code natif, remplacement de Lib, promotion, archivage ASC ou reprise Sprite autorisé par ces PASS. Un seul ASC actif conservé.
