# T06A — Aga Screen Pattern : cible bitmap après Swap stabilisé

**Préparé 24/11/2026**, autorisation auteur « aller go » après PASS EDGE sans pré-VBL. Objectif 0.14.1, WinUAE Runtime uniquement, 68030/JIT ON/AGA PAL comme les derniers essais. Pas de nouveau binaire, pas de modification des sources natives, pas de Compiler demandé. LAST_GOOD P2d protégée.

[ASC](T06_PATTERN_TARGET.asc) : 6381 octets, ASCII LF, SHA256 `55f295a3bc78d38ad349f08e5d28e36e388d1cfd3333e700d91bcba5fcf4e795`, Git blob `8d7ca5b89c1d178242bd5f84d1677079f382e701`. Préflight local amos_preflight.py PASS sur cet ASC exact, aucun essai AMOS exécuté. **PREPARE / Gate B NON TESTEE.** Sonde hors distribution ; l'ASC unique tests/current reste intact.

## Résultat 24/11/2026 — Gate B FAIL

T06A Runtime FAIL sur P2d-L2 : PROBE_COMPLETE=1, TARGET FRONT, ERR 50, back 17/17/17 inchangé, ancien front 64/128/192. Trois Swaps sans refus, fermeture correcte. Écriture de la page présentée confirmée, pas une simple modification de palette. Défaut bloquant 0.14.1 ; aucune preuve d'écriture du back sous Safe pending (non testé).

[Journal original](../../../docs/evidence/T06_PATTERN_RUNTIME_FAIL_L2_2026-11-24.TXT), 460 octets, 27 CRLF, SHA256 `a20fe38d72e5dd58f97c3d8817257075fd75fe816d6eb1bee27c9dc6f36039ed`, blob `07048c4084abd7c38d08706a68051b6677410db8`. SINGLE_RETURNED=1 et SINGLE_CLOSED=1 attestent le retour de contrôle uniquement. Ne pas relancer sur L2 inchangée. Correction native proposée, à autoriser : conserver l'instruction sans argument et le mode simple buffer ; en double buffer, sélectionner explicitement le back et utiliser son RastPort de dessin vérifié, acquérir Safe avant toute écriture de pixels ou palette, reprise bornée comme Back Fill, refus sans mutation si délai épuisé, ne pas permuter implicitement. Conserver ABI, registres, état de dessin, L1/L2 et archives. Gate A native MC68020 : simple buffer, deux parités DB, Safe absent/disponible/acquitté, refus sans mutation, intégrité des pixels et état. Rejouer T06A à l'identique, puis T06B Safe sur candidate corrigée, avant L3. Aucun patch ni changement de Lib dans ce lot.

## Lancer

Lib active P2d-L2 SHA256 `b2811e56c12be23697f0bb3c60dbf67f01bdecae0cfb23a787e2d349070f44a1` (136332 octets). Programme vierge, banque 27 libre, Project > Merge ASCII, Runtime. Aucune IFF, ABK, AMCAF, Turbo ou C2P requis. Ne pas manipuler menus/écran pendant les swaps. Envoyer RAM:T06_PATTERN_RUNTIME.TXT. Premier affichage = mire (2 secondes en PAL), puis deux pages de test, dernier affichage 2 secondes.

## Oracle discriminant

Source L2 inchangée pour Pattern : AP20 14, [UNIT142+$00764](../../../src/native/m19_p2d/M19_UNIT142_BLOCK_00764_MC68020.s), d6=ligne, d7=floor(ligne*nombre de couleurs/hauteur), donc indices 64/128/192 à y=64/128/192 en 320x256x256. Le LVO -852 est **SetRGB32**, non LoadRGB32 (-882) ; -342 SetAPen, -306 RectFill avec Screen.RastPort. Référence [autodoc SetRGB32](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0328.html), [liste LVO](https://fossies.org/linux/uade/amigasrc/score/graphics_lib.i). Cela corrige la désignation du LVO dans l'audit, pas la routine native. La [documentation ChangeScreenBuffer](https://d0.se/autodocs/intuition.library/ChangeScreenBuffer) établit la nécessité du message Safe avant réutilisation de l'ancien bitmap, mais ne suffit pas à mesurer ici la cible effective de RastPort.

1. Simple buffer : exécuter la séquence visuelle de examples/screen.asc, fermer, vérifier Mouse X=-1. SINGLE_RETURNED/CLOSED vérifient retour de contrôle, pas les couleurs ni l'absence de fuite.
2. Nouvel écran DB sans Bob : Fill 17, capture 3 indices, Swap, Fill 239, capture 3 indices, Swap. Trois VBL puis capture de 17 ; capture réussie acquitte Safe, les deux pages portent des signatures distinctes.
3. Appeler Pattern uniquement dans cet état stabilisé. Trois VBL puis capture arrière. Si la signature est reconnue (17/17/17 ou 64/128/192), présenter cette page et capturer l'ancien front après trois VBL ; aucun Fill intermédiaire. Capture CBlock 8x1, méthode CPU 0, lecture de l'octet de poids fort de chaque plan à Start(27)+40 comme dans le banc L2 déjà testé ; trois points x160. On compare les indices, pas la palette globale. Tous les retries sont bornés à 4 ; fermeture et retour AMOS sur erreur.

| TARGET | Back y64/128/192 | Ancien front y64/128/192 | Verdict |
| --- | --- | --- | --- |
| BACK | 64/128/192 | 239/239/239 | PASS pour la cible stabilisée seulement |
| FRONT | 17/17/17 | 64/128/192 | FAIL : écriture sur page présentée |
| BOTH | 64/128/192 | 64/128/192 | FAIL : deux pages modifiées |
| NONE | 17/17/17 | 239/239/239 | FAIL : aucun dessin détecté |
| MIXED / UNKNOWN | autres valeurs ou capture incomplète | voir log | FAIL / diagnostic |

PROBE_COMPLETE=1 signifie les deux pages mesurées. PASS attendu pour contrat back-only : PRG_STATE=1, RESULT=1, ERR=0, PHASE_LAST=5, TARGET BACK, SWAPS=3, SWAP_REFUSALS=SWAP_RECOVERED, CLOSE_RETURNED=1, CLOSED_MOUSE_X=-1. KIND 0=marque, 1=mire, 2=autre. ERR50 est une cible incorrecte ou des indices inattendus, pas une erreur native AMOS. ERR31 = back mixte, pas de Swap supplémentaire. ERR2 = banque occupée, elle reste intacte ; autres ERR identifient le stade. Ce banc ne mesure pas les RGB, ne prouve pas les frees, et n'appelle délibérément pas Pattern sous Safe pending. Un PASS ne clôt pas T06 complet. Si FRONT/BOTH, corriger le ciblage avant toute sonde agressive ; si BACK, qualifier ensuite Safe absent/disponible/non acquitté et autres writers croisés. Pas d'essai physique de ce prototype.


## Reprise T06A sur L2b

P2d-L2b active, 136 708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, blob `2809b4b409eea9e234df1b96bf2b08bd393d8c85`. [Gate A 45449139352](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45449139352) PASS (184 Pattern, 172 writers, 10 suites Bob), seconde reconstruction [45449077283](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45449077283) même SHA256. Gate B T06A à établir, C reportée, D non testée. LAST_GOOD P2d intacte.

Utiliser [l'ASC actif](../../current/T06_PATTERN_TARGET.asc), octets strictement identiques au banc FAIL L2. Le protocole initial ci-dessus reste la référence de test ; aucune nouvelle compilation.
