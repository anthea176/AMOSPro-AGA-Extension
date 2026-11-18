# M19 P0j-b7 — animation de quatre Bobs, Runtime WinUAE (18/11/2026)

## Provenance figée

- Bibliothèque **B7 inchangée**, dist/AMOSPro_AGA.Lib 102 072 octets, SHA256 **f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b**, 86 commandes / 181 sections AP20 / 4 unités natives MC68020+. Gate A B7 PASS (88 contrôles). LAST_GOOD R84 non touchée.
- **ASC actif unique :** [M19_P0J_B7_ANIM_RUNTIME_03.asc](../tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc), **4 718 octets**, SHA256 **0f92b7ee5e1d60b1c0ab78c0d96a7d1aaebb97f3db12696a62c9a73783ad7cb6**. [Banc et mode d'emploi](../tests/current/README.md).
- Ancien [End sans Close](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0e7be49a079f75f0ac628625d567b86a3afa042d/tests/current/M19_P0J_B7_END_NO_CLOSE_BC_02.asc) conservé octet pour octet en historique. Son ERR 2 au second lancement concernait les banques AMOS 24/25 encore réservées ; **Erase All** les a libérées dans le contexte de test. Cela ne mesure ni la RAM Chip ni les MsgPorts.

## Expérience Runtime uniquement

WinUAE AGA PAL, CPU 68030/JIT ON. Banques 24 et 25 libres. Les images masquée rouge et opaque jaune sont créées à partir de l'écran et capturées dans deux banques. Le programme déroule **120 frames**, avec deux Bobs mobiles en aller-retour, deux Bobs fixes partiellement hors écran, et re-sélection de la banque source à chaque placement.

**Ordre de chaque frame :** Aga Blit Fill(0,0,320,256,1) sur la page arrière, quatre placements de Bobs, **une seule fonction Aga Bob Draw**, puis Aga Swap uniquement après résultat Draw=1. Les retries Fill/Swap sont bornés à 40, une erreur bloque le chemin suivant. Une VBL stabilise l'observation ; aucune mesure CPU ou FPS n'est revendiquée. Après la dernière frame, le programme ferme explicitement l'écran, restaure AMOS, efface les banques créées et écrit RAM:M19_B7_ANIM_RUNTIME.TXT.

**Critères Runtime :** RESULT 1, ERR 0, FRAMES_OK 120, DOUBLE_BUFFER 1, CLEAR_FAILS 0, DRAW_FAILS 0, SWAP_FAILS 0, BANKS_ERASED 2, retour à l'éditeur sans Guru/freeze ; **aucune traînée ni corruption graphique visible**, masque/clipping corrects. Relancer une seconde fois **sans Erase All** : un nouvel ERR 3 indiquerait que les banques réservées par ce test n'ont pas été libérées comme prévu. PATH_OK est un statut de chemin logiciel, pas une preuve des pixels ou de la libération Chip OS.

**Gate B du nouveau scénario : NON TESTÉE avant retour WinUAE. Gate C : volontairement NON TESTÉE**, conformément à la consigne de limiter les compilations. Aucun changement du code natif, du builder B7, de la bibliothèque installable, d'archives ou de branche.
