# Audit AGA P2d — passage 8 : dépendances graphiques, caches, C2P et données d'entrée

**Révision : 24 novembre 2026 · Branche : `main` uniquement · Source de référence : `78d16a05700afeb3b5759b67b0b553085eb404c8`.**  
**Statut : AUDIT OUVERT, corrections gelées, chantier Sprite S1-P1e GELÉ.** Relecture des chemins MC68020 liés et des contrats historiques ; **aucune compilation, aucun test CPU/WinUAE/Compiler nouveau, aucune modification native/Lib/ASC**.

> **Addendum Runtime 24/11/2026 :** T06A Runtime FAIL sur P2d-L2 : PROBE_COMPLETE=1, TARGET FRONT, ERR 50, back 17/17/17 inchangé, ancien front 64/128/192. Trois Swaps sans refus, fermeture correcte. Écriture de la page présentée confirmée, pas une simple modification de palette. Défaut bloquant 0.14.1 ; aucune preuve d'écriture du back sous Safe pending (non testé). [Preuve](evidence/T06_PATTERN_RUNTIME_FAIL_L2_2026-11-24.TXT). Le classement initial ci-dessous est historique. La routine Pattern utilise SetRGB32 (-852), pas LoadRGB32 ; cf. [protocole T06A](../tests/proto/t06_pattern/README.md).

## 1. AGA-011 — `Aga Screen Pattern` contourne la sélection de la page arrière

