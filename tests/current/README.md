# S2r-P1 — répartition AP20, campagne active unique

**27/11/2026 — S2r-P1 A/B/C fonctionnelles PASS dans le périmètre du banc.** B Runtime 1/1 (`PRG_STATE=1`, Fast transitoire 128 octets récupérés), C vrai Compiler 1/1 (`-1`, aucun écart cycle), 4/4 Capture/Meta/Negative/Draw, 300 changements/déplacements, 2/2 Open/Close, ERR=CLEAN_ERR=0, pertes nettes Chip/Fast nulles. Capture WinUAE fournie : trois rectangles rouges et trois Sprites distincts simultanés. Pas de preuve de seconde relance indépendante, de SHA installé ou Gate D physique. CI post-activation en échec sur l'accès Git superficiel au prédécesseur S2b ; [correction 21 workflows fetch-depth: 0](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/5c20ee6fca24b5248a7510c29d6586dfac3bfc0f) livrée, résultat final à relever. S2r active inchangée ; LAST_GOOD L2b protégée. Autorisation auteur « oui va y » pour corriger CI et consigner les preuves ; S2c après requalification CI, pas de promotion ni nouvelle Lib. [Résultats et journaux](../../docs/M19_S2R_RUNTIME_COMPILER_2026-11-27.md).

**27/11/2026 — S2r-P1 candidate active sur main, autorisation auteur « ok va y ».** [Gate A complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46059388877) : 8 jobs, 1200 changements Sprite, 600 cycles Show/Off, 20 fermetures et négatifs, 392 contrôles AGAPIC déplacés, DB/IFF/Swap/capture, 184 Pattern, 172 SafePort, 10 suites Bob. [Double construction et préflight ASC strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46059623366). Lib 154352 octets SHA256 `7e1dbfc26f9ae455b7cd8eca01a272c1ea1c7b83ad5a0739f631fd766959553a` blob `61d8211e449ffd9cb41e3fb2b6ec9efdf352c88c` ; ASC 11806 octets SHA256 `d06f3c296d45a8766acdf678b03675c99ee702baf776a2f2f50e2da5aa8939e3` blob `f1985251d4d37e978c4ec61b5e06f81fb3559ee4` ; même AGSP_S2B_MULTI.ABK 1012 octets blob `c122c79976bce5afad051f487d77af8cc296f2cc`. UNIT142 63350 (2184 libres), UNIT207 13756 (18978 libres PC16), nouvel îlot 214=3640, PC16 max 13786, 105 commandes / 219 AP20, MC68020+. Gates B/C/D réelles de S2r NON TESTÉES. S2b A/B/C historique dans Git ; LAST_GOOD L2b et toutes ABK protégées. Aucune promotion, autre branche, archive ou release.

## Fichiers à utiliser ensemble

- [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib), 154352 octets, SHA256 `7e1dbfc26f9ae455b7cd8eca01a272c1ea1c7b83ad5a0739f631fd766959553a`.
- [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc), 11806 octets, SHA256 `d06f3c296d45a8766acdf678b03675c99ee702baf776a2f2f50e2da5aa8939e3`.
- [AGSP_S2B_MULTI.ABK](AGSP_S2B_MULTI.ABK), 1012 octets, banque 29, inchangée depuis S2b. Banque 30 doit être libre (captures AGAPIC temporaires).

## Gate B — WinUAE Runtime (1/1 PASS, réserve Fast transitoire)

1. WinUAE AGA PAL, 68030 JIT ON, même configuration que S2b. Installer la Lib exacte dans APSystem, même slot, redémarrer complètement sans Save State. Vérifier le SHA de la copie installée.
2. ASC et ABK dans le même dossier, Project > Merge ASCII dans un programme vierge. Banques 29 et 30 libres. Runtime PRG_STATE=1.
3. Observer trois rectangles de même couleur en haut (original + v1 + v2), puis trois Sprites distincts, trois groupes de couleurs, mouvements opposés au milieu, alternances de frames, saturation refusée. Off du Sprite central seul, réapparition sous ID 9 ; les deux autres restent visibles. Deux fermetures actives et retour à AMOS.
4. Attendu : AGAPIC_CAPTURE 4 META 4 NEGATIVE 4 DRAW 4 ; AGAPIC_W 19 H 9 DEPTH 8 COLORS 256 MODE 135168 ; AGAPIC_RC 1 INFO_BAD -1 DUP_RC 0 DRAW_RC 1 OWN 0. OPENED=CLOSED=2, CHANGED=MOVED=300, SHOWN=8, OFF_COUNT=2, AUTO_CLOSE=6, SATURATION=2 FULL_RC=-206. SPRITE_RC=CHANGE_RC=MOVE_RC=OFF_RC=FREE_RC=1. CHIP_SCREEN_LOSS=FAST_SCREEN_LOSS=0, CHIP_BEFORE=CHIP_AFTER, FAST_BEFORE=FAST_AFTER, RESULT=1 ERR=0 CLEAN_ERR=0, VERDICT PASS_S2R_REPARTITION. Les écarts transitoires sont journalisés.
5. Transmettre RAM:M19_S2R_RUNTIME.TXT, refaire une relance sans reset si PASS et enregistrer le second journal hors RAM: sous un nom distinct.

## Gate C — vrai AMOS Compiler (1/1 PASS)

Même ASC et ABK ; compiler un nouvel exécutable avec la Lib S2r exacte, PRG_STATE=-1, mêmes observations. RAM:M19_S2R_COMPILED.TXT. Pas de Gate C par simulation.

ERR 10=Show, 11=Change, 12=Move, 13=Off, 14=mémoire, 15=re-show, 16=saturation, 17=banque 30 occupée, 18=Fill, 19=Capture, 20=Info, 21=refus, 22=Draw, 23=Erase, 24=Swap. Relever code API exact. Aucun changement de contrat Sprite (16 px, 3 couleurs opaques, 3 objets simultanés). Pas de Gate D.

[Rapport S2r](../../docs/M19_S2R_REPARTITION_2026-11-27.md) · [S2b historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/502739db328178d7abd47e8bc247a7c54d453139/tests/current/README.md).
