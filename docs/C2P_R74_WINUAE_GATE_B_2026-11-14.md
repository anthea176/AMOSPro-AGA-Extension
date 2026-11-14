# C2P — R74 v0.13.19 : Gate B AMOS interprété / WinUAE PASS

**Date : 14 novembre 2026.** Validation réelle de la **fonction `Aga C2P Open(Bank)` seule**, à partir de la capture de console transmise par l'auteur dans la discussion. Pas d'essai du programme compilé, pas de conversion chunky-to-planar, pas de benchmark ni de test matériel.

## Identité et périmètre

- Dépôt : `anthea176/AMOSPro-AGA-Extension` ; **branche `main` exclusivement**.
- Binaire de la candidate R74 v0.13.19 : `dist/AMOSPro_AGA.Lib`, **52 612 octets**, SHA256 `887f29c0350f47af9d93d1ebf64fc405c8542e897ff0e7d9d95eda6f814c2a23`, **65 commandes publiques / 72 entrées AP20**.
- Binaire protégé inchangé : `dist/AMOSPro_AGA_LAST_GOOD.Lib` = **R73 v0.13.18**, 51 608 octets, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`.
- ASC exécuté : [`tests/current/C2P_R74_OPEN_01.asc`](../tests/current/C2P_R74_OPEN_01.asc), en mode **interprété** tel qu'indiqué par l'auteur, avec `c2p.library` externe installée dans `LIBS:`. La capture seule n'atteste pas indépendamment des paramètres CPU/JIT de WinUAE.
- **Preuve source :** capture utilisateur `image(20261114-110310).png` du 14/11/2026, 1238×1046 pixels, SHA256 du PNG `b10df17105c332839f62ce6b01a75ace3e392bd3087b2b3c53b40947c9a0d686`. Capture fournie dans le chat ; **pas copiée dans GitHub**. Les résultats ci-dessous sont une transcription des valeurs affichées.

## Valeurs lues sur la capture

| Écran AGA | OPEN | DB | C2P | DUP | POST | Statut |
|---|---:|---:|---:|---:|---:|---|
| 320×256, **16 couleurs / 4 plans** | 1 | 1 | 1 | 0 | 0 | PASS |
| 320×256, **32 couleurs / 5 plans** | 1 | 1 | 1 | 0 | 0 | PASS |
| 320×256, **64 couleurs / 6 plans** | 1 | 1 | 1 | 0 | 0 | PASS |
| 320×256, **128 couleurs / 7 plans** | 1 | 1 | 1 | 0 | 0 | PASS |
| 320×256, **256 couleurs / 8 plans** | 1 | 1 | 1 | 0 | 0 | PASS |

Les lignes sont longues et `POST 0` revient visuellement à la ligne suivante sur la capture, sans modifier la valeur.

- `NOS/BADBANK 0 0` : refus d'Open sans écran et sur numéro de banque invalide.
- `DUP 0` : deuxième ouverture rejetée sur chaque écran après réussite du premier Open.
- `POST 0` : nouvel Open refusé après `Aga Screen Close`, en l'absence d'écran.
- `CHIP BEFORE/AFTER 1801952 1801952` : **aucun écart de Chip Free mesuré sur ce scénario** après les cinq cycles d'ouverture/fermeture et `Erase 12`.
- `RESULT 1` et `CLOSE RETURNED` : scénario d'acceptation terminé avec succès et retour de fermeture.
- Aucun Guru, gel ou erreur visible pendant ce test.

## Verdict et ce que cette preuve ne démontre pas

**Gate A CPU/ABI R74 : PASS** (25 scénarios host sous machine68k, contrôles des branches et pont AP20 V2). **Gate B R74 `Aga C2P Open` : PASS en AMOS interprété / WinUAE**, sur les cinq profondeurs testées.

La capture ne prouve pas une conversion de pixels : `Aga C2P Convert` n'est **pas implémentée**. Elle ne mesure pas l'usage de **Fast RAM**, ne vérifie pas le contenu pixel de la destination, et ne teste pas spécifiquement le nettoyage à la **sortie du programme AMOS** (l'ASC finit dans une boucle). Ces cas sont distincts des contrôles natifs hôte.

**Gate C AMOS Compiler R74 : NON TESTÉE. Gate D Amiga physique : NON TESTÉE.** La R74 reste une candidate, **pas une version `LAST_GOOD` promue** ; la référence R73 reste intacte.

## Suite

Avant toute implémentation supplémentaire, figer et faire approuver **séparément** le contrat de `Aga C2P Convert` (nouvelle validation de banque/adresse, bitmap interne, `Safe` du back buffer, `BltBitMap`, `WaitBlit`, gestion des échecs sans Swap) ; concevoir `Aga C2P Close` à part. Ne pas lancer une compilation Gate C intermédiaire sans décision sur le jalon final.

[Contrat Open R74](C2P_R74_OPEN_2026-11-14.md) · [architecture](C2P_R74_INTERMEDIATE_ARCHITECTURE_2026-11-14.md) · [test courant](../tests/current/C2P_R74_OPEN_01.asc).
