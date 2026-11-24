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
