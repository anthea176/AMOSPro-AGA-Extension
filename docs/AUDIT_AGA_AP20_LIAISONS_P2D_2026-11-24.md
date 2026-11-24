# Audit AGA — traçabilité AP20 réelle des 100 commandes P2d
**Analyse du 24 novembre 2026 — lecture seule.** Dépôt `anthea176/AMOSPro-AGA-Extension`, branche `main`, **référence source figée `45911ae8e7816cba9c8f7d1a087091355d5127aa`**. Sprite S1-P1e **GELÉ**.

## Méthode vérifiable
Lecture de `C_Tk` (jetons) et de `C_Lib` (entrées) du [master P2d MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_P2D_LINKED_EDITABLE.s) sans décoder les fichiers binaires `.amos`, ni modifier une bibliothèque. Décodage des deux indices instruction/fonction, du stub `FE31`, de l'indice de groupe et du déplacement ; le dispatcher V2 des quatre groupes mesure **$22 octets**. **Adresse native dans le groupe = déplacement du stub + $22**. Les quatre dispatchers sources : [UNIT142](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_DISPATCH_V2_MC68020.s), [UNIT153](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT153_DISPATCH_V2_MC68020.s), [UNIT156](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT156_DISPATCH_V2_MC68020.s), [BOBS](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_P2D_BOBS_EDITABLE.s).

- **101 tokens** encodés dans le master, dont **1 jeton sentinelle** ; **100 commandes publiques** ; **204 entrées AP20** (sentinelle `Entry_000` et unités comprises). Répartition des **100** appels : **UNIT142 = 68**, **UNIT153 = 5**, **UNIT156 = 1**, **BOBS/202 = 26**.
- Provenance de la Lib LAST_GOOD P2d : **136 020 octets**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, Git blob `8a849b89aae57c2cda0b4db8771034a0978d3e78`. Source/build : [builder P2d](../tools/build_m19_p2d_in_memory.py), master vasm éditable conservant les unités restaurées et vérifiées.
- **Limite :** ce tableau résulte de la lecture statique du master Git sous un HEAD précis. Il **ne recompile pas** le master, ne calcule pas de nouveau SHA256 depuis un binaire assemblé et n'exécute ni WinUAE ni AMOS Compiler. Les fichiers unité marqués `PARTIAL_SOURCE_MIGRATION` conservent des blocs de code/données restaurés pour audit ; une étiquette d'entrée ne prouve pas seule toute la conformité ABI.

## Vérification des chemins prioritaires

