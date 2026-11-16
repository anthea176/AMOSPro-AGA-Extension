# Test actif — M19 P0b : Bobs AGA multi-images, masques indépendants MC68020

**Bibliothèque unique de test :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib),
**82 376 octets**, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`.
**Programme AMOS actif unique :** [`M19_P0B_MC68020_MASK_BANK.asc`](M19_P0B_MC68020_MASK_BANK.asc).

**Cible native : MC68020 minimum, sans fallback 68000.** Les tests fonctionnels
se font sous **WinUAE 68030 + JIT activé, AGA PAL** ; le **68020 sans JIT** est
réservé aux benchmarks, pas à ce test.

## Ce que teste l'ASC

- Régression P0a : `Aga Bob Bank 24`, trois captures `Get AGA Bob`, insertion
  au milieu puis remplacement d'une image, sans perdre les autres ; tailles
  `552`, `976`, `1528`, `1032` octets.
- P0b : `Make AGA Bob Mask I,C` avec indices transparents **0, 127 et 37**,
  bitplane de masque indépendant de la couleur, largeur **17** non alignée ;
  tailles AGBO successives **1092 / 1094 / 1142** octets.
- `No AGA Bob Mask I` pour deux images : **1140 / 1092** octets. Suppression
  répétée sur une image déjà opaque = **aucune nouvelle génération**.
- Contrôle des flags du répertoire, décalage du masque et des mots `$7FFF/$8000`
  (pixel de couleur 0 transparent, autres pixels opaques), puis sauvegarde native
  AMOS, `Erase`, `Load`, resélection et recontrôle du masque.

**Aucune ressource externe `.IFF` ou `.ABK` n'est nécessaire** : l'ASC dessine
lui-même les pixels et crée le fichier `RAM:M19_P0B_68020_BOBS.ABK`.
La banque AMOS **24 doit être libre** dans le nouveau programme au lancement.

## Essai WinUAE

1. Installer exactement [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) sous
   le nom `AMOSPro_AGA.Lib` dans le slot AGA habituel de `APSystem`, puis redémarrer AMOS.
2. Dans un programme vierge, utiliser **Project → Merge ASCII** pour importer
   `M19_P0B_MC68020_MASK_BANK.asc` ; ne pas utiliser `Load` sur l'ASCII.
3. Exécuter en Runtime, puis lire `RAM:M19_P0B_RUNTIME.TXT` (ou
   `RAM:M19_P0B_INTERPRETED.TXT`). Attendu : `RESULT 1`, `ERR 0`, `VERDICT PASS`,
   `ABK_RELOADED 1`, `CLOSE_RETURNED 1`. **Gate B Runtime PASS**
   selon le journal utilisateur du 16/11/2026 (`PRG_STATE 1`).
4. Compiler **le même ASC** avec le véritable AMOS Compiler V2, exécuter le
   binaire obtenu et lire `RAM:M19_P0B_COMPILED.TXT`. **Gate C PASS** selon
   le journal utilisateur du 16/11/2026 (`PRG_STATE -1`, `ERR 0`,
   `CLOSE_RETURNED 1`). Aucun gel/Guru signalé pendant ce scénario.

## Preuves et protections

- **Gate A P0b CPU MC68020 : PASS** : 116 scénarios des deux commandes,
  deux placements de code, plus 104 scénarios du noyau privé (services AMOS simulés).
  [CI P0b](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43758224492).
- **Gate B P0b Runtime WinUAE : PASS** (`PRG_STATE 1`, `RESULT 1`, `ERR 0`).
  **Gate C P0b AMOS Compiler : PASS** (`PRG_STATE -1`, `RESULT 1`, `ERR 0`).
  **Interpréteur strict** (`PRG_STATE 0`) et **Gate D** : non testés.
  Voir le [rapport de preuves M19 P0b du 16/11/2026](../../docs/M19_P0B_GATES_BC_2026-11-16.md).
  L'ABK Runtime et l'ABK Compiled sont identiques octet pour octet.
- **R84 `dist/AMOSPro_AGA_LAST_GOOD.Lib` intouchée**, aucune promotion.
  La base R88 native est conservée à l'identique dans son archive existante.
- L'ASC P0a antérieur reste récupérable dans l'historique Git, sans deuxième
  test actif ni modification de `tests/passed/`.
