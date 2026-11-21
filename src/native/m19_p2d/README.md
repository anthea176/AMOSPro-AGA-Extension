# M19 P2d - trois modules natifs réellement éditables

Ce dossier contient du **source assembleur Motorola MC68020 écrit à partir
des émetteurs Python officiels**, et non une copie du désassemblage. Il
restaure trois blocs de la bibliothèque P2d : Bob Planes (P2c) et Bob Auto
Update / Swap / Close (P2d). Les routines `p2c_reset_slot` et `p2d_close`,
auparavant représentées en `DC.B`, sont désormais des instructions.

## Périmètre exact

- Module : `M19_P2D_CONTROLS_MC68020.s` ; routines `p2d_public_auto_update`,
  `p2d_public_swap`, `p2d_close` ; état `p2d_mode` (12 octets de données).
- Module : `M19_P2C_PLANES_MC68020.s` ; routines `p2c_public_planes`,
  `p2c_apply_planes` et `p2c_reset_slot`, octets `$0B4C4..$0B58B` (**200
  octets**).
- Position totale des trois modules : octets BOBS `$0B4C4..$0B729`, soit
  **1 176 octets**. Les bornes actuelles sont fixes jusqu'à migration du linker AP20.
- Toutes les instructions de ces trois blocs sont écrites avec leurs mnémoniques
  et des labels sémantiques. Le seul `DCB.B` des modules réserve la structure
  d'état ; aucune instruction du bloc n'est en `DC.B` ou `DC.W`.
- Constantes CPU, structures et offsets : déclarés dans le fichier `.s`,
  contrôlés contre les émetteurs du jalon.
- Les autres unités restent, provisoirement, celles de
  `src/asm_migration/m19_p2d/` (audit reconstruit). **Ce n'est pas encore le
  remplacement intégral du builder Python.**

## Un seul fichier maitre pour compiler

**`M19_P2D_LINKED_EDITABLE.s` est le point d'entrée unique de vasm.**
Il inclut `M19_P2D_BOBS_EDITABLE.s` et les modules P2c/P2d écrits à la main ;
les autres unités AGA, C2P et IFF restent incluses depuis
`src/asm_migration/m19_p2d/` en attendant leur migration.

**Compilation directe, sans Python** (Windows) : à la racine, avec
`tools/vasmm68k_mot.exe` :

```bat
BUILD_P2D_ASM_DIRECT.bat
```

Sortie : `src/generated/p2d_editable/M19_P2D_DIRECT_ASM_UNTESTED.Lib`.
Elle est identique au binaire officiel lorsque les sources sont inchangées,
ce que vérifie la CI ; toute édition rend le fichier **non validé**.
Ce mode direct n'impose pas le contrôle de taille/contrat AP20 avant l'écriture.

**Compilation avec garde-fous Python + vasm** :

```bat
BUILD_P2D_ASM.bat
```

Ou directement :

```bat
py -3 tools\build_m19_p2d_editable_asm.py --vasm tools\vasmm68k_mot.exe
```

Sortie : `src/generated/p2d_editable/M19_P2D_ASM_REBUILT_CHECK.Lib`.
Cette reconstruction non modifiée doit être **octet-identique** à la Lib P2d
source (136 020 octets, SHA256
`ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`).
Ce résultat n'est pas publié sous `dist/`.

## Modifier et réassembler

1. Éditer un des deux fichiers `.s` sous `src/native/m19_p2d/`.
2. Pour une modification conservant la longueur du bloc, lancer :

   ```bat
   BUILD_P2D_ASM.bat --allow-edited
   ```

3. Lire `src/generated/p2d_editable/M19_P2D_EDITED_UNTESTED.Lib`.
   Le script rejette un changement d'AP20, de longueur, des autres unités
   ou de `LAST_GOOD`. **Ne pas installer une candidate modifiée sans tests
   WinUAE Runtime et AMOS Compiler.**

Lancer `BUILD_P2D_ASM.bat --self-test-edit` pour une preuve reproductible
sans modifier le dépôt : la CI remplace temporairement `moveq #1,d3` par
`moveq #2,d3` dans `p2d_set_done`, réassemble la bibliothèque complète,
vérifie que **seul l'octet de cet opcode a changé**, puis recommence avec
`p2c_set_fail` (`moveq #0,d3` → `#1,d3`). La structure AP20 reste valide.
Les candidats modifiés sont effacés avec le dossier temporaire.

## Données P2b identifiées depuis l'émetteur source

Le bloc BOBS `+$0A4C0..+$0B4C3` représente **4 100 octets de données**, et non des instructions absentes : `p2b_owner` (4 octets) et `p2b_slots` (64 slots de 64 octets). Les centaines de lignes `DC.B` sont remplacées par [`M19_P2B_SLOTS_DATA_MC68020.s`](M19_P2B_SLOTS_DATA_MC68020.s) avec `DC.L 0` et `DCB.B` à taille déclarée. Les positions et les octets sont vérifiés contre `m19_p2b_bob_flip_emit.py` et par vasm dans la reconstruction complète.

**Distinction :** 1 176 octets de code P2b/P2c/P2d en source maintenable (une exception non canonique `MULU.L` documentée) **et** 4 100 octets de données P2b identifiées. Le reste du moteur demeure partiellement issu de l'audit.

## Troisième module : P2b retournement planaire

`M19_P2B_PLANAR_MC68020.s` remplace **562 octets** (`BOBS +$0A28E..$0A4BF`) de code précédemment en `DC.B` : retournement horizontal et vertical, mesure/limites de géométrie, traitement ligne/plan et allocation Chip via Exec. Il est reconstruit depuis `m19_p2b_planar_orientation020_emit.py`, pas depuis les heuristiques du désassembleur. Le constructeur vérifie l'identité du fragment émis, la reconstruction P2d complète et une modification ciblée du `MOVEQ` de refus.

Les trois blocs métier réécrits représentent désormais **1 176 octets** (P2b 562 + P2c 200 + P2d 414). Le reste des unités et du wrapper AP20 demeure issu de l'audit; *aucune promesse de migration intégrale*. Les modifications restent à longueur constante jusqu'à migration de la relocation AP20.

## Prochaine migration

Ces trois modules sont **une étape**, pas une prétention de couverture intégrale.
Le reste de la bibliothèque doit être migré depuis les émetteurs Python,
avec un inventaire des octets de code encore traités en données, avant
qu'on puisse supprimer la dépendance aux fichiers d'audit et disposer d'un
projet vasm intégralement symbolique et maintenable. Seuls les trois modules `M19_P2C_PLANES_MC68020.s` et
`M19_P2D_CONTROLS_MC68020.s` sont considérés comme **sources métier
maintenus à la main**. Le fichier BOBS principal est encore largement issu
de l'audit des octets, donc ce n'est pas un code source integral definitif.

Gates : **A (identité vasm / essai de changement) uniquement** une fois
la CI verte ; **B/C/D non effectuées** pour les nouvelles éditions natives.
