# Test actif M19 P0j-b7 — Bobs persistants multi-banques (Gates B/C)

**Campagne autorisée le 17 novembre 2026.** Une seule bibliothèque installable de travail et un seul ASC actif :

- **Lib B7 :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **102 072 octets**, SHA256 `f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b`.
- **Builder source déterministe :** [`tools/build_m19_p0j_end_lifecycle_in_memory.py`](../../tools/build_m19_p0j_end_lifecycle_in_memory.py), reconstruit B7 depuis B6 et toutes ses bases figées. 86 commandes, 181 entrées AP20, quatre unités natives, PC16 maximal 28 600.
- **Banc unique :** [`M19_P0J_B7_DRAW_BC_01.asc`](M19_P0J_B7_DRAW_BC_01.asc), **3 982 octets**, SHA256 `f411f13f8213a8ce7b72d7bf205a19cfca7d3ae3ff10087752ddf24f8af7e3af`. ASCII pur, sans ressource externe.
- **Gate A : PASS 88 contrôles MC68020** sur deux implantations, plus diagnostic Safe/Disp, [GitHub Actions 44185874211](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44185874211). **Gate B WinUAE : NON TESTÉE ; Gate C vrai Compiler : NON TESTÉE ; Gate D matériel : NON TESTÉE.**
- **R84 LAST_GOOD : protégée et inchangée** (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`).

Le test AP20 précédent `M19_AP20_ISLANDS_01.asc` a effectivement passé B/C avec **l'ancienne** bibliothèque de 96 908 octets. Ses octets restent disponibles [dans le commit précédent](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0423b15982853630653565cee634c7d4ab5f072a/tests/current/M19_AP20_ISLANDS_01.asc). **Ce PASS historique ne valide pas B7.** Le test validé n'a pas été réécrit ; il a été retiré du répertoire actif pour n'y laisser qu'un seul ASC.

## Installation WinUAE / AMOS Professional

1. Synchroniser le clone Windows avec **`main`**, sans changer de branche. Conserver une sauvegarde de l'ancienne extension **hors dépôt** ; ne pas toucher à `LAST_GOOD`.
2. Remplacer **uniquement** l'extension AGA dans son slot `APSystem` d'AMOS par `dist/AMOSPro_AGA.Lib`. Vérifier l'empreinte de la **copie installée** avec PowerShell `Get-FileHash "CHEMIN_DU_SLOT_APSystem\\AMOSPro_AGA.Lib" -Algorithm SHA256` : elle doit être `f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b`. Redémarrer AMOS pour recharger la table des commandes.
3. Démarrer **WinUAE AGA PAL, CPU 68030, JIT activé** pour les deux Gates fonctionnelles. Noter Kickstart/Workbench, Chip/Fast RAM, AMOS Professional, version exacte de l'AMOS Compiler V2. Le test exige les **banques AMOS 24 et 25 libres** et ne charge aucun IFF/ABK.
4. Ouvrir un programme AMOS vide, puis **Project → Merge ASCII** et choisir `tests/current/M19_P0J_B7_DRAW_BC_01.asc`. Ne pas utiliser `Load` sur cet ASCII.

## Gate B — Runtime AMOS

Lancer le programme en Runtime, relever le journal `RAM:M19_B7_RUNTIME.TXT` et une capture avant fermeture. `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `DRAW 1`, `SWAP 1`, `CLOSE 1`, les deux compteurs d'images à 1 et le masque à 1 sont attendus.

**Rendu attendu :** fond bleu foncé, image rouge/orange **masquée** à (103,72), image jaune **opaque** à (180,110), Bob masqué rogné à gauche (−5,170), Bob opaque rogné à droite (315,200). Les images proviennent de **deux banques distinctes**, avec conservation de la banque d'origine pour chaque Bob. Le Draw ne permute pas automatiquement l'écran ; un **unique** `Aga Swap` explicite présente le back buffer, et uniquement si le Draw a réussi.

Après maintien de l'affichage, `Aga Screen Close` doit se terminer, revenir à AMOS sans écran noir permanent, Guru ni gel ; les banques 24/25 du test sont effacées. Une valeur `RESULT 1` ne remplace pas la vérification **visuelle** des pixels, masques et clipping.

## Gate C — vrai AMOS Compiler V2

Compiler **ce même ASC** avec la **même Lib B7 installée**, générer un **nouvel exécutable** et le lancer sous WinUAE dans la même configuration. Conserver séparément `RAM:M19_B7_COMPILED.TXT`, la capture de l'exécutable, et toute trace d'erreur/gel. `PRG_STATE -1`, `RESULT 1`, `ERR 0`, `DRAW 1`, `SWAP 1`, `CLOSE 1` et un rendu pixel-exact comparable sont les critères.

**Attention :** le texte `CANDIDATE SHA256` inscrit par l'ASC est une chaîne fixe, pas un hachage calculé en AMOS. Il faut mesurer l'empreinte de la copie chargée dans `APSystem` séparément. Une compilation réussie sans exécution/fermeture ne vaut pas Gate C PASS.

## Limites et retour de test

Ce premier banc B/C qualifie **Draw + Swap + Close**. Le callback `End` avec notifications Safe/Disp différées est prouvé seulement en **Gate A MC68020 avec AmigaOS simulé** ; aucune Gate B/C n'est revendiquée pour ce cas. Un scénario `End` sans `Aga Screen Close` et un test de réponses Safe/Disp réellement retardées seront des validations séparées après ce premier banc.

Fournir les deux journaux `RAM:M19_B7_RUNTIME.TXT` et `RAM:M19_B7_COMPILED.TXT`, la capture **Runtime ou Compiled correctement identifiée**, et toute information WinUAE si `ERR` est non nul ou en cas de freeze. Le test utilise les codes 1=AGA absente, 2=banque occupée, 3=Open, 4=Double Buffer, 5–12=préparation/capture, 13=Draw, 14=Swap. Le constat Gate B/C sera écrit seulement à réception des résultats **pour cette empreinte B7 exacte**.
