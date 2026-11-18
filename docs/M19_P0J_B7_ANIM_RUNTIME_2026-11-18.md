# M19 P0j-b7-m1 — animation de quatre Bobs, Runtime WinUAE (18/11/2026)

> **Bilan WinUAE rapporté le 18/11/2026 : Gate B PASS pour cet ancien banc**. Le journal utilisateur indique `RESULT 1`, `ERR 0`, `FRAMES_OK 120`, `DRAW_FAILS 0`, `SWAP_FAILS 0`, `PATH_OK`. La capture montre les deux Bobs mobiles et les deux autres fixes avec clipping ; l'auteur confirme **quatre lancements sans problème et aucune traînée**. Cadence ressentie lente mais **aucun FPS mesuré**. Ce résultat ne valide ni le nouveau benchmark ni le vrai AMOS Compiler.

> **Historique figé :** l'ASC 4 730 octets SHA256 `a5a263e38faa2dfba75bf94beac4915c6ddea85e8c345f9a2f7eb0316d8190dd` est conservé à [ce commit](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/75caa3c8198aad612e434e1ae3d54ceb2249ca45/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc). Le chemin `tests/current/` est désormais utilisé par [le benchmark A/B/C](M19_B7M1_CLEAR_BENCH_RUNTIME_2026-11-18.md), sans modifier la version historique.

## Provenance figée

- Bibliothèque **B7-m1 autorisée comme candidate de travail**, dist/AMOSPro_AGA.Lib 102 360 octets, SHA256 **838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403**, 86 commandes / 181 sections AP20 / 4 unités natives MC68020+. Gate A B7-m1 PASS (793 contrôles multiframe et 88 B7 historiques). LAST_GOOD R84 non touchée.
- **ASC de l'ancienne campagne (historique Git) :** [M19_P0J_B7_ANIM_RUNTIME_03.asc](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/75caa3c8198aad612e434e1ae3d54ceb2249ca45/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc), **4 730 octets**, SHA256 **a5a263e38faa2dfba75bf94beac4915c6ddea85e8c345f9a2f7eb0316d8190dd**. [Banc et mode d'emploi](../tests/current/README.md).
- Ancien [End sans Close](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0e7be49a079f75f0ac628625d567b86a3afa042d/tests/current/M19_P0J_B7_END_NO_CLOSE_BC_02.asc) conservé octet pour octet en historique. Son ERR 2 au second lancement concernait les banques AMOS 24/25 encore réservées ; **Erase All** les a libérées dans le contexte de test. Cela ne mesure ni la RAM Chip ni les MsgPorts.

## Expérience Runtime uniquement

WinUAE AGA PAL, CPU 68030/JIT ON. Banques 24 et 25 libres. Les images masquée rouge et opaque jaune sont créées à partir de l'écran et capturées dans deux banques. Le programme déroule **120 frames**, avec deux Bobs mobiles en aller-retour, deux Bobs fixes partiellement hors écran, et re-sélection de la banque source à chaque placement.

**Ordre de chaque frame :** Aga Blit Fill(0,0,320,256,1) sur la page arrière, quatre placements de Bobs, **une seule fonction Aga Bob Draw**, puis Aga Swap uniquement après résultat Draw=1. Les retries Fill/Swap sont bornés à 40, une erreur bloque le chemin suivant. Une VBL stabilise l'observation ; aucune mesure CPU ou FPS n'est revendiquée. Après la dernière frame, le programme ferme explicitement l'écran, restaure AMOS, efface les banques créées et écrit RAM:M19_B7_ANIM_RUNTIME.TXT.

**Critères Runtime :** RESULT 1, ERR 0, FRAMES_OK 120, DOUBLE_BUFFER 1, CLEAR_FAILS 0, DRAW_FAILS 0, SWAP_FAILS 0, BANKS_ERASED 2, retour à l'éditeur sans Guru/freeze ; **aucune traînée ni corruption graphique visible**, masque/clipping corrects. Relancer une seconde fois **sans Erase All** : un nouvel ERR 3 indiquerait que les banques réservées par ce test n'ont pas été libérées comme prévu. PATH_OK est un statut de chemin logiciel, pas une preuve des pixels ou de la libération Chip OS.

**Gate B PASS pour cette ancienne animation Runtime uniquement (journal + retour utilisateur). Gate C : NON TESTÉE et aucun essai demandé.** Seul le binaire de travail, le test ASC actuel et leurs vérifications de provenance sont modifiés ; le source historique B7, R84 LAST_GOOD et les archives restent protégés.
