# Prototypes AMOS — hors distribution

**Consigne auteur (23 novembre 2026) :** `examples/` contient exclusivement les exemples diffusés avec `AMOSPro_AGA.Lib`. Tout test préparatoire, sonde ou source non validée pour la distribution va dans `tests/proto/`. La CI interdit les prototypes dans `examples/`.

| Sous-dossier | Contenu |
| --- | --- |
| [`sprite_s0_viewport/`](sprite_s0_viewport/README.md) | Sonde expérimentale ViewPort/Sprite S0 |
| [`agsp_bank/`](agsp_bank/AGSP_BANK_SAVELOAD.asc) | DATA AGSP : **Gate B Runtime PASS** (Load/Save), [preuves](../../docs/M19_S1_P1B_AGSP_DATA_AMOS_SAVELOAD_2026-11-22.md) ; Compiler C volontairement non testé |
| [`agsp_capture/`](agsp_capture/README.md) | Capture Sprite AGSP, nouveau token de test `Get AGA Sprite`, Runtime WinUAE non exécuté ; candidate uniquement dans les artefacts CI | 
| [`agtm_prototype/`](agtm_prototype/README.fr.md) | Banque DATA AGTM et benchmark mosaïque (essais WinUAE reçus le 23/11/2026) |

| [`t06_pattern/`](t06_pattern/README.md) | T06A : cible bitmap, FAIL L2 puis PASS L2b Runtime, source inchangée |
| [`t06_pattern_safe/`](t06_pattern_safe/README.md) | T06B : Pattern après Swap, Runtime PASS 12/12, 36 swaps |
| [`l3_resources/`](l3_resources/README.md) | T14A : 26 Open/Close, curseur, mesures Chip/Fast ; préflight PASS, Runtime à exécuter |

Ne pas confondre ce dossier avec `tests/current/` (un seul ASC de campagne) ni `tests/passed/` (archives protégées). Les cinq fichiers ASC/ABK déplacés conservent leurs blobs Git **strictement identiques** ; seuls les README et les chemins des scripts sont adaptés.

[Compte rendu WinUAE AGTM](../../docs/AGTM_WINUAE_PROTOTYPES_2026-11-23.md).

| [`l3_cache/`](l3_cache/README.md) | T11A FICON/FICHIP restaging et mémoire, préflight PASS, Runtime à exécuter |
