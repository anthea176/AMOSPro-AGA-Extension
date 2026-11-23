# Prototypes AMOS — hors distribution

**Consigne auteur (23 novembre 2026) :** `examples/` contient exclusivement les exemples diffusés avec `AMOSPro_AGA.Lib`. Tout test préparatoire, sonde ou source non validée pour la distribution va dans `tests/proto/`. La CI interdit les prototypes dans `examples/`.

| Sous-dossier | Contenu |
| --- | --- |
| [`sprite_s0_viewport/`](sprite_s0_viewport/README.md) | Sonde expérimentale ViewPort/Sprite S0 |
| [`agsp_bank/`](agsp_bank/AGSP_BANK_SAVELOAD.asc) | Test du format DATA AGSP et ressource ABK |
| [`agtm_prototype/`](agtm_prototype/README.fr.md) | Banque DATA AGTM et benchmark mosaïque (essais WinUAE reçus le 23/11/2026) |

Ne pas confondre ce dossier avec `tests/current/` (un seul ASC de campagne) ni `tests/passed/` (archives protégées). Les cinq fichiers ASC/ABK déplacés conservent leurs blobs Git **strictement identiques** ; seuls les README et les chemins des scripts sont adaptés.

[Compte rendu WinUAE AGTM](../../docs/AGTM_WINUAE_PROTOTYPES_2026-11-23.md).
