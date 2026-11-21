# M19 P1d — Gate B Runtime WinUAE

**21 novembre 2026.** Deux exécutions du [banc P1d](../tests/current/README.md), `RUN_MODE RUNTIME`, `PRG_STATE 1`. [Lib active et banc au commit de livraison](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/9d10504282101fc550b0e43938289a0cd9eef40c).

| Journal | SHA256 brut | `RETRY_VBL` |
| --- | --- | ---: |
| `M19_P1D_LIMIT_BOB1.TXT` | `92a2deb7a828d00e42b62436325d641e6f8ce0c9fb9f7acb5efbb1cecebbdbeb` | 370 |
| `M19_P1D_LIMIT_BOB2.TXT` | `f5fb9526b920992d15bbdc9961798cfc85147d72eaf9c175f6ba54ffff8b5cad` | 371 |

Chaque journal rapporte `RESULT 1`, `ERR 0`, `PATH_OK`, 405/405 frames, 9/9 étapes, quatre phases hotspot, 42 getters P1a et 12 getters hotspot. Les huit sondes de priorité donnent les huit couleurs attendues. Les huit refus P1d sont corrects et la fermeture efface quatre banques. Les deux journaux diffèrent uniquement par le compteur `RETRY_VBL`.

| P1d, sur les deux pages de chaque passage | Gauche / centre / droite |
| --- | --- |
| Limite globale d'un pixel | 1 / 4 / 1 |
| Limite locale du Bob 1 disjointe de la limite globale | 1 / 5 / 1 |
| Deux Bobs entièrement coupés | 1 / 1 / 1 |
| Limites effacées | 5 / 4 / 5 |

**Gate B PASS sur les mesures** avec 24/24 pixels vérifiés par lancement. Les fichiers ne consignent pas la continuité de la session AMOS ni l'observation visuelle des quatre phases hotspot. Le champ `LIB_SHA256` est l'empreinte attendue inscrite dans l'ASC. Gate C AMOS Compiler et Gate D Amiga physique P1d à tester. P0 reste `LAST_GOOD`.
