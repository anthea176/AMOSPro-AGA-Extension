# AGAPIC v2 / R82 — Gate A native complète PASS (14/11/2026)

**Statut : R82 v0.13.27 candidate unique dans `dist/AMOSPro_AGA.Lib` (64 112 octets, SHA256 `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36`).** Gate A CPU/ABI intégrée PASS, WinUAE B / Compiler C / matériel D NON TESTÉES. La R81 v0.13.26 (59 972 octets, SHA256 `9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4`) demeure l'unique `LAST_GOOD` promue, strictement protégée dans `dist/AMOSPro_AGA_LAST_GOOD.Lib`. Travail sur `main` uniquement.

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

## Budget 16 bits — candidate unique R82 installée après validation native

| Mesure | R81 LAST_GOOD | R82 candidate active |
|---|---:|---:|
| Taille `.Lib` | 59 972 octets | **64 112 octets** |
| Dernière unité AP20 (dispatcher compris) | 57 034 octets | **60 972 octets** |
| Plafond du pont Compiler V2 | 65 534 octets | **65 534 octets** |
| Marge disponible | 8 500 octets | **4 562 octets** |
| Commandes / entrées AP20 | 70 / 77 | **74 / 81** |

SHA256 **de la candidate unique installée** : `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36`. La représentation antérieure de conception en mémoire faisait 64 124 octets, SHA256 `431968eec32b03ca1f7e99091690e6230b69d6f1a0e5ec6f88ff3cde34689f90`. Les 12 octets d'écart proviennent du titre/version de candidature ; le monolithe natif reste inchangé. Aucun second binaire de travail n'a été créé.
Croissance native de `Aga Image Draw` : +422 octets ; `Aga Image Region` : +400 octets ;
nouveaux wrappers Bank : 122 + 122 + 1 298 + 1 558 octets.

Le `BSR.L` MC68020 résout l'éloignement des routines AGAPAL historiques mais
**ne supprime pas** le plafond de 65 534 octets. Le builder `build_agapic_v2_r82_full_preview.py`
et `aga_compiler_capacity.py` le contrôlent avant toute publication.

## Banc AMOS / WinUAE activé (non exécuté)

- `tests/current/AGAPIC_R82_V2_BANK_PALETTE_01.asc` : seul ASC actif, copie strictement identique au fichier de conception `tests/design/`; test 320×256, 256 couleurs,
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

1. **R81 demeure `LAST_GOOD` protégée** ; seule la R82 candidate occupe maintenant `dist/AMOSPro_AGA.Lib` et son seul ASC actif est sous `tests/current/`. Les preuves antérieures restent historiques, non écrasées.
2. Le SHA256 de la R82 active est verrouillé ; les contrôles d'identité doivent exiger le constructeur déterministe R82 et la référence R81 inchangée.
3. Gate B : lancer le test sous **AMOS interprété / WinUAE**, lire le journal
   `RAM:AGAPIC_R82_INTERPRETED.TXT`, vérifier palette et rendu visuel.
4. Gate C : **compiler une seule fois en fin de chantier**, après Gate B et
   les regressions du moteur ; conserver le journal compilé.
5. Gate D : Amiga AGA physique, séparé. Ne pas promouvoir R82 avant
   l'accord explicite de l'auteur et les preuves de validation.

**Aucune Gate B, C ou D R82 n'est revendiquée à ce stade.**
