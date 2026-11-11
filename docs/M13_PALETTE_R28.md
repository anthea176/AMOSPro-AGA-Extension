# M13 / R28 0.10.0 — palette AGA 24 bits : premier incrément

**11 novembre 2026 — Gate A CPU/CI PASS : 159 cas 68000 ; Gate B AMOS/WinUAE NON TESTÉE.** M13 doit aboutir à une gestion complète : palettes indépendantes des pixels, couleurs RGB, fades, color cycling, sauvegarde/restauration. **Ce R28 n'est que le socle chargement/écriture/lecture**, pas l'achèvement de M13. Le **binaire courant `dist/AMOSPro_AGA.Lib` est R28 0.10.0**, candidate Gate B. **`dist/AMOSPro_AGA_LAST_GOOD.Lib` est R27 0.9.3**, dernière version Gate A+B PASS sur M12. R28 possède aussi une archive versionnée, [archive 0.10.0](../dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib) de **16 208 octets**, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c`. [CI native M13 : 159 tests PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43004699618).

## Audit source et ABI AmigaOS

- L'écran AGA propre à l'extension est un **Screen Intuition privé**. Son ViewPort est à `Screen+44` et `ViewPort.ColorMap` à `Screen+48`. Le `ColorMap.Count` (UWORD, offset +2) est vérifié ; l'accès n'est pas lié aux écrans gérés par AMOS.
- L'ancien loader M5 contient déjà une méthode validée de construction de tables CMAP RGB8 → fractions RGB32, suivie de `graphics.library/LoadRGB32` (**LVO -882**, `A0=ViewPort, A1=table`). L'Autodoc officiel indique que **LoadRGB32 est plus rapide que SetRGB32 même pour une seule couleur** et permet de charger toutes les entrées, y compris celles non utilisées.
- `graphics.library/GetRGB32` (**LVO -900**) prend `A0=ColorMap`, `D0=premierPen`, `D1=nombre`, `A1=table`. Trois LONGs RGB32 donnent les couleurs. L'extension ne lit pas directement la table hardware/Copper.
- Le **format CMAP** d'un ILBM est un tableau de triplets RGB8. La version R28 ne copie **jamais** le chunk BODY et accepte un **FORM ILBM avec CMAP valide**, même sans BMHD/BODY. Elle rejette les tailles CMAP non multiples de 3, le surdimensionnement et les chunks dupliqués.
- **Modes ciblés :** indices 0 à `min(2^depth,ColorMap.Count)-1` pour écran indexé AGA de profondeur 1–8. **HAM, EHB et dual playfield refusés**, en attendant un contrat spécialisé. Aucun accès direct à BPLCON3 ou COLORxx.
- L'appel `LoadRGB32` dépend du ColorMap du ViewPort, **pas du back BitMap** : aucune sonde `Safe` ne doit être nécessaire pour la palette. `Aga Palette Set` ne bloque pas sur le VBL ; le programme peut synchroniser une animation avec `Aga Wait Vbl`. `Aga Palette Load` conserve la synchronisation `WaitTOF` de M5, une fois après le chargement.

Source primaire à consulter : Amiga NDK39 `graphics/view.h`, les Autodocs `LoadRGB32` / `GetRGB32` et [les règles locales sur CMAP](../EXTENSION_SOURCE_RULES.md).

## Trois fonctions expérimentales R28

| API AMOS projetée | Résultat | Règle |
|---|---|---|
| `_OK=Aga Palette Load(_FILE$)` | `1` réussite / `0` échec | Charge seulement les entrées RGB d'un **FORM ILBM** (CMAP), sans modifier les pixels du buffer ni le mode écran. Le chemin est un descripteur chaîne AMOS, comme `Aga Iff Load`. |
| `_OK=Aga Palette Set(_PEN,_R,_G,_B)` | `1` / `0` | Modifie un index par trois composantes **0..255** ; un appel `LoadRGB32` court, sans attente VBL intégrée. |
| `_RGB=Aga Palette Get(_PEN)` | `$00RRGGBB` ou `-1` si refus | Relit via `GetRGB32` depuis le ColorMap actif ; le noir vaut `0`, **pas une erreur**. Retour entier positif sur 24 bits. |

**Périmètre AP20 :** 3 tokens ajoutés après les 31 existants, avec trois segments en fin de HUNK ; les segments 0..35 restent identiques octet pour octet, le segment texte final 36 reçoit uniquement `GetP`, et les segments Palette Load/Set 37/38 reçoivent chacun le séparateur `GetP` requis avant l'entrée suivante. 40 segments au total. **Les liens BSR clavier/souris R23 ne changent pas**, car tout ajout suit le dernier segment existant. Toute différence non prévue doit bloquer Gate A.

**État :** le builder en mémoire reproduit **à l'octet près** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) et l'archive R28 versionnée, 16 208 octets. Le préflight CPU 68000/Capstone/Unicorn **a passé 159 scénarios** dont les variantes **IFF palette seule avec/sans BMHD, avec chunks CRNG, sans BODY**, ainsi que les images ILBM complètes (géométrie source indépendante). [Test WinUAE actif](../tests/current/M13_R28_PALETTE_01.asc) : **aucun PASS réel encore**. Le fichier `LAST_GOOD` a été mis à jour vers **R27 validée WinUAE**, comme l'exige la règle de promotion. Son archive versionnée et l'archive R10 sont intactes. **R28 ne sera promue dans LAST_GOOD qu'après Gate B PASS utilisateur.**

## Gate A — contrôles réalisés en CPU/CI

- Décompilation Capstone 68000 : instructions valides, cibles de branche alignées, labels internes, aucune instruction illégale.
- Machine Unicorn 68000 : `D3` résultat, `D2=0`, A3 consommé correctement, hardware SP équilibrée et autres registres sauvegardés. `Set` : 32-bit RGB fractions correctes et header `LoadRGB32` exact. `Get` : lecture des trois fractions et pack RGB8 correct, rejet `-1` sans effet.
- `Load` : FORM ILBM CMAP sans BMHD/BODY, taille variable de 1 à 256 couleurs, refus des chunks malformés/dupliqués, ressources DOS/Exec libérées sur chaque chemin, **zéro écriture de bitplane**.
- Profondeurs 1, 2, 4, 8 ; indices invalides, octets RGB hors bornes ; ColorMap/Screen/GfxBase invalides ; HAM/EHB/DualPF refusés. Anciennes régressions R27 et anciens tests archivés restent inchangés.
- **Gate A PASS :** candidate R28 dans [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) et archive versionnée [disponible séparément](../dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib) et [test WinUAE unique actif](../tests/current/M13_R28_PALETTE_01.asc). Il dessine **avant** de lire une palette IFF, fait Set/Get et 64 étapes RGB par VBL. **Gate B ne sera PASS qu'après exécution et confirmation de la capture utilisateur.** Une transition pilotée par AMOS n'est pas une commande `Fade` native.

## Sous-jalons restants de M13

1. **R28 candidate :** chargement CMAP indépendant depuis **IFF palette seule Personal Paint/Deluxe Paint** ou IFF image + `Set/Get`. L'extension ne dépend ni du fichier `.pal` ni d'aucun format maison. Pour vérifier sur un export réel PPaint, choisir son fichier dans le [test R28 actif](../tests/current/M13_R28_PALETTE_01.asc). Les premiers effets se pilotent en AMOS avec `Set` à chaque VBL.
2. **Après la validation R28 :** états de palette et copie/restauration, **sauvegarde sur disque au format standard IFF `FORM ILBM` + `CMAP`** (export compatible paint programs, sans format propriétaire ; détails à valider sur un fichier PPaint), puis API dédiée **Fade** (noir ↔ couleurs, A → B, nombre d'étapes et résultat final exact) avec politique explicite de temps et de tâches non bloquantes.
3. **Ensuite :** color cycling sur une plage d'indices, sens/intervalle et retour à la palette d'origine ; charges CPU/synchronisation testées en AMOS et WinUAE.

**Interopérabilité :** le format d'import est identifié par la structure **IFF `FORM ILBM` / `CMAP`**, pas par l'extension de fichier. On ignore `BMHD`/`BODY` pour importer les couleurs, et on peut traiter une palette seule. **Un fichier réellement exporté par PPaint n'a pas encore été testé en WinUAE** : compatibilité attendue selon le standard, à confirmer sur un échantillon concret.

**Hors périmètre :** Compiler AMOS et véritable Amiga AGA restent Gates C/D non testées ; les effets Copper RGB4 M7 peuvent surcharger visuellement une palette et devront faire l'objet d'un test de coexistence. Pas de nouvelle branche. `LAST_GOOD` contient R27 validée, **pas** la candidate R28.
