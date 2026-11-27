# S2a-P1 — changement d'image à chaud, campagne active unique

**27/11/2026 — S2a-P1 clôturée fonctionnellement.** Gate A complète PASS, CI post-activation 39 PASS / 1 skipped / 0 échec, B Runtime 2/2 et C vrai Compiler 1/1 PASS stricts, 300 changements, 300 déplacements, six fermetures, zéro perte nette ou temporaire mesurée ; animation confirmée par l'auteur (« oui lanimation est ok on peux continuer »). D non testée. S2b engagé, S2a reste active et LAST_GOOD L2b protégée. [Résultats et journaux](../../docs/M19_S2A_RUNTIME_COMPILER_2026-11-27.md). [S2b](../../docs/M19_S2B_MULTI_SPRITE_2026-11-27.md).

Campagne déjà exécutée ; ne pas répéter sans anomalie nouvelle.

**27/11/2026 — S2a-P1 active sur main, autorisation auteur « ol continu jusqua la lib ».** [Gate A complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45907171922), commit source `91a4acf89f511420ba0a87515ec2a85b6d124277` : 10 jobs réussis, 400 changements d'image et négatifs, 200 cycles/20 fermetures P2m hérités, DB/IFF/Swap/capture, 184 Pattern, 172 SafePort, 10 suites Bob, reconstruction exacte et préflight strict PASS. Lib 151164 octets SHA256 `1d13ff815aa3b448e420f6783dbac967c03efca2fbb65932e783ec72502e58d2` blob `190504fd46494224c6c32e20f17dcc3d6a027684`; ASC 7265 octets SHA256 `d191282714b43d38b07585fa1054895885f8b2d1be403abcfd9f5f76d993ebdb` blob `ac74e8773a86914a00f3a153487afe61a9803efc`; nouvelle banque de campagne AGSP_S2A_ANIMATION.ABK 372 octets SHA256 `4b13eb9ac278ad56a73c043327a11d48a3d79d65807563409d94e64aa16d50aa` blob `210179c9328e1ff032070b2dd40ffa8849e8294a`. 105 commandes / 214 AP20, MC68020+, UNIT142 65424 (110 libres) inchangée, UNIT207 12142, PC16 max 12172, marge 20592. Uniquement UNIT207 et titre changés depuis P2m. Aucun changement LAST_GOOD L2b, ancien ABK ou archive, aucun autre dépôt, branche, promotion ou release. B/C/D S2a non testées. L'ancien P2m reste dans Git.

## Fichiers à utiliser ensemble

- [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib), 151164 octets, SHA256 `1d13ff815aa3b448e420f6783dbac967c03efca2fbb65932e783ec72502e58d2`.
- [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc), 7265 octets, SHA256 `d191282714b43d38b07585fa1054895885f8b2d1be403abcfd9f5f76d993ebdb`.
- [AGSP_S2A_ANIMATION.ABK](AGSP_S2A_ANIMATION.ABK), 372 octets, SHA256 `4b13eb9ac278ad56a73c043327a11d48a3d79d65807563409d94e64aa16d50aa`. Deux images 3/4, 16×16, palette identique, banque 29.
- L'ancien AGSP_S1P1E_FINAL.ABK est conservé sans modification pour reconstruire P2m ; ne pas l'utiliser pour ce test.

## Gate B — WinUAE Runtime

1. WinUAE AGA PAL, 68030 JIT ON. Installer la Lib dans APSystem, même slot, redémarrage complet unique, pas de Save State.
2. ASC et nouvelle ABK dans le même dossier. Project > Merge ASCII, programme vierge. Banque 29 libre. Lancer en Runtime (PRG_STATE=1).
3. Observer le déplacement des deux images alternées sur le fond sombre, sans disparition volontaire entre les frames. 100 changements, 2 ouvertures et fermetures avec Sprite actif ; un Off/réaffichage volontaire entre campagnes. Vérifier le retour à AMOS.
4. Attendu : CHANGED=100 CHANGE_RC=1, SHOWN=3 MOVED=100 OFF_COUNT=1 AUTO_CLOSE=2, OPENED=CLOSED=2, SPRITE_RC=MOVE_RC=OFF_RC=FREE_RC=1. CHIP_SCREEN_LOSS=FAST_SCREEN_LOSS=0, CHIP_BEFORE=CHIP_AFTER, FAST_BEFORE=FAST_AFTER, RESULT=1 ERR=0 CLEAN_ERR=0, VERDICT PASS_S2A_FRAME_CHANGE. Les écarts transitoires sont consignés séparément.
5. Transmettre RAM:M19_S2A_RUNTIME.TXT. Si PASS, refaire un lancement sans reset pour confirmer la réutilisation. Sauvegarder chaque journal hors RAM: si possible.

## Gate C — vrai Compiler

Même ASC et ABK, compiler un nouvel exécutable avec la Lib exacte, lancer dans les mêmes conditions, PRG_STATE=-1. Journal RAM:M19_S2A_COMPILED.TXT. Ne pas transférer un PASS du modèle AP20 de CI vers la Gate C réelle.

Si un refus : ERR=11 indique changement d'image ; relever CHANGE_RC, -200 à -205 (voir [rapport](../../docs/M19_S2A_PUBLIC_FRAME_CHANGE_2026-11-26.md)). Les deux frames doivent rester distinctes visuellement et la fermeture revenir à AMOS. Deux WaitTOF par changement, largeur 16, hauteur/palette identiques, et refus d'une transition traversant 64 Kio. Pas de preuve DMA physique ; Gate D distincte.

[Ancienne campagne P2m conservée dans Git](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/57a1a9d2085e5d887a1fccc5300a0de5eaeef709/tests/current/README.md).