**Liaison publique P2d :** instruction `Aga Screen Pattern` → AP20 **14** → UNIT142+$00764. [Source natif complet](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/src/native/m19_p2d/M19_UNIT142_BLOCK_00764_MC68020.s#L6-L56).

La routine charge la structure **Screen** courante depuis `456(a5)`, prend `(a2)` (Screen*), puis effectue dans la boucle :
- `lea 44(a4),a0` → `graphics/LoadRGB32(-852)` (couleur/ColorMap),
- `lea 84(a4),a1` → `SetAPen(-342)` et **`RectFill(-306)` sur `Screen.RastPort`**.
- **Aucune sélection explicite de `DBState.back_sb` ni consultation `DB+20`/SafePort, et aucun `GetMsg(-372)`** sur cette routine.

**Ce qui est confirmé :** dessin par le RastPort du Screen, indépendamment des gardes des commandes `Aga Blit Fill` et `Aga Image Draw`. **Ce qui ne l'est pas :** quel BitMap Intuition cible effectivement par `Screen.RastPort` *après* `ChangeScreenBuffer`, si le front est touché sous WinUAE et si la commande est destinée contractuellement à être appelée en mode Double Buffer. Le README ne promet qu'une **mire de diagnostic** ; une assertion de corruption du front serait prématurée.

**Classement AGA-011 : P1 potentielle / sécurité à qualifier**. Si une écriture sur un bitmap non Safe est reproduite, la gravité bascule en **P0**. La vérification sera une **variante de T06**, comparant `Aga Screen Pattern` à `Aga Blit Fill` avec plusieurs Swap, lectures des deux BitMaps et message Safe absent/disponible, et non un patch immédiat. Déterminer aussi le comportement de `LoadRGB32` sur les deux pages : effet global de palette distinct des pixels.

**Important :** `Aga Demo` → AP20 **10** → UNIT142+$00322 ([source](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/src/native/m19_p2d/M19_UNIT142_GRAPHICS_SCREEN_MC68020.s#L6-L96)) **ouvre son propre Screen Intuition** via les services OS, dessine dedans, attend **151 `WaitTOF` bornés**, puis ferme ce Screen. Cela **n'en fait pas un écrivain du back buffer de l'écran privé AGA**. Il reste à vérifier son interaction de premier plan et son retour AMOS ; pas de blocage infini démontré par son compteur.

## 2. FICON/FICHIP : cache `ready` transactionnel, cohérence source manuelle

**Chemin de capture** `Aga F Icon Capture` → AP20 **123** → UNIT142+$09F6A. Le [corps lié](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/src/native/m19_p2d/M19_UNIT142_BLOCK_0A006_MC68020.s#L214-L307) valide les 8 pointeurs de plans, vérifie leur résidence réelle par `TypeOfMem(-534)`, **acquitte SafePort par `GetMsg(-372)` avant de lire**, attend le Blitter, puis copie 16×16 indices dans le slot `FICON8`. C'est une **protection de lecture locale**, pas une preuve du cycle d'édition complet.

**Chemin Stage** `Aga F Chip Stage` → AP20 **121** → UNIT142+$09A9E. Le [code de réorganisation du slot](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/src/native/m19_p2d/M19_UNIT142_BLOCK_09C80_MC68020.s#L154-L198) vérifie notamment les blocs Chip, met `ready=0`, copie et met **`ready=1` seulement après le slot complet**. Le cache est une banque `FICHIP8` distincte du `FICON8` source.

**Dépendance volontaire et documentée** : [contrat M18 R66](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/docs/M18_DYNAMIC_CHIP_CACHE_DESIGN.md#L16-L34) et [capture R67](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/docs/M18_FICON8_CAPTURE_DESIGN.md#L37-L43) : après `Aga F Icon Bank Put` ou `Aga F Icon Capture`, l'appelant **doit refaire `Aga F Chip Stage`** avant `Aga F Blit`. La modification du FICON ne décrémente ni n'invalide automatiquement l'ancien marqueur `ready=1` du FICHIP. **Un Blit affichant une ancienne image sans restaging n'est pas, en soi, une corruption de snapshot B8.**

**Classement : contrat explicite, T11 non exécuté en croisé B8**. Vérifier aussi le refus du Blitter lorsque `ready=0`, le changement de banque AMOS source/destination et la fin DMA avant `Erase Bank`.

## 3. AGPC / `Aga Cache Blit` : Chip RAM vérifiée, flags ABK insuffisants

Le chemin `Aga Cache Blit` → AP20 **162** → BOBS+$01464 passe par [l'entrée de cache native](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/src/native/m19_p2d/M19_P0_CORE_DISPATCH_MC68020.s#L1503-L1779). Le validateur exige le marqueur `AGPCACHE`, des dimensions/offsets exacts, puis acquitte **`GetMsg(-372)` si Safe pending** avant de déléguer le dessin. Le [coeur Blitter](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/src/native/m19_p2d/M19_P0_CORE_DISPATCH_MC68020.s#L1918-L1978) vérifie une résidence mémoire Chip au moyen de `TypeOfMem(-534)`, puis `BltMaskBitMapRastPort(-636)` ou `BltBitMapRastPort(-606)` et `WaitBlit(-228)`.

**Preuve historique à conserver sans la transposer à P2d** : [diagnostic R88 du 15/11](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/docs/M19_P28_R88_CHIP_BANK_DIAGNOSTIC_2026-11-15.md#L5-L23) : des banques ABK indiquant un souhait Chip (`flags disque=3`) ont été **chargées en Fast RAM** sous WinUAE (delta Chip nul, delta Fast négatif), conduisant à **quatre refus propres** de Blit, pas à des dessins corrompus. Les quatre refus appartiennent à **R88 historique**, pas à une Gate B nouvellement exécutée sur P2d.

**Invariant transversal :** pour tout DMA, contrôler la **résidence Chip effective de la plage complète**, pas le nom de banque, les flags ABK ou `Reserve` supposé. Pour le rendu CPU depuis une banque DATA Fast, une lecture peut rester autorisée selon le contrat individuel. Prévoir dans **T10/T11** : bank loaded in Fast, explicit Chip stage, stage terminé, cache remplacé/Erase, puis Swap. La correction éventuelle ne doit **pas** contourner le rejet non-Chip.

## 4. AGAPIC / Image Region : garde Safe constatée dans les chemins réellement publiés

- `Aga Image Draw` (AP20 **101**, UNIT142+$06678) : [Source MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/src/native/m19_p2d/M19_UNIT142_ENTRY_06678_MC68020.s#L383-L410) vérifie Safe et consomme `GetMsg` **avant le dessin**.
- `Aga Bank Image Draw` (AP20 **105**, UNIT142+$077DC) : [wrapper](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/src/native/m19_p2d/M19_UNIT142_BLOCK_0781C_MC68020.s#L6-L28) prépare la source de banque et appelle l'entrée `ENTRY_UNIT142_06678`, donc **hérite** de sa garde.
- `Aga Image Region` (AP20 **109**, UNIT142+$07B56) : après sélection/validation de la source, [bloc $07BC8](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/src/native/m19_p2d/M19_UNIT142_BLOCK_07BC8_MC68020.s#L378-L424) teste `DB+20 bit0`, effectue `GetMsg(-372)` et refuse si aucun message.
- `Aga Cache Blit`, `Aga F Icon`, `Aga F Blit`, et `Aga F Icon Capture` ont également des **gardes locales de page ou de banque**, documentées ci-dessus et dans l'[audit AP20](AUDIT_AGA_AP20_LIAISONS_P2D_2026-11-24.md).

**Statut : présence statique du garde Safe local**, non validation Runtime de toutes les combinaisons `Clear → décor → Swap`. T06/T11. Un writer direct comme **`Aga Iff Load`**, **`Aga Back Fill`** ou **`Aga Screen Pattern`** ne bénéficie pas magiquement de la garde d'un autre token.

## 5. C2P : deux couches mémoire et un seul passage vers les plans

Les [contrats R78 Blit](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/docs/C2P_R78_BLIT_CONTRACT_2026-11-14.md#L8-L25) et [R79 Zoom](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/docs/C2P_R79_ZOOM_CONTRACT_2026-11-14.md#L8-L36) définissent `Aga C2P Blit` (AP20 150) et `Aga C2P Zoom` (AP20 152) comme **copies CPU de banque DATA/WORK chunky vers le tampon chunky du contexte C2P** : aucun accès planaire, aucune conversion ou Swap implicite.

La [source native UNIT153 liée](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/src/native/m19_p2d/M19_P2D_UNIT153_EDITABLE.s#L27-L45) contient les préflights et copies C2P ; le passage vers le bitmap arrière a lieu via **`Aga C2P Convert` (AP20 146)** avec son propre `GetMsg(SafePort)` et sa synchronisation Blitter. Échouer Blit/Zoom sur un problème de banque chunky ne doit **pas** déclencher Convert/Swap. Tester dans **T06 et T14** les erreurs de banque, `Close` C2P, `Screen Close` puis réouverture, sans déduire qu'une fermeture de Screen appelle systématiquement `C2P Close`.

**Statut : séparation des domaines de mémoire explicitée ; conformité Close/End croisée toujours VM.**

## 6. R76 historique : déplacements vers données clavier/souris, contrôle permanent nécessaire

[Incident R74/R75 → R76 et sa cause native](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/docs/C2P_R76_RPG_REGRESSION_2026-11-14.md#L5-L41) : une insertion de 138 octets avait déplacé le tableau d'état clavier/souris, laissant **sept instructions LEA à offsets obsolètes**. Une initialisation `CLR.L` effaçait alors du **code exécutable** ; le RPG pouvait geler sans utiliser C2P.

Le script [`tools/test_current_input_state_offsets.py`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/tools/test_current_input_state_offsets.py#L9-L46) vérifie les **7 LEA** et **8 mutations négatives** sur l'héritage figé, précisément pour prévenir cet incident. **Attention état courant** : sa sélection `main()` [lignes 48–74](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/78d16a05700afeb3b5759b67b0b553085eb404c8/tools/test_current_input_state_offsets.py#L48-L74) est encore basée sur un ensemble de SHA historiques ; la candidate S1-P1e est maintenant la Lib **active** mais n'est pas listée dans la branche de `P2D_SHA`. Une exécution naïve du contrôle sur `dist/AMOSPro_AGA.Lib` S1 ne constitue donc pas un certificat de son héritage P2d ; **politique CI à reprendre après l'audit, sans patch maintenant**. AGA-005 doit inclure ce point.

**Critère de clôture structurelle :** tout futur assemblage/relocation/swap de groupe exige un contrôle de la disposition effective des données accessibles par déplacements relatifs à `State`, **en plus de** SHA exact, HUNK/AP20 et relocations, avant les Gates B/C. Les tests clavier/souris du banc P2 historique restent intacts.

## 7. Graphe des dépendances croisées à vérifier (aucun PASS implicite)

| Séquence | Dépendance / règle | Risque si non respectée | Scénario |
|---|---|---|---|
| `Open → Double Buffer → Swap` | Messages Safe/Disp et `DB+20` | Attente/refus illégitime, page non Safe | T01,T05 |
| `Swap → Iff Load` | IFF sans GetMsg local | P0 statique de protection | T04,T12,T17 |
| `Swap → Back Fill` | SetRast sans GetMsg local | P0 statique de protection | T19 |
| `Swap → Screen Pattern` | Screen.RastPort direct, pas de back explicite | **AGA-011 P1**, éventuelle écriture front/non-Safe | T06 |
| `Auto Update → premier Bind B8` | Safe pending refusé avant routine GetMsg Swap | **AGA-002 P1 conditionnelle** | T02 A–E |
| `Bob Clear → éditer décor → Swap` | Bit `cleared`, snapshot fond nouveau | AGA-003 VM contractuelle | T03 |
| `FICON Put/Capture → FICHIP Stage → F Blit` | Cache `ready` et restaging manuel | Image périmée malgré appels locaux valides | T11 |
| `Load ABK → Cache Blit` | Chip RAM réelle, pas seulement flags ABK | Refus légitime si banque en Fast | T10,T11 |
| `Image Draw/Region/Cache Blit → Swap` | GetMsg Safe avant pixels, Clear si décor B8 | Garde locale OK, intégration VM | T05,T06,T11 |
| `C2P Blit/Zoom → Convert → Swap` | Chunky privé distinct du bitmap arrière | Convert prématuré / page non prête | T06,T14 |
| `Palette Set/Apply/Cycle → Swap` | ColorMap global, snapshot de pixels inchangé | Faux positif d'invalidation B8 | T09,T12 |
| `Bob Bank Free / Erase / Load → Update` | Stamp, owner, cache Chip, CLEAN/READY | Banque périmée / cache orphelin | T10 |
| `CBlock Capture/Restore → Swap` | Capture back Safe, restauration sous Clear si décor | Mauvais bitmap / snapshot | T13 |
| `C2P/Copper/Fonts/B8 actifs → Screen Close → Open` | Propriété des ressources et callbacks End | Double Free, fuite, pointer ABA | T14,T16 |
| `nouveau binaire → Screen Open / Mouse/Key` | Sept offsets State, relocation/HUNK | **Régression R74/R75 connue**, corruption code | Gate A/T14 |

## 8. Bilan / critères de clôture restants

- **P0 statiques documentées** : AGA-001 IFF et AGA-010 Back Fill (sans corruption Runtime prouvée).
- **P1 conditionnelle documentée** : AGA-002 premier Bind B8.
- **P1 nouvelle à qualifier** : AGA-011 `Screen Pattern` direct `Screen.RastPort` après Swap.
- **Contrats à ne pas classer comme anomalies sans test :** B8 Clear→décor→Swap ; restaging FICHIP ; refus DMA hors Chip ; palette-only ne change pas les snapshots.
- **Échec CI historique et dispositions clavier/souris** : AGA-005, corrections de politique CI reportées après gel.
- **Gate A/B/C** : aucune nouvelle exécution. **19 scénarios planifiés, pas un seul requalifié PASS pendant ce passage**. Même les chemins avec GetMsg source ne sont pas marqués globalement conformes.
- **S1-P1e Sprite : GELÉE**, source, candidate 142 000 octets et `LAST_GOOD` P2d 136 020 octets à préserver.

La prochaine vérification documentaire utile consiste à confronter ce graphe aux **journaux originaux P2d Runtime/Compiler**, puis à préciser les conditions de test restant sans preuve avant toute décision de réparation. **Aucune correction native autorisée par le présent rapport.**
