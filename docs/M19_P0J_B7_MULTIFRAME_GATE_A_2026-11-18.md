# M19 B7-m1 — correction End multiframe, Gate A (18/11/2026)

## Diagnostic vérifié

Dans tools/m19_p0j_explicit_safe_draw_emit.py, explicit_frame_draw_entry appelle program_end_arm_entry du pont P0c à chaque Draw. Celui-ci accepte les callbacks End AGA originel ou program_end_bridge_entry, mais refuse le b7_end_entry laissé par le premier Draw. Le refus provoque Draw=0 et le garde DIRTY bloque Swap.

Le banc distingue aussi un deuxième refus légitime : après Swap, DB+20=3 représente des notifications Safe/Disp en attente. Ce verrou ne doit pas être supprimé.

## Delta minimal en source MC68020

- tools/m19_p0j_end_lifecycle_emit.py : nouvelle routine b7_multiframe_draw_entry ajoutée APRÈS les octets B7 figés. Vérifie A5, écran, State, TypeOfMem, signature native End et égalité des slots A5+$1CC/$1D0. Si B7/B7, bascule temporairement vers P0c/P0c ; la routine B7 d'origine réinstalle B7. AGA/AGA ou P0c/P0c restent acceptés. Callback étranger, paire désaccordée ou signature modifiée : refus (D2=0, D3=0), garde DIRTY, sans nouveau Blit.
- tools/build_m19_p0j_end_lifecycle_in_memory.py : build_multiframe() construit un AP20 uniquement en mémoire depuis la B7 source-pinnée, avec 86 commandes, 181 entrées et quatre unités ; build() original reste octet pour octet reproductible.
- tools/test_m19_p0j_end_lifecycle_gate_a.py : reproduit l'échec B7 de la deuxième frame après acquittement simulé de Safe/Disp, puis exécute 120 Draw/Swap successifs et quatre Bobs dans chacun des deux placements natifs MC68020. Teste aussi callbacks étrangers, paire partielle, signature altérée, Close, End et Safe/Disp différés. Le mock met DB+20 à 0 avant Draw pour représenter des notifications déjà reçues, sans prétendre exécuter leur traitement réel sous AmigaOS.

## Preuves

- [Gate A MC68020 — CI 44383118836](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44383118836) : **PASS 793 contrôles multiframe** et **PASS 88 contrôles B7 historiques**, deux placements natifs. AmigaOS, AMOS et DMA restent simulés.
- [Politique native CPU/chemins — CI 44383118843](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44383118843) : **PASS**.
- **Binaire B7 installé inchangé** : dist/AMOSPro_AGA.Lib, 102 072 octets, SHA256 f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b.
- **Gate B B7-m1 NON TESTÉE ; Gate C NON TESTÉE ; Gate D NON TESTÉE.** Aucun nouvel ASC ni bibliothèque. R84 LAST_GOOD et archives protégés.

## Suite soumise à autorisation distincte

Une éventuelle nouvelle candidate dans dist/AMOSPro_AGA.Lib nécessite une autorisation explicite. Ensuite seulement, contrôler en Runtime WinUAE réel les 120 frames Draw/Swap, la disponibilité Safe/Disp après Clear, les pixels, Close, End et le retour à AMOS. Aucun essai Compiler n'est demandé pour cette phase.
