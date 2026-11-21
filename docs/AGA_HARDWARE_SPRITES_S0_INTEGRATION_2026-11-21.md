# S0 — Audit d'intégration des Sprites matériels AGA (21 novembre 2026)

**État : AUDIT S0 EN COURS — modèle hôte 12/12 PASS ; aucun Sprite natif / ASC / WinUAE.**
Référence protégée : **M19 P2d**, `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` byte-identiques, **136 020 octets**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, cible MC68020/68EC020 minimum. Les deux bibliothèques et le banc `tests/current/M19_P2_ALL_IN_ONE.asc` ne sont pas modifiés.

## 1. Architecture source examinée (autorité = sources du dépôt)

- `tools/build_m19_p2d_in_memory.py` : assemble P2d de manière déterministe à partir de P2c/P1e ; 100 commandes / 203 sections AP20. **Pas de commandes Sprite DMA**. Le binaire est une référence à préserver, pas un point de départ à désassembler pour produire du nouveau code.
- `tools/build_ntsc_pal_r10.py` et `docs/M3_SCREEN_DESIGN.md` : l'écran privé est issu d'Intuition `OpenScreenTagList`, avec tags de largeur, hauteur, profondeur et ModeID, sous le contrôle de l'OS. Les builders historiques prouvent l'intention et la provenance ; **la valeur effective du bit Sprites sur le ViewPort du P2d installé n'est pas observée**.
- `tools/m15bis_cursor_r44_emit.py` : contexte AMOS `A5+$01C8`, `Screen*` à l'offset 0 du contexte, `IntuitionBase` à +4, `GfxBase` à +8, `Window*` à +36 ; vérifie `Window.WScreen` à +46 ; pointeur transparent local à la fenêtre, tampon 72 octets Chip, `SetPointer/ClearPointer`, et hook `CloseWindow`. Ne pas réutiliser son tampon pour le nouveau Sprite.
- `tools/m19_p0c_screen_close_bridge_emit.py`, `tools/m19_p0c_screen_preclose_emit.py`, `tools/m19_p0j_swap_barrier_emit.py` : fermeture privée et `Aga Swap` à état propriétaire vérifié, avec armement/cleanup Bob/Chip ; **un nouveau Sprite doit être détaché et libéré AVANT la fermeture effective de sa fenêtre/Screen**, sans effacer les gardes Bob, et sans jamais déclencher un Swap.
- `docs/M7_COPPER_R18.md` : liste `UCopList` appartenant à `ViewPort.UCopIns`, états de Copper dans les deux bits bas de `Screen.UserData`. Aucun nouveau champ Sprite dans ces bits. **Ne pas écrire `COP1LC/COP2LC` ou changer `FMODE/BPLCON3/BPLCON4` directement** dans S1.

**Attention** : les offsets internes AMOS et les structures OS ci-dessous sont deux espaces distincts ; les données historiques doivent être confirmées par une sonde sur la Lib P2d et par les includes NDK réellement employés avant émission MC68020.

## 2. API NDK AmigaOS V39 — direction S1

Pour le **premier Sprite 16 pixels, 2 bits/pixel, non attaché**, choisir le chemin OS le plus réduit :
  
| Fonction `graphics.library` | Contrat et registres ABI documentés | Résultat attendu |
| --- | --- | --- |
| `GetSprite(SimpleSprite*, -1)` | `A0=SimpleSprite*`, `D0=-1` (premier canal libre), LVO **-408** | Canal **0..7 réellement attribué**, ou **-1**. Ne jamais inventer/sélectionner un numéro fixe |
| `MoveSprite(ViewPort*,SimpleSprite*,X,Y)` | `A0=ViewPort*`, `A1=SimpleSprite*`, `D0=X`, `D1=Y`, LVO **-426** | Position sur le ViewPort ; vérifier la convention et l'offset réel d'affichage |
| `ChangeSprite(ViewPort*,SimpleSprite*,data)` | `A0=ViewPort*`, `A1=SimpleSprite*`, `A2=data`, LVO **-420** | Changement d'image par l'OS uniquement après vérification du format/ownership |
| `FreeSprite(n)` | `D0=n`, LVO **-414** | Libérer **seulement** le canal obtenu avec succès |

Inclure les signatures/offsets exacts des versions NDK utilisées dans les tests futurs avant de coder une routine. Les API **étendues**, à étudier en S2, sont `AllocSpriteDataA`, `GetExtSpriteA`, `ChangeExtSpriteA`, `FreeSpriteData` ; ne pas mélanger les ressources `SimpleSprite` et `ExtSprite` dans le modèle S1.

La structure NDK `SimpleSprite` contient `posctldata` (LONG), `height`, `x`, `y`, `num` (WORD) : **12 octets**, hors données image. Pour un Sprite 16×16 classique, prévoir **72 octets Chip** : 2 mots de contrôle, 16×2 mots de pixels 2 bpp, 2 mots terminateurs. Pas d'index couleur 256 direct dans un Sprite : **transparent + trois couleurs visibles**, dont les registres peuvent interagir avec le Copper/les bitplanes. Le bitmap source peut exister en Fast, mais **le tampon réellement référencé par DMA doit être en Chip**.

