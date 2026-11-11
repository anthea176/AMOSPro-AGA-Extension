# M13 / R31 0.10.3 — Aga Palette Bank Capture (candidate Gate A PASS)

## R31 0.10.3 — candidate AGAPAL Capture : Gate A CPU PASS / Gate B WinUAE en attente (11/11/2026)

**Nouvelle instruction unique :** `_OK=Aga Palette Bank Capture(Start(bank),index)` ; index 0..N-1. Lecture `GetRGB32` de la `ColorMap` de l'écran AGA Intuition privé actif, conversion en RGB24 (octet de poids fort de chaque composante), écriture du seul emplacement AGAPAL sélectionné (768 octets et nombre réel 1..256). Un nouvel appel écrase cet emplacement et remet les octets inutilisés à zéro, sans modifier les autres palettes ni l'affichage. Retour entier 1/0 ; rejet avant écriture sur index, banque, en-tête AGAPAL, écran ou allocation temporaires invalides. **Fournir uniquement le `Start(bank)` d'une banque DATA AMOS vivante et déjà initialisée par R30**, jamais un pointeur libre/arbitraire.

**Candidat publiable Gate A :** `dist/AMOSPro_AGA.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.3_AGAPAL_BANK_CAPTURE_R31.Lib`, **R31 0.10.3**, **18 520 octets**, SHA256 `0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41`. **107 scénarios natifs CPU 68000 PASS**, export 68000 strict PASS et [CI source complète 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43027092394); résultat CI du commit de publication à contrôler séparément. **Gate B AMOS/WinUAE NON TESTÉE**, Gates C Compiler/D Amiga réel NON TESTÉES.

**Protection R30 :** `dist/AMOSPro_AGA_LAST_GOOD.Lib` demeure la **R30 0.10.2 validée WinUAE**, 17 824 octets, SHA256 `446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e`, identique à l'archive figée R30. Le test unique à exécuter via `Project → Merge ASCII` est [`tests/current/M13_R31_AGAPAL_CAPTURE_01.asc`](../tests/current/M13_R31_AGAPAL_CAPTURE_01.asc) ; il remplace banques AMOS 10/11 et `RAM:R31_AGAPAL_CAPTURE.ABK`. **Aucune promotion de `LAST_GOOD` avant un PASS explicite WinUAE utilisateur.** Aucune autre commande (import/apply/fades/cycling) n'est autorisée sans discussion séparée.

---



**État avant publication (historique) :** la source était en préparation. Désormais, le binaire candidat R31 est distribué dans `dist/AMOSPro_AGA.Lib` après Gate A CPU/CI PASS ; R30 reste `LAST_GOOD`. Gate B WinUAE/C Compiler/D matériel non testées.

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

## Protocole WinUAE de Gate B

Installer la candidate [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) R31 0.10.3 sous son nom exact dans `APSystem`, puis quitter et relancer AMOS. Dans un programme vide, choisir **Project → Merge ASCII** avec [`tests/current/M13_R31_AGAPAL_CAPTURE_01.asc`](../tests/current/M13_R31_AGAPAL_CAPTURE_01.asc). **Attention : remplace les banques DATA 10 et 11 et `RAM:R31_AGAPAL_CAPTURE.ABK`.**

Le test ouvre l'écran AGA 320×256×8, crée une banque AGAPAL de huit emplacements, capture la palette avec le pen 28 vert en index 0, passe le pen au rouge et capture l'index 1, puis au bleu et recapture l'index 0. Il vérifie que l'index 1 reste rouge, que le seul index 0 a changé, que le pen 224 est conservé, que les deux descripteurs indiquent 256 couleurs, et que `Aga Palette Get(28)` est inchangé par la capture. Les indices -1/8, une banque mal dimensionnée et l'absence d'écran doivent être refusés. La sauvegarde et le rechargement via `Save/Load` AMOS doivent préserver les RGB24.

Sortie attendue : `CAP0 1 CAP1 1 OVER 1`, `GREEN 255 RED 255 BLUE 255`, `COUNT0 256 COUNT1 256`, `BEFORE 255 AFTER 255`, `BADNEG 0 BAD8 0 BADSIZE 0`, `NOSCREEN 0 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `RELOAD 255 255 10 56`, `CLOSED -1 RESULT 1` et `CLOSE RETURNED`. La preuve de Gate B exige le résultat réel et le retour normal à AMOS ; **ne pas promouvoir R31 avant**.
