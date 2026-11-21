# M19 P2d - première unité native réellement éditable

Ce dossier contient du **source assembleur Motorola MC68020 écrit à partir de
l'émetteur Python officiel**, et non une copie du désassemblage. Il restaure
intégralement le bloc Bob Auto Update / Swap / Close de la bibliothèque P2d,
y compris `p2d_close`, qui restait jusqu'ici sous forme de `DC.B`.

## Périmètre exact

- Module : `M19_P2D_CONTROLS_MC68020.s` ; routines `p2d_public_auto_update`,
  `p2d_public_swap`, `p2d_close` ; état `p2d_mode` (12 octets de données).
- Position actuelle du module : octets BOBS `$0B58C..$0B729`, soit **414
  octets** ; destination fixe jusqu'à migration du linker AP20.
- Toutes les instructions de ce bloc sont écrites avec leurs mnémoniques
  et des labels sémantiques. Le seul `DCB.B` du module réserve la structure
  d'état ; aucune instruction du bloc n'est en `DC.B` ou `DC.W`.
- Constantes CPU, structures et offsets : déclarés dans le fichier `.s`,
  contrôlés contre les émetteurs du jalon.
- Les autres unités restent, provisoirement, celles de
  `src/asm_migration/m19_p2d/` (audit reconstruit). **Ce n'est pas encore le
  remplacement intégral du builder Python.**

## Construire (Windows)

À la racine, avec `tools/vasmm68k_mot.exe` :

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

1. Éditer directement `src/native/m19_p2d/M19_P2D_CONTROLS_MC68020.s`.
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
vérifie que **seul l'octet de cet opcode a changé** et contrôle à nouveau
la structure AP20. Le candidat modifié est effacé avec le dossier temporaire.

## Prochaine migration

Ce module est **une étape**, pas une prétention de couverture intégrale.
Le reste de la bibliothèque doit être migré depuis les émetteurs Python,
avec un inventaire des octets de code encore traités en données, avant
qu'on puisse supprimer la dépendance aux fichiers d'audit et disposer d'un
projet vasm intégralement symbolique et maintenable. Les sources `.s` du
présent dossier restent les seuls fichiers de ce jalon à modifier directement.

Gates : **A (identité vasm / essai de changement) uniquement** une fois
la CI verte ; **B/C/D non effectuées** pour les nouvelles éditions natives.
