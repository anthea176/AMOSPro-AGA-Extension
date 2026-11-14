# AGAPIC v2 / R82 — Gate A native complète PASS (14/11/2026)

**Statut : préparation R82, PAS de binaire installable R82 sur `main`.**
La R81 v0.13.26 demeure `LAST_GOOD` : `dist/AMOSPro_AGA.Lib` et
`dist/AMOSPro_AGA_LAST_GOOD.Lib` identiques (59 972 octets,
SHA256 `9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4`).
Aucune autre branche GitHub n'a été créée.

## Périmètre validé — MC68020 et hôte uniquement

Les deux CI **Artifact integrity** suivantes ont exécuté la Gate A R82 :

- [43628508648 — API palettes + Image Region + AP20 complet en mémoire](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43628508648)
- [43628732478 — ajout du test natif AP20 aux offsets réels après relink](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43628732478)

| Contrôle | Résultat vérifié |
|---|---|
| AGAPIC v1/v2 modèle Python et palettes | **168 aller-retours PASS**, 23 refus |
| Garde de taille Compiler V2 | **14 cas PASS** |
| `Aga Image Draw` v1/v2 | **69 scénarios natifs PASS** |
| `Aga Bank Palette Init/Capture` | **52 scénarios natifs PASS**, `BSR.L`, refus CPU000 |
| `Aga Bank Palette Apply/Fade` AGAPAL/v2 | **63 scénarios natifs PASS**, RGB32, fondus, ABI, ModeID, rejets |
| `Aga Image Region` v1/v2 | **70 scénarios natifs PASS**, crop, masque, pixels, ModeID, refus CPU000 |
| AP20 complet et banque de tokens | **74 commandes**, **81 entrées**, structure PASS |
| Wrappers de palette aux offsets finaux après intégration Region | **19 cas MC68020 PASS** |

Les anciens moteurs AGAPIC v1 et AGAPAL v1 ne sont pas remplacés : le code
R82 utilise des sources/émetteurs distincts, vérifiés par des tests historiques.
Les wrappers `Init/Capture` délèguent aux routines AGAPAL qualifiées ; `Apply/Fade`
dispatchent sur le nom/format de banque. Pour AGAPIC v2, seule la palette RGB24
complète à l'index 0 est prise en compte et un ModeID identique est exigé.

## Budget 16 bits — candidat **en mémoire uniquement**

| Mesure | R81 LAST_GOOD | R82 source assemblée en mémoire |
|---|---:|---:|
| Taille `.Lib` | 59 972 octets | **64 124 octets** |
| Dernière unité AP20 (dispatcher compris) | 57 034 octets | **60 972 octets** |
| Plafond du pont Compiler V2 | 65 534 octets | **65 534 octets** |
| Marge disponible | 8 500 octets | **4 562 octets** |
| Commandes / entrées AP20 | 70 / 77 | **74 / 81** |

SHA256 **de la représentation assemblée uniquement en mémoire** :
`431968eec32b03ca1f7e99091690e6230b69d6f1a0e5ec6f88ff3cde34689f90`.
Il ne correspond pas à un fichier `.Lib` déjà publié dans `dist/`.
Croissance native de `Aga Image Draw` : +422 octets ; `Aga Image Region` : +400 octets ;
nouveaux wrappers Bank : 122 + 122 + 1 298 + 1 558 octets.

Le `BSR.L` MC68020 résout l'éloignement des routines AGAPAL historiques mais
**ne supprime pas** le plafond de 65 534 octets. Le builder `build_agapic_v2_r82_full_preview.py`
et `aga_compiler_capacity.py` le contrôlent avant toute publication.

## Banc AMOS / WinUAE préparé (non exécuté)

- `tests/design/AGAPIC_R82_V2_BANK_PALETTE_01.asc` : test 320×256, 256 couleurs,
  ModeID PAL LowRes `$00021000`, palettes AGAPAL et AGAPIC v2, fondu,
  compatibilité AGAPIC v1, rejets, journal RAM: et fermeture.
- `tests/design/R82_AGAPIC_V2_BANK10.abk` : image 96×64×8 masquée,
  palette RGB24 complète, ModeID PAL LowRes, SHA256
  `11a5102f05bfda8372ccdcf2a5b8eec2c5d1a5c80d2cbb83b5d563e0abc667f0`.
- `tests/design/R82_AGAPIC_V1_BANK12.abk` : image équivalente au format v1,
  SHA256 `09b3badeec687732010c00c2152fa51df609d2000d64e915a64f4dbd10fa71e8`.
- Les outils `tools/m16_agapic_v2_winuae_fixture.py` et
  `tools/test_agapic_v2_r82_amos_design_static.py` vérifient la génération des
  banques et la syntaxe structurale AMOS. Cela **ne constitue pas** un test AMOS.

## Garde-fous et prochaine validation

1. **R81 conserve sa protection et son ASC actif unique** ; les nouveaux exemples
   sont dans `tests/design` et ne prétendent pas être PASS WinUAE.
2. Avant l'installation d'une **candidate unique R82** dans `dist/AMOSPro_AGA.Lib`,
   les contrôles de l'identité active doivent être mis à jour sans dégrader les
   tests historiques ni changer `LAST_GOOD`.
3. Gate B : lancer le test sous **AMOS interprété / WinUAE**, lire le journal
   `RAM:AGAPIC_R82_INTERPRETED.TXT`, vérifier palette et rendu visuel.
4. Gate C : **compiler une seule fois en fin de chantier**, après Gate B et
   les regressions du moteur ; conserver le journal compilé.
5. Gate D : Amiga AGA physique, séparé. Ne pas promouvoir R82 avant
   l'accord explicite de l'auteur et les preuves de validation.

**Aucune Gate B, C ou D n'est revendiquée à ce stade.**
