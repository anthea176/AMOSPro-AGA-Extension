# M18/P4 — raccordement AMOS Fast Icon/Bank/Safe, Gates A/B/C PASS

**État au 13/11/2026 : Gate A CPU/CI PASS (226 cas), Gate B AMOS interprété PASS, Gate C compilé WinUAE PASS pour le scénario testé.** [Rapport B/C](M18_R61_FICON_WINUAE_GATES_BC.md). Candidate R61 v0.13.6, [dist/AMOSPro_AGA.Lib](../dist/AMOSPro_AGA.Lib), 36 816 octets, SHA256 `ff26a7819744a8e42a64628d5e66504710835c2af812650e89cc681fb3c9050f`. **R60 LAST_GOOD protégée ; R61 NON PROMUE. Gate D physique non testée.**

## API proposée

`_OK=Aga F Icon(Bank,IconID,X,Y,Mode)` — fonction entière 1/0, cinq arguments. Mode 0 opaque, mode 1 couleur zéro transparente. Positions X/Y exactes au pixel près ; source 8 bitplanes et moteur CPU P3.

## Banque dédiée

Banque DATA AMOS numéro 5..65535, nom exact `FICON8  ` (huit octets), contenu Unity : en-tête big-endian 12 octets (taille totale, nombre 4..4096, largeur 16, hauteur 16, profondeur 8) et 288 octets par icône. Chaque slot alterne, sur 16 lignes, un mot de masque de préservation et 8 mots de plans. ID 1-based. Le slot sélectionné est validé ligne par ligne avant le dessin. Il n'est pas interchangeable avec AGAPIC RLE ni la banque Icon 2.

## Sécurité native

La nouvelle routine [émetteur P4](../tools/m18_ficon_ap20_emit.py) résout Bnk.GetAdr en direct, contrôle l'enveloppe DATA, les adresses via TypeOfMem, le format et la taille de la banque. Elle valide un ScreenBuffer privé AGA en 8 plans, la géométrie et les pointeurs avant d'obtenir Safe par GetMsg non bloquant. Le moteur interne P3 est appelé par BSR.W. Aucun Swap, Wait Vbl, allocation ou Blitter DMA caché.

Le [builder mémoire](../tools/build_m18_r61_ficon.py) reconstruit la R60 SHA-épinglée et ajoute un seul token/point d'entrée AP20 sans modifier les anciennes fonctions. Le [test Gate A](../tools/test_m18_r61_ficon_gate_a.py) vérifie les deux dispositions AP20, les pixels, ABI, mémoire front et rejets sans écriture.

**Gates A/B/C PASS sur le seul scénario WinUAE documenté ; Gate D non réalisée.** Circuit unique conservé : `dist/AMOSPro_AGA.Lib` et `tests/current/M18_R61_FICON_01.asc`, sans promotion automatique ni changement de `LAST_GOOD`.

**Ressources de validation :** [test ASC R61](../tests/current/M18_R61_FICON_01.asc), [banque ABK FICON8](../tests/current/M18_FICON8_SAMPLE_BANK10.abk) et [instructions](../tests/current/README.md). Le flag Fast de la banque ne garantit pas sa position physique : le vérifier dans WinUAE. Aucun backend DMA/Blitter masqué ni cache Chip natif n'est fourni dans R61.
