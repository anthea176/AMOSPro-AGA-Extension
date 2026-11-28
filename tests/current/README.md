# 0.15.0-alpha.3 — S2f : clipping des sprites

**28/11/2026 — S2f 0.15.0-alpha.3 candidate de TEST active sur `main`, bascule autorisée par l'auteur « go » / « ok go ».** [Gate A P2b complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46163164542), 11 suites et contrôle final : 426 cas publics et 90 refus par layout, 576 Move et 576 Change à hotspot nul, 87 refus et 51 cycles par layout, captures AGSP, AGAPIC, Pattern, SafePort, Bobs et chaînage. Dernière suite [zero-runtime PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46163164542/job/141034782528) à 16:33:57 UTC. Préflight strict PASS. Bascule conjointe Lib/ASC, ABK identique ; CI post-activation à relever. [Préparation binaire PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46163387336) : Lib 162288 octets SHA256 `6efdc6f17897de69fb7f292e131cbb31bd55626dea0566d77555f1d7f7073e66`, blob `d58c985692d88b08df2d55b690b43ed47b087b13` ; ASC 22943 octets SHA256 `96c9c526f3e37d5e11d023b7ee8681e6114dc0e22f5aff1c8aaf6ff05590bb48`, blob `ece785049b2c82ad00e44455f84d7f7cbfb639af` ; AGSP_HOTSPOT_TEST.ABK 6836 octets SHA256 `df3b9af963c65ada0d294708761f9990e240aa771e58b53bf8840d8c98d15d8a`, blob `fcc7f978aa73ae755d8028905f8e4a84c001214e` inchangé. MC68020+, 105 commandes/219 AP20, UNIT142 65062 (472 libres), UNIT213 19964 (45570 libres), PC16 3658 avec réserve 16384. Registre privé v8 672o/records 188o. Les sources natives qualifiées restent inchangées. S2e Runtime et visuel PASS, historique exact au commit `65f0cce933d7bcf471378231a2a29d5e81580388`. B/C/D réelles S2f non testées, C réelle différée. LAST_GOOD L2b protégée, aucune archive, autre branche, promotion, tag ni release.

## Fichiers à utiliser ensemble

| Fichier | Octets | SHA256 |
| --- | ---: | --- |
| [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib) | 162288 | `6efdc6f17897de69fb7f292e131cbb31bd55626dea0566d77555f1d7f7073e66` |
| [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc) | 22943 | `96c9c526f3e37d5e11d023b7ee8681e6114dc0e22f5aff1c8aaf6ff05590bb48` |
| [AGSP_HOTSPOT_TEST.ABK](AGSP_HOTSPOT_TEST.ABK) | 6836 | `df3b9af963c65ada0d294708761f9990e240aa771e58b53bf8840d8c98d15d8a` |

Installer la Lib dans APSystem, même slot. Vérifier SHA installé, redémarrer complètement WinUAE sans Save State. AGA PAL, 68030, JIT ON ; graphics.library V39/40. ASC et ABK dans le même dossier, banques 29 et 30 libres. Project > Merge ASCII dans un programme vierge. Ne pas réutiliser un ancien exécutable.

## Gate B — Runtime (PRG_STATE=1)

Neuf écrans : 16/32/64 pixels, simples, mixtes, attachés. D'abord la boucle d'animation héritée S2e, puis 4 bords, 4 coins, 4 positions totalement extérieures, retour entièrement visible pour chacun des trois objets, échange de frame avec hotspot négatif puis retour. Nouveau Show partiellement visible à droite. Sur le dernier écran, Erase 29 lorsque trois sprites sont encore actifs : chacun doit pouvoir se déplacer partiellement, disparaître et revenir sans sa banque d'origine. Vérifier visuellement que les pixels visibles sont ceux de l'image originale, aucune traînée, corruption, wrapping ou changement de couleur ; restitution du curseur et retour AMOS.

| Champ | Attendu |
| --- | ---: |
| OPENED / CLOSED | 9 / 9 |
| SHOWN / CHANGED / MOVED | 36 / 324 / 324 |
| CLIPPED / OUTSIDE / RESTORED | 216 / 108 / 27 |
| CLIP_CHANGE / CLIP_SHOW / ERASE_MOVES | 54 / 9 / 9 |
| OVERFLOW / OVERFLOW_RC | 9 / -128 |
| SATURATION / FULL_RC | 9 / -206 |
| WIDTH_REFUSED / WIDTH_RC | 9 / -206 |
| OFF_COUNT / AUTO_CLOSE | 9 / 27 |
| AGAPIC_CAPTURE / META / NEGATIVE / DRAW | 18 chacun |
| AGSP_CAPTURED / REFUSED | 18 / 9 |
| FREE_RC / OWN / BANK_OWN | 1 / 0 / 0 |
| CHIP_CYCLE_LOSS / FAST_CYCLE_LOSS | 0 / 0 |
| CHIP_SCREEN_LOSS / FAST_SCREEN_LOSS | 0 / 0 |
| RESULT / ERR / CLEAN_ERR | 1 / 0 / 0 |

Attendre `VERDICT PASS_S2F_CLIPPING`, Chip/Fast avant et après identiques. Ne pas imposer la valeur transitoire Fast de S2e : la nouvelle taille du registre et les caches sont différents. Aucun benchmark dans ce test.

Conserver le journal complet `RAM:M19_S2F_RUNTIME.TXT`, même en cas d'échec, hors RAM: avant un nouvel essai.

## Diagnostics / Gates restantes

ERR 31 : Move clip ou extérieur ; 32 : échange de frame ; 33 : overflow ; 34 : restauration Show ; 35 : Erase ; 36 : Move après Erase ; 37 : compteurs. Autres diagnostics hérités : [README S2e historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/65f0cce933d7bcf471378231a2a29d5e81580388/tests/current/README.md). Transmettre le journal, la largeur/mix, tout Guru et observation de rendu. **Compiler réel C différé** ; journal futur `RAM:M19_S2F_COMPILED.TXT`. Interprété PRG_STATE=0 : `RAM:M19_S2F_INTERPRETED.TXT`. D matérielle séparée. Pas de promotion LAST_GOOD.

[Contrat S2f](../../docs/M19_S2F_CLIPPING_0_15_0.md) · [Résultat Runtime S2e](../../docs/M19_S2E_RUNTIME_2026-11-28.md).
