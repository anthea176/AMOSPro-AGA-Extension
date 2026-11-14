# AGAPIC R84 v0.13.29 — Gate A native (14/11/2026)

**Candidate sur `main`, NON PROMUE.** Le binaire de travail unique `dist/AMOSPro_AGA.Lib` est obtenu par `tools/build_aga_r84_agapic.py` depuis la R83 SHA-pinnée, sans toucher `dist/AMOSPro_AGA_LAST_GOOD.Lib` (R83).

| Mesure | Valeur |
|---|---|
| R84 `AMOSPro_AGA.Lib` | **67 904 octets** |
| SHA256 candidate | `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` |
| Commandes / AP20 | **76 / 85** |
| Groupes natifs | **3** : C2P 5 558, IFF 2 508, AGA/AGAPIC 56 580 octets |
| Marge Compiler V2 AGA | **8 954 octets** (limite par groupe 65 534) |
| Ajouts natifs | Info **1 088 octets**, capture versionnée **2 510 octets** |
| `RBSR/BSR.W` maximum | 9 000 octets |
| Ancienne `Aga Image Capture` | **code binaire inchangé**, exclusivement v1 |

**Gate A — PASS :** [workflow ciblé](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43644680232), sur vrai cœur MC68020 émulé avec services AMOS/Exec/graphics isolés. Le test structurel couvre le dispatcher, 76 signatures, 85 entrées et les trois modules natifs. `tools/test_r84_agapic_info_native.py` : **44 cas** v1/v2, champs 1..5, métadonnées corrompues et banque invalide. `tools/test_r84_agapic_capture_native.py` : **47 cas** en profondeurs 1/4/8, v1/v2 opaque et masquée, RLE réel, RGB24, ModeID, refus, collision, nettoyage des banques/tampons et retour ABI ; moteur historique v1 préservé. Les tests de format v1/v2 existants passent également. SHA et taille ont été récupérés directement du binaire construit dans la CI, sans recompilation différente.

**Non validées :** WinUAE Runtime Gate B, AMOS Compiler Gate C, mode `PRG_STATE 0` strict, Amiga physique Gate D. La Gate A simulée ne démontre pas le fonctionnement réel du chargeur AMOS, des allocations Intuition/ColorMap ni du Compiler. Ces deux Gates exigent le test [AGAPIC_R84_V1_V2_01.asc](../tests/current/AGAPIC_R84_V1_V2_01.asc) en 4 et 8 plans, Save/Load ABK, comparaison des flux RLE, palette/ModeID, Draw/Region, fermeture et RAM. Une promotion de `LAST_GOOD` nécessitera un nouvel accord explicite.

Aucune nouvelle branche et aucun fichier expérimental créés ; l'ancien test R83 reste archivé.
