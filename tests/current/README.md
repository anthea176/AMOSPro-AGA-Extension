# S2b-P1 — trois Sprites indépendants, campagne active unique

**27/11/2026 — S2b-P1 candidate active, autorisation auteur « ok go ».** [Gate A intégrée PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46041721740), source `f49a027ce466b4968c60db0dab901b53751aecd2` : 1200 changements d'image, 600 cycles Show/Off, 20 fermetures collectives et négatifs dans deux modèles AP20 ; chain DB/IFF/Swap/capture, 184 Pattern, 172 SafePort, 10 suites Bob ; 7 jobs PASS. [Reconstruction et préflight ASC strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46042040810). Lib 152876 octets SHA256 `b44edbbcf4b3c02cb6527ea0f002bee863c992dd4b670636e7431a1b69e1a2fa` blob `6a9493b69c5fa64a0cb167722423cfee7f18bbb3` ; ASC 8954 octets SHA256 `2cda351432ba495589c4848ef8c2d640426e18c6e71287d643a506e2e21acde0` blob `2d1737f64cff84a24ff7551386abd672dc59b738` ; nouvelle ABK 1012 octets SHA256 `eb0060bce79d15785d5d6f6caf31f8819adfd518b0e179dca5feb025b80b2c78` blob `c122c79976bce5afad051f487d77af8cc296f2cc`. UNIT142 65524 (10 libres), UNIT207 13756 (18978 libres PC16), PC16 max 13786, 105 commandes/214 AP20, MC68020+. B/C/D réelles non testées. Anciennes ABK et LAST_GOOD L2b inchangées. S2a A/B/C validée dans Git ; aucun changement de release ou branche.

## Fichiers à utiliser ensemble

- [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib), 152876 octets.
- [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc), 8954 octets.
- [AGSP_S2B_MULTI.ABK](AGSP_S2B_MULTI.ABK), 1012 octets, banque 29. Images 3/4, 5/6, 7/8, 16×16 ; trois palettes RGB24. Les anciennes ABK restent intactes pour les reconstructions historiques.

## Gate B — WinUAE Runtime

1. WinUAE AGA PAL, 68030 JIT ON, même configuration S2a. Installer la Lib exacte dans APSystem dans le même slot. Redémarrage complet une seule fois (registry v4 incompatible v3), sans Save State.
2. ASC et AGSP_S2B_MULTI.ABK dans le même dossier, Project > Merge ASCII, programme vierge, banque 29 libre. Runtime PRG_STATE=1.
3. Observer trois Sprites distincts (paires 2/3, 4/5, 6/7), trois groupes de couleurs, mouvements opposés au milieu, alternances de frames. Aucun Off entre les changements. Le quatrième Sprite est refusé, le Sprite central seul disparaît puis réapparaît sous ID 9. Les deux autres doivent rester visibles. Close actif, deuxième écran et retour à AMOS.
4. Attendu : OPENED=CLOSED=2, CHANGED=MOVED=300, SHOWN=8, OFF_COUNT=2, AUTO_CLOSE=6 (nombre d'objets actifs au Close), SATURATION=2 FULL_RC=-206, SPRITE_RC=CHANGE_RC=MOVE_RC=OFF_RC=FREE_RC=1. CHIP_SCREEN_LOSS=FAST_SCREEN_LOSS=0, CHIP_BEFORE=CHIP_AFTER, FAST_BEFORE=FAST_AFTER, RESULT=1 ERR=0 CLEAN_ERR=0, VERDICT PASS_S2B_MULTI_SPRITE. Les écarts transitoires sont journalisés séparément.
5. Transmettre RAM:M19_S2B_RUNTIME.TXT, refaire un lancement sans reset si PASS. Enregistrer les journaux hors RAM: si possible.

## Gate C — vrai Compiler

Même ASC et ABK, nouveau programme compilé avec cette Lib ; PRG_STATE=-1. RAM:M19_S2B_COMPILED.TXT. Vérification visuelle et mémoire identiques. Les modèles AP20 de Gate A ne sont pas le Compiler réel.

ERR 10=Show, 11=Change, 12=Move, 13=Off, 14=mémoire, 15=re-show, 16=saturation. Relever code API exact. -206 capacité/conflit/pending, -207 insertion refusée. Deux WaitTOF par changement d'image, largeur 16 et hauteur/palette constantes par objet, refus transition traversant 64 Kio. Pas de promesse de fluidité maximale à ce stade ; D physique non testée.

[Rapport S2b](../../docs/M19_S2B_MULTI_SPRITE_2026-11-27.md) · [S2a historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/4719388fbc67e80a12973e686937d0cda1c12553/tests/current/README.md).
