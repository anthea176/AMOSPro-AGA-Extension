# 0.15.0-alpha.2 — S2e : hotspots des sprites (campagne active)

**28/11/2026 — S2e 0.15.0-alpha.2 Gate B Runtime PASS, contrôle visuel confirmé par l'auteur (« oui »).** Journal `M19_S2E_RUNTIME.TXT`, PRG_STATE=1, RESULT=1 ERR=0 CLEAN_ERR=0, PASS_S2E_HOTSPOT. 9 Open/Close, 36 Show, 324 Change et 324 Move, 9 Off, 27 retraits auto, 18 refus géométriques -128, 9 conflits de largeur -206, 9 saturations -206, 18 AGAPIC et 18 AGSP, 9 refus de 16 opaques. Chip/Fast pertes et dérives nulles, 6840 octets Fast temporaires récupérés. C réelle différée, D et PRG_STATE=0 non testées. SHA installé, relance indépendante et mesures FPS non attestés. CI post-activation : [intégrité](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46157670125), [CPU/chemins](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46157670278), [reconstruction/campagne](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46157669956), [hotspots natifs](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46157670245) PASS ; [régressions historiques S2e](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46157669967) post-activation PASS (relevé du 28/11/2026). Active et LAST_GOOD inchangées. [Rapport](../../docs/M19_S2E_RUNTIME_2026-11-28.md).

**28/11/2026 — 0.15.0-alpha.2 S2e candidate de TEST active, autorisation auteur « ggo go », reprise « ok next ».** [Gate A native PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46134733533) et [régressions exactes PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46135040114) : 2840 géométries, 186 cas publics par layout, 576 Change et 576 Move à hotspot zéro par layout, 93 négatifs et 51 cycles par layout, 232 captures larges, AGAPIC 392, Pattern 184, SafePort 172, Bob 10 suites, DB/IFF/Swap. [Double reconstruction et livraison exacte PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46157121705), [politique CPU/chemins PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46157121717). Lib 160352 octets SHA256 `3135ba3973b138ec44a07ade3e190baba12a9425746252aaf88853b00d4ae7d3`, blob `6206d425dc787d9a1460bf0e7f85d2e7579c9037` ; ASC 17604 octets SHA256 `b11f05a88a311cce82da5eb10962133e0c703fcd18fef20fcb592ddfa294be84`, blob `38b69e5fdab38e8abde89b0d9ec9fa43dd1aba8e` ; ABK AGSP_HOTSPOT_TEST.ABK 6836 octets SHA256 `df3b9af963c65ada0d294708761f9990e240aa771e58b53bf8840d8c98d15d8a`, blob `fcc7f978aa73ae755d8028905f8e4a84c001214e`. MC68020+, 105 commandes/219 AP20, UNIT142 65062 (472 libres), UNIT213 18028 (47506 libres), PC16 3658 avec réserve 16384. Source native qualifiée inchangée ; seul raccord de provenance/livraison adapté. AGSP v1 inchangé, coordonnées logiques X/Y moins hotspot signé par image, registre v7 624o/records 172o, rejet des rectangles partiels et des débordements ; aucun token ni setter public. S2d historique préservée dans Git `fc16c5a49546aeffddb0d342842743d15e58cd38`, ancienne ABK et LAST_GOOD L2b strictement inchangées. À la bascule, B/C/D réelles S2e non testées ; voir résultat daté ci-dessus (historique). Aucune promotion, archive, autre branche, tag ni release.

## Fichiers à utiliser ensemble

| Fichier | Octets | SHA256 |
| --- | ---: | --- |
| [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib) | 160352 | `3135ba3973b138ec44a07ade3e190baba12a9425746252aaf88853b00d4ae7d3` |
| [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc) | 17604 | `b11f05a88a311cce82da5eb10962133e0c703fcd18fef20fcb592ddfa294be84` |
| [AGSP_HOTSPOT_TEST.ABK](AGSP_HOTSPOT_TEST.ABK) | 6836 | `df3b9af963c65ada0d294708761f9990e240aa771e58b53bf8840d8c98d15d8a` |

Installer la Lib dans APSystem, même slot d'extension. Vérifier le SHA installé, redémarrer complètement WinUAE sans Save State. AGA PAL, 68030, JIT ON ; graphics.library V39/40 dans le périmètre du code. ASC et ABK dans le même dossier, banques 29 et 30 libres. Project > Merge ASCII dans un programme vierge. Ne pas réutiliser un ancien exécutable.

## Gate B — Runtime (PRG_STATE=1)

Neuf écrans : 16, 32 puis 64 pixels ; pour chaque largeur, trois simples, mixte, trois attachés. Les 24 images héritées de S2d alternent hotspots (largeur/2,8) et (-3,-4). Les deux premières frames ont la même ancre logique X=32 avec pause visible ; vérifier le décalage conforme au hotspot de la frame, le contraste, les déplacements, la transparence et l'absence de traînées. Origine affichée = ancre logique - hotspot signé ; le rectangle doit rester entièrement dans 320x256. Vérifier également la restauration du curseur.

Résultat attendu : OPENED=CLOSED=9, SHOWN=36, CHANGED=MOVED=324, OFF_COUNT=9, AUTO_CLOSE=27, SATURATION=9, FULL_RC=-206, WIDTH_REFUSED=9, WIDTH_RC=-206 ; HOT_REFUSED=18, HOT_RC=-128, HOT_CHANGE_RC=-128 ; AGAPIC_CAPTURE/META/NEGATIVE/DRAW=18, AGSP_CAPTURED=18, REFUSED=9, FREE_RC=1, OWN=0. RESULT=1 ERR=0 CLEAN_ERR=0 ; VERDICT PASS_S2E_HOTSPOT. Aucune perte nette Chip/Fast ni dérive mémoire après réchauffement du cache. Conserver le journal complet RAM:M19_S2E_RUNTIME.TXT, même en cas d'échec ; sauvegarder hors RAM: avant nouvelle exécution.

## Gate C — vrai AMOS Compiler (PRG_STATE=-1)

**Compiler différé par l'auteur.** Aucun essai Compiler demandé maintenant. Lors de sa reprise, construire un nouvel exécutable avec la Lib, ASC et ABK exacts de cette campagne. RAM:M19_S2E_COMPILED.TXT ; interprété PRG_STATE=0 : RAM:M19_S2E_INTERPRETED.TXT. Gate D matérielle distincte.

## Diagnostic

ERR 31=refus Move hotspot attendu ; ERR 32=refus Change hotspot attendu. Les autres codes hérités de S2d sont documentés dans le [README historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/fc16c5a49546aeffddb0d342842743d15e58cd38/tests/current/README.md). Transmettre le code exact, la largeur/mix et tout Guru. Aucun clipping ni setter public de hotspot dans cette candidate. Aucune promotion de LAST_GOOD.

[Rapport S2e](../../docs/M19_S2E_HOTSPOT_0_15_0.md) · [Preuve Runtime S2d](../../docs/M19_S2D_RUNTIME_2026-11-28.md).
