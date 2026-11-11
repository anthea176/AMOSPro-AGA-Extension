# M13 / R28 0.10.0 — palette AGA 24 bits : premier incrément

**11 novembre 2026 — prototype 68000 en source, tests CPU/CI à exécuter, WinUAE NON TESTÉ.** M13 doit aboutir à une gestion complète : palettes indépendantes des pixels, couleurs RGB, fades, color cycling, sauvegarde/restauration. **Ce R28 n'est que le socle chargement/écriture/lecture**, pas l'achèvement de M13. Le binaire courant reste R27 0.9.3 (Gates A+B PASS sur ses scénarios).

## Audit source et ABI AmigaOS

- L'écran AGA propre à l'extension est un **Screen Intuition privé**. Son ViewPort est à \`Screen+44\` et \`ViewPort.ColorMap\` à \`Screen+48\`. Le \`ColorMap.Count\` (UWORD, offset +2) est vérifié ; l'accès n'est pas lié aux écrans gérés par AMOS.
- L'ancien loader M5 contient déjà une méthode validée de construction de tables CMAP RGB8 → fractions RGB32, suivie de \`graphics.library/LoadRGB32\` (**LVO -882**, \`A0=ViewPort, A1=table\`). L'Autodoc officiel indique que **LoadRGB32 est plus rapide que SetRGB32 même pour une seule couleur** et permet de charger toutes les entrées, y compris celles non utilisées.
- \`graphics.library/GetRGB32\` (**LVO -900**) prend \`A0=ColorMap\`, \`D0=premierPen\`, \`D1=nombre\`, \`A1=table\`. Trois LONGs RGB32 donnent les couleurs. L'extension ne lit pas directement la table hardware/Copper.
- Le **format CMAP** d'un ILBM est un tableau de triplets RGB8. La version R28 ne copie **jamais** le chunk BODY et accepte un **FORM ILBM avec CMAP valide**, même sans BMHD/BODY. Elle rejette les tailles CMAP non multiples de 3, le surdimensionnement et les chunks dupliqués.
- **Modes ciblés :** indices 0 à \`min(2^depth,ColorMap.Count)-1\` pour écran indexé AGA de profondeur 1–8. **HAM, EHB et dual playfield refusés**, en attendant un contrat spécialisé. Aucun accès direct à BPLCON3 ou COLORxx.
- L'appel \`LoadRGB32\` dépend du ColorMap du ViewPort, **pas du back BitMap** : aucune sonde \`Safe\` ne doit être nécessaire pour la palette. \`Aga Palette Set\` ne bloque pas sur le VBL ; le programme peut synchroniser une animation avec \`Aga Wait Vbl\`. \`Aga Palette Load\` conserve la synchronisation \`WaitTOF\` de M5, une fois après le chargement.

Source primaire à consulter : Amiga NDK39 \`graphics/view.h\`, les Autodocs \`LoadRGB32\` / \`GetRGB32\` et [les règles locales sur CMAP](../EXTENSION_SOURCE_RULES.md).

## Trois fonctions expérimentales R28

| API AMOS projetée | Résultat | Règle |
|---|---|---|
| \`_OK=Aga Palette Load(_FILE$)\` | \`1\` réussite / \`0\` échec | Charge seulement les entrées RGB d'un **FORM ILBM** (CMAP), sans modifier les pixels du buffer ni le mode écran. Le chemin est un descripteur chaîne AMOS, comme \`Aga Iff Load\`. |
| \`_OK=Aga Palette Set(_PEN,_R,_G,_B)\` | \`1\` / \`0\` | Modifie un index par trois composantes **0..255** ; un appel \`LoadRGB32\` court, sans attente VBL intégrée. |
| \`_RGB=Aga Palette Get(_PEN)\` | \`$00RRGGBB\` ou \`-1\` si refus | Relit via \`GetRGB32\` depuis le ColorMap actif ; le noir vaut \`0\`, **pas une erreur**. Retour entier positif sur 24 bits. |

**Périmètre AP20 :** 3 tokens ajoutés après les 31 existants, avec trois segments en fin de HUNK ; les 36 segments anciens restent identiques octet pour octet, et \`GetP\` est ajouté au segment texte final 36 pour établir la nouvelle frontière. 40 segments au total. **Les liens BSR clavier/souris R23 ne changent pas**, car tout ajout suit le dernier segment existant. Toute différence non prévue doit bloquer Gate A.

**État :** seules les sources \`m13_palette_r28_emit.py\`, \`build_m13_palette_r28.py\` et \`test_m13_palette_r28.py\` sont préparées. **Aucun fichier .Lib R28 ni test AMOS actif** avant que les tests CPU/CI, la reproductibilité HUNK et l'export source strict soient validés. Les limites restent observables uniquement sur l'écran WinUAE.

## Vérifications nécessaires pour Gate A

- Décompilation Capstone 68000 : instructions valides, cibles de branche alignées, labels internes, aucune instruction illégale.
- Machine Unicorn 68000 : \`D3\` résultat, \`D2=0\`, A3 consommé correctement, hardware SP équilibrée et autres registres sauvegardés. \`Set\` : 32-bit RGB fractions correctes et header \`LoadRGB32\` exact. \`Get\` : lecture des trois fractions et pack RGB8 correct, rejet \`-1\` sans effet.
- \`Load\` : FORM ILBM CMAP sans BMHD/BODY, taille variable de 1 à 256 couleurs, refus des chunks malformés/dupliqués, ressources DOS/Exec libérées sur chaque chemin, **zéro écriture de bitplane**.
- Profondeurs 1, 2, 4, 8 ; indices invalides, octets RGB hors bornes ; ColorMap/Screen/GfxBase invalides ; HAM/EHB/DualPF refusés. Anciennes régressions R27 et anciens tests archivés restent inchangés.
- Seule après Gate A PASS, créer une **candidate versionnée R28** (nouveau SHA) et **un test WinUAE actif** montrant la palette chargée indépendamment des pixels, une couleur changée, un Get exact et une transition couleur par étapes. Ce test ne sera pas assimilé à une API Fade dédiée.

## Sous-jalons restants de M13

1. **R28 :** chargement CMAP indépendant + \`Set/Get\`, premiers effets possibles en AMOS en pilotant \`Set\` à chaque VBL.
2. **Après la validation R28 :** états de palette et copie/restauration, API dédiée **Fade** (noir ↔ couleurs, A → B, nombre d'étapes et résultat final exact) avec politique explicite de temps et de tâches non bloquantes.
3. **Ensuite :** color cycling sur une plage d'indices, sens/intervalle et retour à la palette d'origine ; charges CPU/synchronisation testées en AMOS et WinUAE.

**Hors périmètre :** Compiler AMOS et véritable Amiga AGA restent Gates C/D non testées ; les effets Copper RGB4 M7 peuvent surcharger visuellement une palette et devront faire l'objet d'un test de coexistence. Pas de nouvelle branche ni de promotion de \`LAST_GOOD\`.
