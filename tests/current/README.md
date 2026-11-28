# 0.15.0-alpha.1 — S2d-P3e : sprites larges (campagne active)

**28/11/2026 — 0.15.0-alpha.1 (M19 S2d-P3e) candidate de TEST active sur main, autorisation auteur « ok go go ».** [Gate A intégrée PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46131159222) : 576 Change + 576 Move, 93 négatifs et 51 cycles de vie dans chacun des deux modèles AP20 ; 116 captures larges par modèle, chaîne DB/IFF/Swap/Capture et double reconstruction PASS. [Régressions historiques PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46131265679) : AGAPIC 392, Pattern 184, SafePort 172, Bob 10. [Préparation exacte et preflight strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46131720387). Lib 160148 octets SHA256 `a216a0e9f19233cb867e4a22cb6e7af5342e9863538baad5268c95010247ebef`, blob `5f3c72b68c3b6b424d173a989eecf757f13f1c01` ; ASC 16576 octets SHA256 `520c1a8a4c964b288fc76a337b5a6389e33d28340a98a8b21b342abaddaa1a29`, blob `994f74916ec774b43b69688dce5401d26dd647d1` ; ABK 6836 octets SHA256 `f8816b944102c5826f9819b84747acd61fd4468423bf815c25e128a9dcfe4e64`, blob `0f3decda5863337c5a1f95fe1844a95df4d34823`. MC68020+, 105 commandes/219 AP20, UNIT142 65062 (472 libres), UNIT213 17822 (47712 libres), PC16 3658 avec réserve 16384. Code natif identique à e0c5a75, seul raccord de provenance/livraison adapté. S2c-E1 conservée dans Git `caf0b6ba768328f78d3a148f54dfecc760ea1d8c` ; LAST_GOOD L2b et anciennes ABK inchangées. Gates B/C/D réelles NON TESTÉES ; graphics.library V39/40 modélisées, largeur commune 16/32/64 par contexte actif, trois paires. Aucun tag, release, promotion, autre branche ou dépôt. CI post-activation à relever.

## Fichiers à utiliser ensemble

| Fichier | Octets | SHA256 |
| --- | ---: | --- |
| [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib) | 160148 | `a216a0e9f19233cb867e4a22cb6e7af5342e9863538baad5268c95010247ebef` |
| [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc) | 16576 | `520c1a8a4c964b288fc76a337b5a6389e33d28340a98a8b21b342abaddaa1a29` |
| [AGSP_WIDE_TEST.ABK](AGSP_WIDE_TEST.ABK) | 6836 | `f8816b944102c5826f9819b84747acd61fd4468423bf815c25e128a9dcfe4e64` |

Installer la Lib dans APSystem, même slot d'extension. Vérifier le SHA installé, redémarrer complètement WinUAE sans Save State. AGA PAL, 68030, JIT ON ; graphics.library V39/40 dans le périmètre du code. ASC et ABK dans le même dossier, banques 29 et 30 libres. Project > Merge ASCII dans un programme vierge. Ne pas réutiliser un ancien exécutable.

## Gate B — Runtime (PRG_STATE=1)

Neuf écrans : 16, 32 puis 64 pixels ; pour chaque largeur, trois simples, mixte, trois attachés. Observer le contraste et les repères aux frontières de 16 pixels, les deux frames, les déplacements, la transparence, l'absence de traînées et la restauration du curseur. Les 3 familles simples utilisent les pens 21..23, 25..27, 29..31 ; attaché 17..31. Les largeurs différentes sont refusées lorsque des objets restent actifs.

Résultat attendu : OPENED=CLOSED=9, SHOWN=36, CHANGED=MOVED=324, OFF_COUNT=9, AUTO_CLOSE=27, SATURATION=9, FULL_RC=-206, WIDTH_REFUSED=9, WIDTH_RC=-206 ; AGAPIC_CAPTURE/META/NEGATIVE/DRAW=18, AGSP_CAPTURED=18, REFUSED=9, FREE_RC=1, OWN=0. RESULT=1 ERR=0 CLEAN_ERR=0 ; VERDICT PASS_S2D_WIDE. Aucune perte nette Chip/Fast ni dérive mémoire après réchauffement du cache d'animation (premier changement). Conserver et transmettre le journal complet RAM:M19_S2D_RUNTIME.TXT, même si échec ; sauvegarder hors RAM: avant une relance indépendante sans reset.

## Gate C — vrai AMOS Compiler (PRG_STATE=-1)

Après Runtime PASS, construire un nouvel exécutable avec la même Lib, ASC et ABK. Même critères ; RAM:M19_S2D_COMPILED.TXT. Interprété PRG_STATE=0 : RAM:M19_S2D_INTERPRETED.TXT. Aucun modèle CI ne remplace les essais réels.

## Diagnostic

ERR 10=Show, 11=Change, 12=Move, 13=Off, 14=mémoire, 15=re-show, 16=saturation, 17=banque 30 occupée, 18=Fill, 19=AGAPIC Capture, 20=Info, 21=refus, 22=Draw, 23=Erase, 24=Swap, 25=motif capture AGSP, 26=banque AGSP, 27=capture 1 ligne, 28=capture 16 lignes, 29=refus 16 opaques, 30=conflit largeur. CLEAN_ERR bit64=nettoyage capture AGSP. Les retours courts Sprite incluent -206 (capacité/largeur/palette), -208 (acquisition), -209 (échange/déplacement). Transmettre le code exact et la largeur/mix en cas de refus ou de Guru. Pas de promesse de performance ; deux WaitTOF par échange, trois objets maximum, même largeur des objets actifs, même hauteur/profondeur/palette par objet ; retrait complet avant changement de largeur. Aucun test matériel Gate D.

[Rapport](../../docs/M19_S2D_WIDE_SPRITES_0_15_0.md) · [S2c historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/caf0b6ba768328f78d3a148f54dfecc760ea1d8c/tests/current/README.md).
