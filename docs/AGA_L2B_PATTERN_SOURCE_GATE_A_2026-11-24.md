# L2b — AGA-011 Screen Pattern : correctif source-only

24/11/2026, main exclusivement. Autorisation auteur « ok go » après preuve [T06A FAIL](evidence/T06_PATTERN_RUNTIME_FAIL_L2_2026-11-24.TXT). Objectif 0.14.1. Prédécesseur exact P2d-L2 136332 octets SHA256 `b2811e56c12be23697f0bb3c60dbf67f01bdecae0cfb23a787e2d349070f44a1`, LAST_GOOD P2d protégée 136020 octets SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`. Source de départ `880fc5f009d3dec8a30c99f39327d9a1e1242bdb`. Pas de nouveau binaire installé.

## Correction

AP20 14, UNIT142+$00764. Remplacer les six octets source à $0077A (chargement Screen et graphics.library), branche MC68020 BRA.L vers un append-only après L1. En simple buffer, restaurer A3 et reprendre le code original à $00780. En DB, sélectionner ScreenBuffer opposé à DB+8, contrôler les pointeurs et dimensions, refuser l'alias avec le front. Acquisition L1_AcquireSafe, zéro à trois WaitTOF, aucune consommation Disp. Safe absent/port nul ou impair : aucun pixel, palette ou allocation. Reprendre la convention AllocVec 128 MEMF_CLEAR / InitRastPort de Back Fill ; RP privé lié au bitmap arrière, WaitBlit avant dessin et avant FreeVec. Calcul de mire et SetRGB32 identiques à l'ancien code, palette globale. Aucun Swap implicite. ABI A3 sauvée explicitement en plus du MOVEM historique. Si allocation refusée après acquisition Safe, la seule mutation légitime est l'acquittement Safe.

- [Overlay MC68020](../src/native/m19_p2d_l2b/M19_L2B_PATTERN_TAIL_MC68020.s)
- [Builder source](../tools/build_m19_p2d_l2b_pattern_in_memory.py)
- [Gate A](../tools/test_m19_p2d_l2b_pattern_gate_a.py)
- [Workflow](../.github/workflows/m19-p2d-l2b-pattern-gate-a.yml)

Le builder reconstruit L2 octet pour octet, réassemble le master P2d avec L1+L2b en dossier temporaire et réutilise le groupe BOBS L2 exact. Les garde-fous exigent que seuls le branchement de 6 octets et la queue append-only UNIT142 changent, que les 203 entrées et tokens restent identiques, que les liens PC16 restent inchangés, et que les deux Lib ne soient pas écrites. Cible MC68020. Aucun nouvel export de binaire ni désassemblage.

## Validation attendue (non exécutée à la rédaction)

184 cas Pattern sous Unicorn MC68020, deux modèles AP20, deux parités, deux profondeurs, témoin L2 qui dessine FRONT, simple buffer, Safe déjà acquis/retardé/absent, port invalide, échec allocation, invalidité écran/bitmap, indices et padding, RGB, registres, pile, mémoire et libération. Services OS simulés. Rejouer les 172 cas writers L1 et 10 suites Bob L2 sur la candidate. Gate A à lire sur le SHA exact, pas de PASS présumé. Gate B : même T06A inchangé, puis sonde Safe T06B distincte. Gate C manuelle reportée par l'auteur, D non testée. Pas de promotion ni publication.


## Reprise du contrôle AP20

Premier run [45448577208](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45448577208) FAIL avant exécution : le stub 14 contient l'offset relatif $0742, le dispatcher V2 ajoute $22 (34 octets) pour atteindre UNIT142+$0764. Le contrôle et le fixture utilisent désormais explicitement `len(DISPATCH_V2)`. Les sources natives L2b sont inchangées. Après PASS complet uniquement, la CI fournit un delta source borné (six octets, queue UNIT142 et titre AP20) avec SHA256 et blob Git de l'image testée ; aucun fichier Lib alternatif ni push CI. Bascule canonique explicitement autorisée par « ben go », conditionnée au PASS exact. README EN/FR : identité active en première ligne du résumé comme l'exige le contrôle, trois paragraphes, mention du défaut T06 confirmé.

## Gate A PASS et livraison autorisée

P2d-L2b active, 136 708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, blob `2809b4b409eea9e234df1b96bf2b08bd393d8c85`. [Gate A 45449139352](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45449139352) PASS (184 Pattern, 172 writers, 10 suites Bob), seconde reconstruction [45449077283](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45449077283) même SHA256. Gate B T06A à établir, C reportée, D non testée. LAST_GOOD P2d intacte.

UNIT142 62960 -> 63334 octets, branche $077A `60ff0000ee74`, append 374 octets ; groupe202 identique, PC16 max 854. Livraison exclusivement dans dist/AMOSPro_AGA.Lib, reconstitution via delta issu du run PASS et blob Git vérifié identique à l'image testée. Le premier run échoué contrôlait l'offset AP20 sans les 34 octets du dispatcher V2. Le run final utilise le séparateur NUL correct pour le blob Git. L'ASC T06A est activé sans changer ses octets. Aucune publication, promotion ou compilation AMOS. Les contrôles historiques reconnaissent l'identité L2b exacte ; nouvelles CI de livraison à établir.

## T06A Runtime PASS et suite

T06A Runtime PASS sur L2b : TARGET BACK, PROBE_COMPLETE 1, back 64/128/192, ancien front 239/239/239, ERR 0, 3 swaps sans refus, CAP_RETRIES 0, FILL_RETRIES 1, CLOSE_RETURNED 1, CLOSED_MOUSE_X -1. Défaut FRONT AGA-011 corrigé dans le scénario stabilisé. T06B sans pré-VBL reste à exécuter ; Gates C/D non testées sur L2b. Le banc T06A et les deux Lib restent inchangés. [Journal](evidence/T06_PATTERN_RUNTIME_PASS_L2B_2026-11-24.TXT). Journal original 461 octets CRLF, SHA256 `4d0842343c6c99cf9a4742497dd783066159077fc59eb1b3da7980707d943d3f`, blob `ca9e3266d06a81281a0db634856cd83c9aef1be7`.

[Gate A de reconstruction après livraison](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45450891738) PASS, [contrôle canonique](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45450891845) PASS. Les CI générales/historiques ont encore des échecs (Artifact integrity, documentation et d'autres) : L0 non clos. [T06B préparé](../tests/proto/t06_pattern_safe/README.md) préflight PASS, aucun changement natif ou binaire. Aucun nouveau PASS Runtime présumé.

## T06B Runtime PASS ; clôture du ciblage Pattern

T06B Runtime PASS sur L2b : 12/12 cycles, 12 Pattern immédiatement après Swap réussi sans VBL préalable, BACK_OK=FRONT_OK=12, 36 swaps, 0 refus Swap, 12 reprises Fill et 12 Capture abouties, ERR 0, CLOSE_RETURNED 1, CLOSED_MOUSE_X -1. T06A et T06B qualifiés en Runtime ; fenêtre post-Swap exercée sans observation directe du drapeau interne Safe. Refus Safe absent/allocateur injectés couverts par Gate A, pas par WinUAE. Compiler reporté, D non testée. [Journal original](evidence/T06B_SAFE_RUNTIME_PASS_L2B_2026-11-24.TXT). Journal original 488 octets CRLF, SHA256 `1f07abe44b08ae13b294ddec5e80f507642920deba9a8e64f750e36ab26d1263`, blob `030887327d580e83520df62ae99270e31423b85b`.

L3 : commencer par T14A, mesure mémoire Open/DB/Close avec curseur ; T10/T11 banques et caches, T14 autres variantes (B8/End/C2P et timeout), T16 Copper restent ouverts. [Protocole T14A](../tests/proto/l3_resources/README.md). Aucune modification binaire. Les CI historiques en échec demeurent à traiter en L0.

## L4 — régression intégrée Runtime

L4 P2 ALL IN ONE Runtime : journal transmis par l'auteur à la suite de la demande de régression L2b, RESULT1 ERR0 PHASE_LAST4 PRG_STATE1, VALID_SAMPLES240 SWAPS252, PIX0/1=29/29, COL_CHECKS8, FLIP_PIX0/1=8/12, PLANES_PIX0/1=5/5, AUTO_ENABLE/DISABLE=1/1, 121 refus récupérés sur 121 en une VBL chacun, CLOSE_RETURNED1, VERDICT PASS. Source gelée c48d334fd4508d402d28399bffdfec08d4cb4acb. Le fichier fourni est strictement identique au journal P2d du 21/11 : 1632 octets, 97 CRLF, SHA256 864f6b17652033b99f06ec34df3ce85f3a1579bbb52c033d67d62e178852c627, blob 4bf3931fbaf487f7cee92b0768c22e925f981fe2. La nouvelle exécution est associée à L2b par le protocole et le contexte de transmission ; le journal ne porte pas le SHA de la Lib et ne permet pas d'attester seul une exécution distincte. Ne pas dupliquer les octets historiques, ni transférer le PASS Compiler P2d à L2b. [Journal](evidence/M19_P2_ALL_IN_ONE_RUNTIME_PASS_2026-11-21.TXT). Aucun nouveau défaut fonctionnel détecté ; pas de validation C/D ou promotion. L0 et dispositions résiduelles L3 restent ouverts.
