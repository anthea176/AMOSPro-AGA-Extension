# Audit P2d — passage 6 : CBlock, C2P, Copper, polices et Close

**24 novembre 2026** · Dépôt `anthea176/AMOSPro-AGA-Extension` · **`main` uniquement** · sources examinées au HEAD figé `74ab87df0a6e4fda8804fd74f541afc310c713f7`.

**Périmètre strict de cette passe : lecture du source MC68020 lié et des contrats archivant sa conception. Aucun assemblage, test Gate A, WinUAE Gate B, AMOS Compiler Gate C, changement de code, banque, ASC ou Lib. Le chantier Sprite S1-P1e reste GELÉ.** La référence est la LAST_GOOD P2d : 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 tokens.

## 1. CBlock : trois entrées AP20, même garde Safe locale

Le [master AP20 P2d](AUDIT_AGA_AP20_LIAISONS_P2D_2026-11-24.md) pointe sans ambiguïté vers :

| Commande | AP20 | Cible native | Preuve d'acquisition Safe |
|---|---:|---|---|
| `Aga C Block Capture` | 125 | UNIT142+$0A476 | [fin du wrapper capture](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT142_BLOCK_0A71A_MC68020.s#L258-L297) : `DB+20 & 1` puis `GetMsg(-372)` ; si absent, branche d'échec avant `WaitBlit` et `jsr CORE_$0ABCE` |
| `Aga C Block Draw` | 127 | UNIT142+$0AF3A | [fin du wrapper draw](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT142_BLOCK_0B0A6_MC68020.s#L283-L325) : même garde, `WaitBlit(-228)`, puis `jsr CORE_$0B592` |
| `Aga C Block Restore` | 129 | UNIT142+$0B8FE | [fin du wrapper restore](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT142_BLOCK_0BA5E_MC68020.s#L287-L329) : même garde, `WaitBlit(-228)`, puis `jsr CORE_$0BF5A` |

Les trois [cœurs natifs CBlock, mode CPU8/CPU16/Blitter](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT142_CBLOCK_CORE_0ABCE_MC68020.s#L1-L20) sont de vrais blocs `INCLUDE` du [master UNIT142 P2d](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_P2D_UNIT142_EDITABLE.s#L281-L313) et non une simple référence à un script historique. Le cœur Blitter attend lui-même `WaitBlit` avant son retour lorsqu'il utilise le DMA.

**Détail important :** pour Capture, les dimensions et pointeurs Chip du CBlock sont prévalidés avant GetMsg, mais l'écriture du pixel dans le CBlock et la publication des coordonnées de dernière capture se trouvent **après** l'acquisition Safe (publication `16(a0)/20(a0)` en fin de succès). Il ne faut donc pas déclarer une corruption de banque sur simple refus Safe sans démontrer une modification réelle : **le chemin nominal refuse d'abord la copie**. Il reste à tester refus après allocation, états de banque et snapshot B8 par T13.

**Statut :** garde Safe **confirmée statiquement** dans les trois wrappers ; pixels, allocation, ressaisies bank et coordination B8 **NON VALIDÉS sous Gate B/C de cette nouvelle campagne**.

## 2. C2P : Safe avant DMA ; Close libère après synchronisation

- `Aga C2P Convert` → entrée AP20 **146**, UNIT153+$00372. Le [préflight MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT153_PUBLIC_PREFLIGHT_MC68020.s#L6-L67) vérifie notamment le contexte d'écran **320 × 256**, profondeur **4 à 8 plans**, contexte C2P et les pointeurs de banque. La [suite UNIT153](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT153_SECOND_GET_MC68020.s#L213-L268) vérifie `DB+20 bit0`, appelle `Exec/GetMsg(-372)` si pending, puis les routines C2P, `WaitBlit(-228)`, `BltBitMap(-30)`, et une seconde attente Blitter. En l'absence de message, branche `0` avant le DMA back.
- `Aga C2P Close` → entrée AP20 **148**, UNIT153+$0094A. Le [service natif](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT153_SHORT_SERVICE_MC68020.s#L6-L57) vérifie le contexte `C2P1`, met ses pointeurs internes à zéro, attend `WaitBlit(-228)`, libère le bitmap via graphics.library (`-60`) et le contexte via Exec (`-414`). L'ordre évite une libération de ressources pendant le DMA du même appel.

**Attention :** la présence d'une routine Close explicite correcte ne démontre **pas** automatiquement que tous les chemins **`Screen Close` / `End` / réouverture** invoquent le cleanup au bon moment ; c'est l'objectif de T14. La conversion et les variantes Blit/Zoom n'ont pas de validation croisée B8 nouvelle.

**Statut :** garde Convert et synchronisation Close **confirmées localement**, sécurité globale cycle de vie **VM**.

## 3. Copper : « bit actif en avance » = fail-safe intentionnel, pas P1 confirmé

Traçabilité P2d :
- `Aga Copper Clear` → AP20 36 → [UNIT142+$025AA](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT142_BLOCK_02584_MC68020.s#L21-L90), alloue/initie l'UCopList avec vérification d'identité ; la liste est conservée comme propriété du Screen.
- `Aga Copper On` → AP20 38 → [UNIT142+$02690](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT142_BLOCK_02690_MC68020.s#L6-L59). Vérifie `Screen.UserData & ~3` et `ViewPort.UCopIns`, puis **positionne le bit actif avant** les appels `Intuition/MakeScreen(-378)` et `RethinkDisplay(-390)`.
- `Aga Copper Off` → AP20 40 → [UNIT142+$0273C](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT142_BLOCK_0273C_MC68020.s#L6-L79). Détache `UCopIns`, reconstruit l'affichage, attend `WaitTOF`, libère la mémoire **seulement après succès** ; si une opération de reconstruction échoue, restaure l'association et garde les ressources pour une nouvelle tentative.

Le placement du bit actif **avant** les appels OS, suspect en première lecture, est explicitement commenté dans [le builder historique R18](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/tools/build_m7_copper_raster_r18.py#L147-L179) : en cas d'échec d'activation, la liste doit rester considérée comme active, donc non éditable, **jusqu'à Off**. Le [banc Gate A historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/tools/test_m7_copper_raster_r18.py#L270-L288) vérifiait ce cas sous services OS mockés. **Ne pas déclarer un bug de rollback pour ce drapeau : c'est le contrat fail-safe**, à vérifier maintenant sur la P2d complète.

Le statut de Copper Clear/Wait/Move/End/On/Off sous Close/Swap/End reste **VM**, avec T16 incluant les retours OS simulés `MakeScreen` et `RethinkDisplay` puis récupération `Off`.

## 4. Aga Screen Close : une voie native existe même sans pool B8

**Entrée publique réelle** : `Aga Screen Close` → AP20 **182** → **BOBS+$0718E**.

1. [Trampoline B8/B7 native](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_B7_B8_DRAW_BRIDGE_MC68020.s#L163-L192) appelle **inconditionnellement** `L_BOBS_070D6 = b7m2_close_reset_entry` **avant** de lire le root du callback B8. Même avec root B8 nul, le trampoline n'est donc pas une voie « No-op ».
2. [`b7m2_close_reset_entry`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_B7_B8_DRAW_BRIDGE_MC68020.s#L97-L110) vérifie le CPU/contexte, relaie le reset des 64 Bob slots puis appelle `L_BOBS_06C9E = guarded_close_entry`. Le [builder de ce pont](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/tools/m19_b7m2_close_reset_emit.py#L19-L45) confirme cet ordre et le rôle du relais historique.
3. [`guarded_close_entry`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_P1B_FRAME_GUARD_MC68020.s#L296-L336) lance `screen_close_bridge_entry`. Ce [pont natif](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_P0_SCREEN_PRECLOSE_MC68020.s#L66-L107) identifie l'adresse du véritable Close de l'unité AGA, appelle la préfermeture contrôlée, puis l'exécute (`JSR (A4)`), sans inventer de pointeur OS arbitraire.
4. Le [Close R83](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT142_R83_CLOSE_SAFEWAIT_MC68020.s#L14-L38) acquitte Safe/Disp et attend avec au plus **301 vérifications** dans cette boucle précise. Son dépassement prend une sortie de refus ; il **n'établit pas que toute l'opération Close est bornée en durée**, notamment les éventuelles boucles de drain et le temps des services OS.
5. Une fois ce Close exécuté, le trampoline B8 n'appelle le callback post-close **que si le root est associé au propriétaire courant**, puis nettoie le root **si ce callback retourne un succès**. [Root B8 / End](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_B8_END_REGISTER_MC68020.s#L10-L57) et [finalisation P2d](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_P2D_CONTROLS_MC68020.s#L156-L183) effectuent des opérations d'identité et de remise à zéro, qui restent à vérifier sur refus/réouverture et End.

**Conclusion négative importante :** la crainte que « l'absence de root B8 empêcherait systématiquement `Aga Screen Close` d'atteindre l'ancien Close » est **écartée par la chaîne native**, puisque `b7m2_close_reset_entry` exécute `guarded_close_entry` avant le test du root. **Cela ne valide pas tout Close** : callback, ordre des FreeMem, ports Safe/Disp encore pending et nouvelle allocation à la même adresse sont des risques T14 encore ouverts.

**Classement AGA-004 : validation manquante** (aucun défaut démontré sur la voie sans pool ; les variantes de réouverture sont encore à tester). **AGA-009 : latence possible, non freeze infini confirmé.**

## 5. Polices : ownership partiel vérifié, fermeture croisée encore à tester

- `Aga Font Select` → AP20 87 → [UNIT142+$05150](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT142_BLOCK_05150_MC68020.s#L68-L120) : `OpenLibrary(diskfont)`, `OpenDiskFont`, fermeture du handle library temporaire, puis **commit du nouveau TextFont seulement après succès**, suivi de libération de l'ancienne police. Le pointeur antérieur est conservé si l'ouverture échoue.
- `Aga Font Bank Select` → AP20 89 → [UNIT142+$0530E](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/src/native/m19_p2d/M19_UNIT142_ENTRY_0530E_MC68020.s#L242-L297) : remplacement du pointeur et `L_UNIT142_056A6` pour libération du type précédent. Le [contrat historique R38](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/tools/m14_font_bank_r38_emit.py#L211-L237) distingue une police `BankFont` copiée (StripFont + FreeVec) d'une police OS (CloseFont).
- Le [hook de Screen Close R37](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/74ab87df0a6e4fda8804fd74f541afc310c713f7/tools/m14_font_select_r37_emit.py#L162-L185) contient la libération de la police détenue. Il **reste à tracer sa liaison binaire exacte dans le Close P2d** et à vérifier le résultat Runtime/Compiler lorsque l'on alterne police OS, BankFont et Close/End. La simple présence de ce hook dans un émetteur historique ne permet pas de déclarer le lifecycle conforme.

**Classement :** libération sur remplacement/source partiellement contrôlée ; **T09/T14 validation manquante** pour remplacement/fermeture complète.

## 6. Synthèse du passage et limites

| Domaine | Ce que l'on sait du P2d lié | Verdict actuel |
|---|---|---|
| CBlock 3 entrées | SafePort GetMsg + WaitBlit avant le cœur de copie | Garde locale **présente** ; intégration B8 VM |
| C2P Convert / Close | GetMsg avant DMA back ; WaitBlit avant libération de la bitmap Chip | Garde locale **présente** ; cleanup via Close/End VM |
| Copper On / Off | Drapeau d'activation conservateur, rollback propriétaire ; R18 le prévoit explicitement | **Comportement voulu**, pas nouveau P1 ; Runtime croisé VM |
| Screen Close sans root B8 | Chaîne `b7m2_close_reset → guarded_close → ancien Close` existe | Défaut « Close inopérant faute de root » **écarté statiquement** ; global AGA-004 VM |
| Fonts | Remplacement source/privé ; release selon type | Remplacement contrôlé partiellement, cleanup complet VM |

**Pas de nouvel essai ; aucune correction ni promotion de Lib ; aucune conformité du socle entier revendiquée.** P2d LAST_GOOD demeure la référence, S1-P1e reste gelée. L'[audit transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md), la [matrice de 102 commandes](AUDIT_AGA_MATRICE_COMMANDES_2026-11-23.md) et les [19 scénarios de non-régression](AUDIT_AGA_MATRICE_TESTS_2026-11-23.md) demeurent ouverts.

## Addendum T14C Runtime L2b — 24/11/2026

T14C Runtime L2b : RUN1 ERR0, PREP/FONT/BOB/C2P/COPPER_OK=2, CLOSE_OK=1, END_READY=1, RESULT=0 volontaire, READY_FOR_END. RUN2 RESULT1 ERR0, POST_END_OK=1, PREP/FONT/BOB/C2P/COPPER/CLOSE_OK=1, CLOSED_MOUSE_X=-1, zéro reprise Swap. Banques 12/24 de 81920/328 octets retrouvées avec marqueurs valides, puis Erase et réouverture réussis. Les journaux sont cohérents avec deux lancements consécutifs sans redémarrage (protocole demandé ; absence de redémarrage non instrumentée). Dans RUN2, Chip/Fast après End puis Close témoin sont exactement 1791304/138086736. RUN1 Close témoin : 1791304/138087336 ; delta inter-run Fast 600 octets, cause non mesurée (journal RAM et environnement Runtime), pas de fuite démontrée. T14C PASS du scénario, aucun correctif natif requis. Font système par retours, pas de pixel font/BankFont ; Copper sans oracle visuel ; pas de faute OS injectée, ABA ni inventaire Alloc/Free exhaustif. [BEFORE](../docs/evidence/T14_END_BEFORE_RUNTIME_L2B_2026-11-24.TXT) : 465 octets, 26 CRLF, SHA256 `4fc7b2a8c1b59df17e4ad6ea04a4ded3b9167fe03985803dcaa8fbb99762043c`, blob `e661eb7bf89d63daf2ae3edd38cd469d5fcfd806` ; [AFTER](../docs/evidence/T14_END_AFTER_RUNTIME_L2B_2026-11-24.TXT) : 476 octets, 26 CRLF, SHA256 `1abd067b1a9eb545eeea6471f863b726b0364e9dda56f59de9a2db1b9c54ce5c`, blob `38fef4ad93b53e3fc75e0504119c7bb744bdd4b2`.
