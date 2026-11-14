# R82 v0.13.27 — WinUAE Runtime et AMOS Compiler PASS (14/11/2026)

## Statut

**R82 Gates A/B Runtime/C Compiler : PASS dans le périmètre du banc AGAPIC.**
**Gate B AMOS strictement interprété : NON DOCUMENTÉE** (aucun journal
`PRG_STATE 0` transmis). **Gate D Amiga AGA physique : NON TESTÉE.**
R82 a été **autorisée à la promotion** après réception des journaux ; sa
qualification Runtime/Compiler ci-dessous constitue la preuve préalable.
La R81 reste reconstructible et consultable dans l'historique Git. Aucune nouvelle branche.

Binaire testé annoncé par les journaux : `R82 V0.13.27 NATIVE CANDIDATE`.
L'artefact GitHub actif est `dist/AMOSPro_AGA.Lib` : **64 112 octets**,
SHA256 `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36`, **74 commandes / 81 entrées AP20**,
monolithe Compiler V2 **60 972 octets**, **4 562 octets de marge**.
Cette identification est celle du test ; les logs RAM ne contiennent pas de
hachage du fichier effectivement installé sur WinUAE.

Les journaux originaux fournis par l'auteur, sans réécriture de leurs
valeurs et en conservant le format de lignes CRLF AmigaDOS, sont archivés
dans [le journal Runtime](evidence/AGAPIC_R82_RUNTIME_2026-11-14.TXT)
et [le journal Compiler](evidence/AGAPIC_R82_COMPILED_2026-11-14.TXT).

## Preuves utilisateur — deux journaux WinUAE

Source exacte des valeurs : fichiers fournis le 14/11/2026
`AGAPIC_R82_RUNTIME.TXT` et `AGAPIC_R82_COMPILED.TXT`, produits par
`tests/current/AGAPIC_R82_V2_BANK_PALETTE_01.asc`.

| Champ journal | Runtime | Compiler |
|---|---:|---:|
| `RUN_MODE` | `RUNTIME` | `COMPILED` |
| `PRG_STATE` | `1` | `-1` |
| `CPU` | `68030` | `68030` |
| `CPU_ATTNFLAGS` | `32823` | `32823` |
| `RESULT` | **1** | **1** |
| `VERDICT` | **PASS** | **PASS** |
| `PALETTE_V2_OK`, `PALETTE_AGAPAL_OK` | 1 / 1 | 1 / 1 |
| `FADE_V2_OK`, `FADE_AGAPAL_OK` | 1 / 1 | 1 / 1 |
| `INIT_OK`, `CAPTURE_OK` | 1 / 1 | 1 / 1 |
| `DRAW_V1_OK`, `DRAW_V2_OK` | 1 / 1 | 1 / 1 |
| `REGION_V1_OK`, `REGION_V2_OK` | 1 / 1 | 1 / 1 |
| `INVALID_OK`, `SWAP_OK` | 1 / 1 | 1 / 1 |
| `ERR` | **0** | **0** |
| `CHIP_BEFORE` | 1 383 904 | 1 350 440 |
| `CHIP_AFTER` | 1 383 904 | 1 350 440 |
| **Delta Chip RAM** | **0** | **0** |
| `FAST_BEFORE` | 130 312 496 | 130 158 888 |
| `FAST_AFTER` | 130 312 496 | 130 158 888 |
| **Delta Fast RAM** | **0** | **0** |
| `CLOSE_RETURNED` | **1** | **1** |

Les deltas nuls prouvent le retour aux valeurs initiales au terme de ces
deux exécutions ; ils ne démontrent pas l'absence de fuite dans tous les
scénarios possibles.

## Observation graphique

La capture WinUAE transmise par l'auteur montre le montage sur fond noir :
trois images dans la rangée supérieure, une image en bas à gauche et deux
régions recadrées en bas. Palettes multicolores visibles, images et masques
rendus, sans artefact fatal apparent. L'auteur confirme que le test fonctionne.
La capture constitue une vérification visuelle, **pas** une comparaison
pixel par pixel automatisée ni une mesure de performance.

## Qualification et limites

- **Gate A : PASS** — émulation native MC68020 et contrôles d'intégrité AP20
  du binaire R82. CI [43630405052](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43630405052)
  job ciblé R82 PASS.
- **Gate B Runtime : PASS** — WinUAE, `RUN_MODE RUNTIME`,
  `PRG_STATE 1`, écran/palette/dessin/régions/rejets/fermeture et RAM PASS.
- **Gate C Compiler : PASS** — WinUAE, `RUN_MODE COMPILED`,
  `PRG_STATE -1`, mêmes tests PASS ; la limite 16 bits reste respectée.
- **Gate B interpréteur pur : non documentée** — aucun `PRG_STATE 0`
  dans les deux fichiers reçus, ne pas l'inventer.
- **Gate D : NON TESTÉE** — aucun essai Amiga physique.
- **Promotion : EXPLICITEMENT AUTORISÉE** — référence promue R82
  `dist/AMOSPro_AGA_LAST_GOOD.Lib` : 64 112 octets, SHA256
  `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36`. R81 v0.13.26 est historique, disponible
  via le commit antérieur et son constructeur SHA épinglé.

**Conclusion : R82 est validée en Runtime et compilé pour ce banc WinUAE,
avec décompte de RAM inchangé et fermeture propre ; elle a reçu
l'autorisation de promotion, sans qualification physique.**
