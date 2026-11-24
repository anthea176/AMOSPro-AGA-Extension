# L3 — T14A Open/Close et mémoire (première sonde)

P2d-L2b inchangée : 136 708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, blob `2809b4b409eea9e234df1b96bf2b08bd393d8c85`. LAST_GOOD P2d protégée. Source [T14_CLOSE_MEMORY.asc](T14_CLOSE_MEMORY.asc), 4880 octets ASCII LF, SHA256 `99bc9947dc50732abcea784fb7e57c83803b4aeba48ad713a2abd04a9b7427d4`, blob `5ae340fa6985961b1bd7ad17c839fd9ad8593a86`. Préflight local du skill AMOS PASS, **Gate B NON TESTÉE**.

## Exécution

Même WinUAE que T06, 68030/JIT ON/AGA PAL, projet vierge -> Merge ASCII -> Runtime. Aucun IFF, ABK, banque AMOS ou c2p.library nécessaire. Ne pas manipuler le Workbench ni modifier la configuration mémoire pendant les mesures. RAM:T14_CLOSE_RUNTIME.TXT. Un seul ASC courant conservé à l'identique, nouvelle sonde sous tests/proto.

## Séquence

Une paire d'échauffement (simple buffer + double buffer), puis 12 paires identiques. Chaque écran : Open 320x256x256, Pattern, masquage répété du curseur, restauration puis masquage, Close avec curseur masqué. DB : Fill contrôlé, Swap avec reprise bornée à quatre VBL en cas de refus, puis Close sans VBL imposée après succès du Swap. Retour AMOS et Mouse X=-1. Aucun Swap après échec Fill. Les séquences reprennent les appels documentés de README.fr.md et les sondes T06, Chip Free / Fast Free de M19_P27_R87_CACHE_CPU_BLITTER_01.asc. Les deux tableaux sont réservés avant l'échauffement. Après chaque paire réussie, noter Chip Free et Fast Free ; paire 0 = référence, paires 1..12 = suivi, avant ouverture du journal RAM.

Attendu : PRG_STATE 1, RESULT 1, ERR 0, PAIRS_OK 12, CYCLES 26, SINGLE_OK 13, DB_OK 13, CURSOR_OK 104, SWAPS 13, SWAP_REFUSALS=SWAP_RECOVERED, CLOSE_RETURNED 26, CLOSED_MOUSE_X -1. Si les deux mesures restent identiques à la référence à chacune des 12 paires : MEM_STABLE 1, CHIP_LOSS=FAST_LOSS=0, DIFF_PAIRS 0, VERDICT PASS. Si tous les cycles passent mais qu'au moins une mesure diffère : VERDICT REVIEW ; analyser les valeurs des 13 paires (écarts, plateau, dérive). Une différence de mémoire disponible ne démontre pas à elle seule une fuite ; les mesures AMOS ne constituent pas un inventaire d'allocations Exec. Une stabilité n'exclut pas une fuite unique pendant l'échauffement, ni toutes les fuites possibles. Aucun seuil arbitraire ou PASS masqué. ERR10/11 Open/DB, ERR12..15 curseur, ERR20 Fill, ERR21 Swap, ERR60 Close/Mouse ; en FAIL, les mesures incomplètes ne sont pas interprétées comme un bilan mémoire final.

Ce premier test vise AGA-013 (oracle de fermeture) et une partie de T14 ; il ne couvre pas B8, C2P, End, Copper, banques/cache, refus OS injectés, ni tous les chemins d'allocation. T16 concerne le cycle Copper (matrice T01–T19). Les tests historiques et les preuves T06 restent intacts. Aucune modification de Lib ni compilation AMOS.
