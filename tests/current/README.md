# 0.15.0-alpha.4 — S2g-P1b : priorités des sprites

**28/11/2026 — S2g-P1b 0.15.0-alpha.4 candidate de TEST active sur `main`**, bascule conjointe Lib/ASC autorisée par l'auteur (« go jsuqu a la lib », puis « go » et « next »). Gate A composée PASS : les dix suites fonctionnelles de la [CI initiale](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46171737275) sont PASS sur la même identité publique (1662 contrôles de priorité et 426 cas clipping + 90 refus par layout Runtime/Compiler, capture, AGAPIC, Pattern, SafePort, Bob, chaînage). Le job link initial avait échoué sur le choix de la fixture historique, pas sur les octets de la Lib ; le [link corrigé et contrôle final](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46173679331) sont PASS, double reconstruction, préflight strict et vérification exacte Lib/ASC/ABK. Le rerun intégré [46173679354](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46173679354) reste complémentaire, pas déclaré complet. Lib **162432o**, SHA256 `7c68fb4ba1f903fe11a0c079b37d4f8d54a5a8dcc8bce96b6de4c791b5be9e1d`, blob `e657167548082be034834130fdb188c42f37f595` ; ASC **25332o**, SHA256 `2a79bf1a996eafd25b3a3b027c2eb1aac7830a339681b8597fdfa687ce8be5aa`, blob `47db0fa032e487e525d40bfd3f584a8e879bb7b4` ; AGSP_HOTSPOT_TEST.ABK 6836o SHA256 `df3b9af963c65ada0d294708761f9990e240aa771e58b53bf8840d8c98d15d8a` inchangée. Les 128 blocs de reçu ont été recomposés et leurs trois SHA256 recalculés ; Git a retourné les deux blobs attendus. MC68020+, 105 noms / 106 signatures / 221 AP20 ; UNIT142=65062o (472 libres), UNIT215=20074o (45460 libres bruts), PC16 max 3658 avec réserve 16384o ; registre v8 672o/188o. Surcharge 4/5 arguments, couche 0 auto, 1/2/3 paires 2/3, 4/5, 6/7 ; -210 rang invalide, -206 indisponible/incompatible/migration. Aucun changement de priorité playfield (P2 hors périmètre). **Re-Merge ASCII obligatoire : offsets de tokens modifiés. B/C/D réelles non testées**, contrôle visuel et journal S2g à obtenir ; Compiler réel à qualifier séparément. S2f B Runtime/visuel PASS reste historique. LAST_GOOD L2b, banque, tests passés et archives protégés ; aucune promotion ni release, aucune autre branche. CI post-activation à relever.

## Fichiers à utiliser ensemble

| Fichier | Octets | SHA256 |
| --- | ---: | --- |
| [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib) | 162432 | `7c68fb4ba1f903fe11a0c079b37d4f8d54a5a8dcc8bce96b6de4c791b5be9e1d` |
| [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc) | 25332 | `2a79bf1a996eafd25b3a3b027c2eb1aac7830a339681b8597fdfa687ce8be5aa` |
| [AGSP_HOTSPOT_TEST.ABK](AGSP_HOTSPOT_TEST.ABK) | 6836 | `df3b9af963c65ada0d294708761f9990e240aa771e58b53bf8840d8c98d15d8a` |

Installer la Lib dans APSystem, même slot. Vérifier SHA installé, redémarrer complètement WinUAE sans Save State. AGA PAL, 68030, JIT ON ; graphics.library V39/40. ASC et ABK dans le même dossier, banques 29 et 30 libres. Project > Merge ASCII dans un programme vierge. **Ne pas réutiliser un ancien .AMOS tokenisé ou un ancien exécutable : offsets de tokens modifiés.**

## Gate B — Runtime (PRG_STATE=1)

Neuf écrans : 16/32/64 pixels, simples, mixtes, attachés. Les trois objets logiques 17/42/64 sont créés dans l'ordre inverse 3, 2, 1, puis se recouvrent pendant 100 VBL. Vérifier dans la zone de superposition opaque : couche 1 devant 2, couche 2 devant 3, même si 3 a été créée en premier. Les refus de migration et de couche occupée ne doivent pas déplacer les objets ni altérer les voisins. Le rang -1/4 et la palette incompatible sont testés avant création. Ensuite la boucle d'animation héritée S2e, puis 4 bords, 4 coins, 4 positions totalement extérieures, retour entièrement visible pour chacun des trois objets, échange de frame avec hotspot négatif puis retour. Nouveau Show partiellement visible à droite. Sur le dernier écran, Erase 29 lorsque trois sprites sont encore actifs : chacun doit pouvoir se déplacer partiellement, disparaître et revenir sans sa banque d'origine. Vérifier visuellement que les pixels visibles sont ceux de l'image originale, aucune traînée, corruption, wrapping ou changement de couleur ; restitution du curseur et retour AMOS.

| Champ | Attendu |
| --- | ---: |
| LAYER_SHOW / LAYER_MOVE / BAD | 27 / 27 / 18 |
| LAYER_PALETTE / MIGRATION / BUSY / RC | 9 / 27 / 27 / -206 |
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

Attendre `VERDICT PASS_S2G_PRIORITY`, Chip/Fast avant et après identiques. Ne pas imposer la valeur transitoire Fast de S2e : la nouvelle taille du registre et les caches sont différents. Aucun benchmark dans ce test.

Conserver le journal complet `RAM:M19_S2G_RUNTIME.TXT`, même en cas d'échec, hors RAM: avant un nouvel essai.

## Diagnostics / Gates restantes

ERR 38 : rang invalide ; 39 : palette incompatible ; 40 : Move explicite ; 41 : migration refusée attendue ; 42 : couche occupée ; 43 : compteurs de priorité. ERR 31 : Move clip ou extérieur ; 32 : échange de frame ; 33 : overflow ; 34 : restauration Show ; 35 : Erase ; 36 : Move après Erase ; 37 : compteurs. Autres diagnostics hérités : [README S2e historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/65f0cce933d7bcf471378231a2a29d5e81580388/tests/current/README.md). Transmettre le journal, la largeur/mix, tout Guru et observation de rendu. **Compiler réel C non testé (à qualifier séparément pour la surcharge)** ; journal `RAM:M19_S2G_COMPILED.TXT`. Interprété PRG_STATE=0 : `RAM:M19_S2G_INTERPRETED.TXT`. D matérielle séparée. Pas de promotion LAST_GOOD.

[Contrat S2g](../../docs/M19_S2G_PRIORITY_0_15_0.md) · [Gate A composée](../../docs/M19_S2G_P1B_GATE_A_2026-11-28.md) · [S2f historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/ef8cd7c175d97f73fc058dd6d16b43da1acd0103/tests/current/README.md) · [Contrat S2f](../../docs/M19_S2F_CLIPPING_0_15_0.md) · [Résultat Runtime S2e](../../docs/M19_S2E_RUNTIME_2026-11-28.md).