| Commande / usage | Entrée AP20 | Unité et cible réelle | Source native et statut |
|---|---:|---|---|
| `Aga Back Fill` | 22 | `142:$00C9E` | [Bloc Back Fill](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_BLOCK_00C9E_MC68020.s) : bitmap arrière + RastPort/RectFill/WaitBlit, **sans GetMsg Safe**. Limitation legacy déjà décrite dans [R27](../docs/M12_SAFE_BLITTER_R27.md), maintenant **AGA-010 P0 risque** en double buffer |
| `Aga Iff Load` | 24 | `142:$00D3C` | [IFF BODY](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_IFF_LOAD_BODY_MC68020.s) : sélection back puis copie directe des plans, **aucun GetMsg Safe dans ce chemin** ; **AGA-001 P0** |
| `Aga Blit Copy` | 31 | `142:$0219C` | [Bloc $0219C](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_BLOCK_0219C_MC68020.s), `GetMsg(-372)` avant `BltBitMap(-30)` |
| `Aga Blit Fill` | 33 | `142:$02360` | [Relais $02360](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_BLOCK_02360_MC68020.s) vers [moteur $078E6](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_BLOCK_078A4_MC68020.s) : `GetMsg(-372)` avant `RectFill/WaitBlit` |
| `Aga Blit Clear` | 35 | `142:$02584` | [Wrapper $02584](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_BLOCK_02584_MC68020.s) rappelle `ENTRY_UNIT142_02360`, donc garde Fill hérité |
| `Aga Swap` | 181 | `202:$0B606` | [P2d Auto/Swap](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_P2D_CONTROLS_MC68020.s) : `p2d_service_update` **avant** `guarded_swap_entry` ; **AGA-002 P1** |
| `Aga Bob Update` | 197 | `202:$0E688` | [Public Update P2d](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_P2D_PUBLIC_UPDATE_MC68020.s), transactions et pool B8 |
| `Aga Bob Clear` | 196 | `202:$0E6EC` | [Public Clear P2d](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_P2D_PUBLIC_UPDATE_MC68020.s), reprise Safe bornée si pool/snapshot valides |
| `Aga C2P Convert` | 146 | `153:$00372` | [UNIT153](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_P2D_UNIT153_EDITABLE.s), garde Safe à vérifier dans toute la chaîne. L'[émetteur C2P](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/tools/c2p_r75_convert_emit.py) contient GetMsg + WaitBlit |
| `Aga F Blit` | 113 | `142:$08CDA` | [Wrapper $08CDA et corps suivant](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_BLOCK_08D78_MC68020.s) : `GetMsg(-372)` retrouvé avant appels Blitter `-636/-606` et `WaitBlit(-228)` |
| `Aga F Icon` | 111 | `142:$08568` | [Corps $08618](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_BLOCK_08618_MC68020.s) : `GetMsg(-372)` retrouvé avant copie CPU |
| `Aga Bank Image Draw` | 105 | `142:$077DC` | [Wrapper $0781C](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_BLOCK_0781C_MC68020.s) appelle `ENTRY_UNIT142_06678` d’Image Draw (garde Safe dans l'[émetteur](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/tools/m16_image_draw_r45_emit.py)) |
| `Aga Bank Image Capture` | 141 | `142:$0D336` | [Corps $0D694](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_BLOCK_0D694_MC68020.s) : `GetMsg(-372)` sur le chemin de lecture des plans |
| `Aga Image Capture` | 103 | `142:$0700A` | [Corps $0725A](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_BLOCK_0725A_MC68020.s) : `GetMsg(-372)` sur le chemin de capture |
| `Aga Screen Pattern` | 14 | `142:$00764` | [Motif diagnostique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45911ae8e7816cba9c8f7d1a087091355d5127aa/src/native/m19_p2d/M19_UNIT142_BLOCK_00764_MC68020.s) utilise le `Screen.RastPort`, pas l'acquisition du back Safe : **compatibilité avec DB/B8 non présumée** |

Le test **ne conclut pas** que les autres appels sont conformes : la matrice ci-dessous fixe seulement le **point d'entrée exact**, pour éviter d'auditer un mauvais builder ou un ancien émetteur.

## Table complète des 100 tokens publics P2d

**Index AP20** = entrée réellement invoquée (instruction ou fonction), **RBSR** = déplacement encodé, **Natif** = cible calculée à partir du dispatcher 34 octets. Tous les nombres de colonnes déplacement/cible sont hexadécimaux.

| # | Token | Rôle | Index AP20 | Groupe | RBSR | Natif +$22 |
|---:|---|---|---:|---:|---|---|
| 1 | `aga probe` | Instruction | 6 | 142 | `$00290` | `$002B2` |
| 2 | `aga detect` | Fonction | 8 | 142 | `$002A0` | `$002C2` |
| 3 | `aga demo` | Fonction | 10 | 142 | `$00300` | `$00322` |
| 4 | `aga screen open` | Fonction | 12 | 142 | `$0F4C0` | `$0F4E2` |
| 5 | `aga screen pattern` | Instruction | 14 | 142 | `$00742` | `$00764` |
| 6 | `aga screen close` | Instruction | 182 | 202 | `$0716C` | `$0718E` |
| 7 | `aga wait vbl` | Instruction | 16 | 142 | `$00A40` | `$00A62` |
| 8 | `aga double buffer` | Fonction | 18 | 142 | `$00A5E` | `$00A80` |
| 9 | `aga swap` | Fonction | 181 | 202 | `$0B5E4` | `$0B606` |
| 10 | `aga back fill` | Instruction | 22 | 142 | `$00C7C` | `$00C9E` |
| 11 | `aga iff load` | Fonction | 24 | 142 | `$00D1A` | `$00D3C` |
| 12 | `aga pic info` | Fonction | 26 | 142 | `$015B6` | `$015D8` |
| 13 | `aga key` | Fonction | 28 | 142 | `$01BF6` | `$01C18` |
| 14 | `aga wait key` | Fonction | 29 | 142 | `$01EA2` | `$01EC4` |
| 15 | `aga blit copy` | Fonction | 31 | 142 | `$0217A` | `$0219C` |
| 16 | `aga blit fill` | Fonction | 33 | 142 | `$0233E` | `$02360` |
| 17 | `aga blit clear` | Fonction | 35 | 142 | `$02562` | `$02584` |
| 18 | `aga copper clear` | Fonction | 36 | 142 | `$02588` | `$025AA` |
| 19 | `aga copper on` | Fonction | 38 | 142 | `$0266E` | `$02690` |
| 20 | `aga copper off` | Fonction | 40 | 142 | `$0271A` | `$0273C` |
| 21 | `aga copper wait` | Fonction | 42 | 142 | `$0280A` | `$0282C` |
| 22 | `aga copper move` | Fonction | 44 | 142 | `$02978` | `$0299A` |
| 23 | `aga copper end` | Fonction | 45 | 142 | `$02AC0` | `$02AE2` |
| 24 | `aga mouse x` | Fonction | 47 | 142 | `$02B98` | `$02BBA` |
| 25 | `aga mouse y` | Fonction | 49 | 142 | `$02C08` | `$02C2A` |
| 26 | `aga mouse buttons` | Fonction | 51 | 142 | `$02C78` | `$02C9A` |
| 27 | `aga mouse pressed` | Fonction | 53 | 142 | `$02D6E` | `$02D90` |
| 28 | `aga mouse released` | Fonction | 55 | 142 | `$02DD8` | `$02DFA` |
| 29 | `aga hotspot hit` | Fonction | 59 | 142 | `$0315A` | `$0317C` |
| 30 | `aga rect overlap` | Fonction | 61 | 142 | `$031C2` | `$031E4` |
| 31 | `aga text` | Fonction | 63 | 142 | `$0324E` | `$03270` |
| 32 | `aga palette load` | Fonction | 65 | 142 | `$034D2` | `$034F4` |
| 33 | `aga palette set` | Fonction | 67 | 142 | `$03A02` | `$03A24` |
| 34 | `aga palette get` | Fonction | 69 | 142 | `$03B30` | `$03B52` |
| 35 | `aga palette save` | Fonction | 71 | 142 | `$03C24` | `$03C46` |
| 36 | `aga palette bank init` | Fonction | 73 | 142 | `$040F8` | `$0411A` |
| 37 | `aga palette bank capture` | Fonction | 75 | 142 | `$04234` | `$04256` |
| 38 | `aga palette bank apply` | Fonction | 77 | 142 | `$044C8` | `$044EA` |
| 39 | `aga fade to bank` | Fonction | 79 | 142 | `$0477C` | `$0479E` |
| 40 | `aga fade to black` | Fonction | 81 | 142 | `$04B1E` | `$04B40` |
| 41 | `aga fade to white` | Fonction | 83 | 142 | `$04D2A` | `$04D4C` |
| 42 | `aga palette cycle` | Fonction | 85 | 142 | `$04F36` | `$04F58` |
| 43 | `aga font select` | Fonction | 87 | 142 | `$0512E` | `$05150` |
| 44 | `aga font bank select` | Fonction | 89 | 142 | `$052EC` | `$0530E` |
| 45 | `aga plot` | Fonction | 91 | 142 | `$056E4` | `$05706` |
| 46 | `aga draw` | Fonction | 93 | 142 | `$058A4` | `$058C6` |
| 47 | `aga box` | Fonction | 95 | 142 | `$05C58` | `$05C7A` |
| 48 | `aga circle` | Fonction | 97 | 142 | `$0607C` | `$0609E` |
| 49 | `aga mouse cursor` | Fonction | 99 | 142 | `$0650A` | `$0652C` |
| 50 | `aga image draw` | Fonction | 101 | 142 | `$06656` | `$06678` |
| 51 | `aga image capture` | Fonction | 103 | 142 | `$06FE8` | `$0700A` |
| 52 | `aga bank image draw` | Fonction | 105 | 142 | `$077BA` | `$077DC` |
| 53 | `aga bank font select` | Fonction | 107 | 142 | `$07856` | `$07878` |
| 54 | `aga image region` | Fonction | 109 | 142 | `$07B34` | `$07B56` |
| 55 | `aga f icon` | Fonction | 111 | 142 | `$08546` | `$08568` |
| 56 | `aga f blit` | Fonction | 113 | 142 | `$08CB8` | `$08CDA` |
| 57 | `aga f icon bank create` | Fonction | 115 | 142 | `$09406` | `$09428` |
| 58 | `aga f icon bank put` | Fonction | 117 | 142 | `$09542` | `$09564` |
| 59 | `aga f chip bank create` | Fonction | 119 | 142 | `$0990E` | `$09930` |
| 60 | `aga f chip stage` | Fonction | 121 | 142 | `$09A7C` | `$09A9E` |
| 61 | `aga f icon capture` | Fonction | 123 | 142 | `$09F48` | `$09F6A` |
| 62 | `aga c block capture` | Fonction | 125 | 142 | `$0A454` | `$0A476` |
| 63 | `aga c block draw` | Fonction | 127 | 142 | `$0AF18` | `$0AF3A` |
| 64 | `aga c block restore` | Fonction | 129 | 142 | `$0B8DC` | `$0B8FE` |
| 65 | `aga c2p open` | Fonction | 144 | 153 | `$00000` | `$00022` |
| 66 | `aga c2p convert` | Fonction | 146 | 153 | `$00350` | `$00372` |
| 67 | `aga c2p close` | Fonction | 148 | 153 | `$00928` | `$0094A` |
| 68 | `aga c2p blit` | Fonction | 150 | 153 | `$009E0` | `$00A02` |
| 69 | `aga c2p zoom` | Fonction | 152 | 153 | `$00F7E` | `$00FA0` |
| 70 | `aga iff to chunky` | Fonction | 155 | 156 | `$00000` | `$00022` |
| 71 | `aga bank palette init` | Fonction | 131 | 142 | `$0C2A4` | `$0C2C6` |
| 72 | `aga bank palette capture` | Fonction | 133 | 142 | `$0C322` | `$0C344` |
| 73 | `aga bank palette apply` | Fonction | 135 | 142 | `$0C3A0` | `$0C3C2` |
| 74 | `aga bank palette fade` | Fonction | 137 | 142 | `$0C8B6` | `$0C8D8` |
| 75 | `aga bank image info` | Fonction | 139 | 142 | `$0CED0` | `$0CEF2` |
| 76 | `aga bank image capture` | Fonction | 141 | 142 | `$0D314` | `$0D336` |
| 77 | `aga bob batch` | Fonction | 160 | 202 | `$00000` | `$00022` |
| 78 | `aga cache blit` | Fonction | 162 | 202 | `$01442` | `$01464` |
| 79 | `aga bob bank` | Instruction | 164 | 202 | `$074D6` | `$074F8` |
| 80 | `get aga bob` | Instruction | 166 | 202 | `$020AC` | `$020CE` |
| 81 | `make aga bob mask` | Instruction | 168 | 202 | `$02D22` | `$02D44` |
| 82 | `no aga bob mask` | Instruction | 170 | 202 | `$02D30` | `$02D52` |
| 83 | `aga bob blit` | Fonction | 172 | 202 | `$058A0` | `$058C2` |
| 84 | `aga bob` | Instruction | 174 | 202 | `$074A4` | `$074C6` |
| 85 | `aga bob off` | Instruction | 176 | 202 | `$05B64` | `$05B86` |
| 86 | `aga bob draw` | Fonction | 183 | 202 | `$070D6` | `$070F8` |
| 87 | `aga bob clear` | Fonction | 196 | 202 | `$0E6CA` | `$0E6EC` |
| 88 | `aga bob update` | Fonction | 197 | 202 | `$0E666` | `$0E688` |
| 89 | `aga bob bank free` | Instruction | 198 | 202 | `$0E832` | `$0E854` |
| 90 | `aga x bob` | Fonction | 199 | 202 | `$0ED4E` | `$0ED70` |
| 91 | `aga y bob` | Fonction | 200 | 202 | `$0ED7E` | `$0EDA0` |
| 92 | `aga i bob` | Fonction | 201 | 202 | `$0EDAE` | `$0EDD0` |
| 93 | `aga bob priority` | Fonction | 178 | 202 | `$07B62` | `$07B84` |
| 94 | `aga limit bob` | Fonction | 180 | 202 | `$07D5C` | `$07D7E` |
| 95 | `aga del bob` | Fonction | 185 | 202 | `$07EDE` | `$07F00` |
| 96 | `aga ins bob` | Fonction | 187 | 202 | `$07F0C` | `$07F2E` |
| 97 | `aga bob col` | Fonction | 189 | 202 | `$09D16` | `$09D38` |
| 98 | `aga bob flip` | Fonction | 191 | 202 | `$09E74` | `$09E96` |
| 99 | `aga bob planes` | Fonction | 193 | 202 | `$0B4A2` | `$0B4C4` |
| 100 | `aga bob auto update` | Fonction | 195 | 202 | `$0B56A` | `$0B58C` |

## Non-conformités de coordination et décisions encore attendues

1. Les vérifications **locales Safe** de Copy, Fill, Image Draw, F Blit, CBlock, C2P ne prouvent pas l'invalidation globale des snapshots. **Toutefois, le contrat P2d est explicite : `Aga Bob Clear` → dessin du décor → `Aga Swap`**. Le bit `cleared` du [B8 transactionnel](../tools/m19_b8_clear_update_tx_emit.py) permet alors de capturer le nouveau fond sans restaurer l'ancien. **AGA-003 est donc requalifiée en validation manquante du chemin autorisé**, pas bug P1 confirmé par une écriture hors contrat.
2. Les commandes **legacy sans Safe** (`Aga Back Fill`, `Aga Iff Load`) ne doivent pas être utilisées comme implicitement sûres après un Swap. **Le gel interdit tout patch**, et ce rapport n'autorise aucune correction automatique.
3. Le `BODY` IFF est décodé en deux passes à partir du même buffer alloué une seule fois, validation avant écriture. Cette structure limite le risque d'une erreur de format tardive pendant la seconde passe : **AGA-007 reste à qualifier**, aucune écriture partielle sur retour 0 n'est démontrée.
4. **Aucun essai WinUAE/Compiler nouveau**, aucune assertion d'intégrité globale, **aucune validation de la capture Sprite S1** : candidate S1-P1e préservée et chantier gelé.

[Audit transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md) · [Matrice commande → mémoire](AUDIT_AGA_MATRICE_COMMANDES_2026-11-23.md) · [Scénarios](AUDIT_AGA_MATRICE_TESTS_2026-11-23.md)