Les offsets `struct Screen` (ViewPort embarqué à **+44**) et `struct ViewPort` (`Modes` à **+32**) indiquent une **sonde candidate `Screen*+76`** pour `ViewPort.Modes`. Le mode `V_SPRITES=$4000` est une constante NDK à recouper ; **ce calcul d'offset n'est PAS encore une mesure sur la P2d sous WinUAE**, et ne justifie pas d'écriture dans ces structures. Utiliser les includes réels `intuition/screens.i`, `graphics/view.i`, `graphics/sprite.h` et les Autodocs V39 au jalon natif.

Sources NDK/AmigaOS : https://developer.amigaos3.net/autodocs/graphics.library/ ; https://d0.se/include/graphics/sprite.h ; https://d0.se/include/graphics/view.h ; https://wiki.amigaos.net/wiki/Hardware_Sprites .

## 3. Modèle de propriété host-only exécuté

- Source : [`tools/aga_sprite_s0_model.py`](../tools/aga_sprite_s0_model.py).
- Tests : [`tools/test_aga_sprite_s0_model.py`](../tools/test_aga_sprite_s0_model.py).
- CI dédiée : [`.github/workflows/aga-sprite-s0-host.yml`](../.github/workflows/aga-sprite-s0-host.yml) ; **12 tests hôtes PASS localement**, confirmation CI indépendante à relever.
- Phases : `EMPTY → DATA_READY → CHANNEL_OWNED → VISIBLE → DMA_DETACHED → RELEASED`, avec les raccourcis d'échec `DATA_READY → RELEASED` si aucun canal.
- La mémoire image est affectée à **un seul écran privé et ViewPort**, et le numéro de canal est **strictement celui renvoyé par `GetSprite(-1)`**. Un retour `-1` n'autorise jamais `FreeSprite`. Le canal 0 **n'est ni choisi par défaut ni interdit arbitrairement** : seul l'OS peut l'accorder, si disponible.
- Un nettoyage bloqué tant que DMA est susceptible de référencer l'image. Les obligations sont ordonnées : **détacher le Sprite / prouver l'arrêt de la référence DMA → `FreeSprite` du canal possédé → `FreeMem` de l'image Chip → fermeture écran**.
- `confirm_dma_detached()` est uniquement **une attestation passée par un futur adaptateur externe**. Le modèle n'appelle aucun LVO et **ne démontre pas que le DMA est réellement arrêté**. Il ne valide ni un simple VBL, ni un `Aga Swap`, ni un `ChangeSprite(NULL)` non documenté. L'adaptateur OS réel devra lever ce verrou.
- Les tests couvrent allocation normale, mouvement, canal saturé, plage 0..7, propriétaire incorrect, double acquisition, OOM, refus de release si DMA référencé, libération idempotente et réouverture avec propriétaire neuf. Ils ne testent **aucun pixel** et n'impliquent **aucune interruption, Copper, AMAL ou Bob**.

**Exécution du modèle** : `PYTHONPATH=tools python -B -m unittest discover -s tools -p 'test_aga_sprite_s0_model.py' -v`.

## 4. Verrous encore ouverts — avant S1 natif

1. **Sonde WinUAE de l'écran AGA réel** : `Screen*`, `ViewPort*`, `Modes`, état Sprite autorisé, conflits avec le pointeur Intuition et canaux réellement libres. La sonde doit lire, sans réécrire `Screen.ViewPort` ou `UserData`.
2. **Propriété et DMA** : obtenir un protocole démontrable de mise hors DMA/attente/FreeSprite/FreeMem conforme aux Autodocs et au comportement Intuition, sur fermeture normale, erreurs, Ctrl+C et réouverture ; les 12 tests hôtes ne couvrent pas le matériel.
3. **Palette et priorité** : distinguer les palettes 2bpp Sprite des 8 bitplanes à 256 couleurs ; mesurer les interactions avec `COLOR16..31`, Copper et pointeur. Ne modifier aucun registre AGA dans S1 sans preuve.
4. **ABI/offsets réels de P2d** : tracer la bonne adresse `Screen*` jusqu'au ViewPort sans écriture intrusive, valider 68020 et les phases de teardown par source autoritative/NDK ; aucun patch de HUNK désassemblé.
5. **S1 minimal seulement après clôture S0** : un Sprite matériel 16×16, mouvement, off/close, échecs canal/OOM, présence du pointeur, Bobs en arrière-plan et Copper On/Off. Essais **Gate A CPU native** puis **B WinUAE Runtime**, **C vrai Compiler**, **D matériel** indépendants.

## 5. Décision de périmètre

S0 reste **ouvert**. Aucune API publique `Aga Sprite`, aucun nouveau fichier `.asc` actif, aucune nouvelle Lib candidate, aucun binaire réassemblé, aucune promotion ou release. Prochaine intervention utile : **sonde native en lecture seule de l'état `Screen/ViewPort`**, puis choix du contrat de détachement DMA ; ne pas déplacer le socle P2d `LAST_GOOD` avant autorisation.
