# M13 / R31 0.10.3 — Aga Palette Bank Capture (contrat approuvé)

**Statut au 11/11/2026 : source 68000 et tests Gate A en préparation.**
La commande n'est PAS encore disponible dans la bibliothèque R30 validée
(`dist/AMOSPro_AGA.Lib` / `LAST_GOOD`); ne publier une candidate R31 qu'après
Gate A native CPU + export strict + CI PASS. Gate B WinUAE, C Compiler,
D Amiga physique NON TESTÉES.

## Contrat fonctionnel approuvé

`_OK=Aga Palette Bank Capture(Start(bank),index)` : deux entiers.
`Start(bank)` désigne une banque DATA AMOS encore valide et préalablement
initialisée par `Aga Palette Bank Init`. `index` vaut 0..N-1.

- Lire uniquement la palette `ColorMap` de l'écran Intuition AGA privé actif,
  avec `graphics.library/GetRGB32`; les modes HAM/EHB/dual playfield ne
  sont pas pris en charge.
- Capturer `min(State.LogicalColours, ColorMap.Count)` couleurs, borné à
  1..256 ; chaque composante RGB24 est l'octet fort de son RGB32 AmigaOS.
- Écrire les trois composantes RGB24 consécutives par couleur dans l'unique
  emplacement AGAPAL de 768 octets. Remplacer une palette précédente si
  nécessaire ; mettre à zéro les octets inutilisés et enregistrer le nombre
  de couleurs dans le descripteur WORD à l'offset `16 + 8*index + 4`.
- Ne modifier ni les autres palettes/indices de la banque, ni les pixels,
  ni les couleurs de l'écran, ni le Copper. Aucun VBL implicite.
- Retour entier : 1 = réussite complète ; 0 = rejet/échec **sans écriture
  persistante dans la banque**. Rejeter avant toute écriture une banque
  non DATA/AGAPAL, la mauvaise taille, signature, version, flags, offset
  de l'emplacement, l'index invalide, un écran absent/incompatible et
  une allocation temporaire impossible.
- Banque RGB24 conservée dans le mécanisme DATA/ABK natif AMOS. Stocker
  les RGB32 temporaires dans `Exec/AllocVec` (maximum 3072 octets) et
  les libérer via `FreeVec`, sur Fast RAM si le système le permet.

**Sûreté mémoire :** fournir exclusivement `Start(bank)` d'une banque DATA
native AMOS vivante. `TypeOfMem` ne démontre pas qu'un pointeur arbitraire
appartient réellement à l'allocation et ne rend pas sûre une adresse périmée.

## Gate A et Gate B

Builder : `tools/build_m13_agapal_capture_r31.py`.
Émetteur 68000 : `tools/m13_agapal_capture_r31_emit.py`.
Tests Unicorn/Capstone : `tools/test_m13_agapal_capture_r31.py`.
Ces fichiers s'appuient sur l'archive R30 0.10.2 et protègent SHA256
`446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e`.

La Gate B sera testée dans AMOS interprété avec un écran Intuition 320×256×8,
une banque AGAPAL initialisée par R30, deux captures sur des indices distincts,
une recapture du même index après changement de couleur, la vérification du
nombre de couleurs et des octets RGB24, des rejets d'index/absence d'écran,
puis `Save` / `Erase` / `Load` du vrai fichier ABK et un retour propre.
Une réussite CPU seule ne constitue ni un PASS WinUAE ni une promotion
`LAST_GOOD`. Ce test n'ajoute aucune nouvelle commande d'application de
palette, de fade ou de cycling.

**Règles permanentes :** une seule instruction nouvelle pour R31,
documentation exacte dans README EN et FR avec la candidate Gate A,
test unique actif dans `tests/current/`, archive sans modification et
promotion obligatoire `LAST_GOOD` seulement après PASS WinUAE utilisateur.
Aucune branche nouvelle et aucun autre dépôt.
