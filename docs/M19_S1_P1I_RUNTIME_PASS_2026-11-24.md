# S1-P1i — Gate B Runtime capture AGSP PASS (24 novembre 2026)

**Auteur :** remise des trois fichiers originaux après installation de la candidate P1i et lancement du protocole convenu, puis « ok va y » pour figer la preuve et préparer S1-P2. **Aucune promotion de LAST_GOOD.**

Base canonique sur main : P1i, 142968 octets, SHA256 `2f3cb4adf56121f62aeccf9916d680ba3e2857c9bdbe0fda777d1d7eaed7ffc3`, Git blob `c7e13993bc32e17cb96c8e8ee68e8b5a1dffeb1b`, 102 commandes / 208 AP20, MC68020+. [Gate A complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45492646401) PASS sur la candidate. ASC [GET_AGA_SPRITE.asc](../tests/proto/agsp_capture/GET_AGA_SPRITE.asc), blob `8e0cd050ebf72a1150a20d1cc5d480e39cf79024`, SOURCE_TAG M19_S1P1E_GET_AGSP_V1 ; [IFF](../tests/proto/agsp_capture/AGSP_CAPTURE_320X256.iff) SHA256 `b39aa201dddd878405c828687973b3b874ae5d0f8cc1f09d1617dda7ff0628b9`. Attribution du Runtime à P1i par la séquence conversationnelle ; le log ne contient pas l'empreinte de la Lib réellement installée ni la configuration CPU/JIT détaillée.

## Preuves originales

| Fichier | Taille | SHA256 |
|---|---:|---|
| [Runtime TXT](evidence/M19_S1P1I_AGSP_RUNTIME_2026-11-24.TXT) | 216 (CRLF) | `52d251873ecf3dff4ef9852bec32bf82594dcb640cd81d7cdc8eeeffdbd57c1e` |
| [SAVED ABK](evidence/M19_S1P1I_AGSP_SAVED_2026-11-24.ABK) | 372 | `54965e4d4ed0e59c7a77ddaeb8cb43a1926305bd669358d7bc4f77eb928f8d9f` |
| [FINAL ABK](evidence/M19_S1P1I_AGSP_FINAL_2026-11-24.ABK) | 532 | `225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93` |

Journal : PRG_STATE 1, RUN_MODE RUNTIME, RESULT 1, ERR 0, CAPTURED 3, REFUSED 1, SAVED 1, RELOADED 1, RECAPTURED 1, VERDICT PASS_CAPTURE_AGSP_DATA_ONLY.

Analyse locale indépendante : enveloppes AmBk DATA, banque 29, flags 1, tailles avec bit 31 du Save natif $80000168 et $80000208, nom AGASPRT. Construction des payloads attendus selon le motif de la fixture, vérification octet-exacte des 352 et 512 octets. SAVED : IDs 1/2 zone B, génération 4. FINAL : IDs 1/2 B conservés, ID 3 A, génération 5. 1280 pixels au total, 64 transparents et 64 pixels de chaque couleur par image. Palette B locale : 000000,1A73FF,24DC75,FF4628 ; palette A : 000000,FF4628,24DC75,1A73FF. Aucun octet divergent. Les deux banques sont des preuves, pas des fichiers à modifier.

## Limites et suite

Gate B PASS pour la capture, le refus, le remplacement, Save/Load et nouvelle capture. C non testée (reportée), D non testée. La CI générale post-livraison est distincte. LAST_GOOD L2b (136708 octets, blob 2809b4b409eea9e234df1b96bf2b08bd393d8c85) et la Lib P1i restent inchangées. Le test T06A, le prototype ASC et son IFF restent byte-exacts. Aucun transfert vers le DMA.

S1-P2 : préparer une image DMA indépendante en Chip RAM, vérifier les bases de palette du ViewPort et le contrat de retrait avant une API d'affichage. S0d a une preuve visuelle historique B/C, mais FreeSprite ne prouve pas l'arrêt des références DMA. Aucun changement public de Lib dans cette phase.
