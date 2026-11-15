# M19 P0a — capture planaire et remplacement atomique : modèle de référence

**Statut : modèle hôte développé et testé ; AUCUNE nouvelle instruction AMOS/AP20 et AUCUN nouveau binaire.**

## Base strictement autorisée

- R88 v0.13.33, commit figé `7c575a02087d550611b8e966a7708b5f6a8c4b71` : source de référence du back buffer AGA et des contrats AMOS.
- Format `AGBO` v1 déjà intégré : [`M19_P0A_ABK_FORMAT_2026-11-15.md`](M19_P0A_ABK_FORMAT_2026-11-15.md).
- N'utiliser aucun code, programme de test, binaire ou builder R89/R90.
- `dist/AMOSPro_AGA.Lib` R88 et `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 sont inchangés.

## Ajouts

- `tools/m19_p0a_capture_transaction.py` : `BackBitmap` (largeur, hauteur, profondeur, **stride physique** et plans séparés), `read_back_rectangle()` (coords **inclusives** et X non aligné) et `HostBobBanks` (modèle d'allocation/remplacement à deux phases).
- `tools/test_m19_p0a_capture_transaction.py` : **14 tests hôte exécutés localement et PASS**.
- Les 11 tests originaux de `test_m19_p0a_multi_bob_abk.py` passent encore : **25 tests au total**, tous côté hôte.

### Capture

- Source : le **back buffer privé AGA** ; le modèle exige explicitement un état `safe=True`, mais **ne simule pas le protocole réel Exec/DBState Safe/Disp**.
- Lecture des pixels par plan physique, avec stride réel (potentiellement supérieur au `rowBytes` utile). Bit de poids fort à gauche et plan 0 = bit 0 de l'index couleur.
- `Get AGA Bob I,X1,Y1,X2,Y2` : bornes de rectangle inclusives ; `0,0,31,31` signifie 32×32 pixels. Refus des rectangles inversés/hors écran. Testé sur des largeurs 1, 17, 31, 32, 37, avec profondeur 1/4/8, découpes X impaires et bords exacts.
- Sortie : données d'image `AGBO` **plan-major, non compressées**, sans masque par défaut ; `Make AGA Bob Mask I,C` reste une opération distincte.

### Remplacement de banque : invariants, pas encore implémentation AMOS

1. Vérifier le numéro (5..65535), le format `AGBO` et la validité du payload existant ; ne pas détruire une banque d'un autre format.
2. Lire uniquement le bitmap identifié comme **Safe**, capturer les pixels et construire un nouveau payload complet en mémoire privée.
3. Vérifier l'ensemble du nouveau payload (taille/offsets/masques/génération), puis valider la disponibilité mémoire ; si une étape échoue, la banque existante doit rester **identique octet pour octet**.
4. Basculer l'association du numéro de banque uniquement lorsque le nouveau contenu est prêt. Dans le *modèle*, cette étape est une affectation unique ; **aucune preuve n'existe encore pour une substitution atomique dans les listes AMOS Professional 365**.
5. Un `Erase` ou `Load` sous le même numéro invalide la sélection courante ; `Aga Bob Bank N` doit être rappelée pour lier le nouveau contenu. La sélection ne doit jamais stocker durablement un ancien pointeur de banque.
6. Les objets Bobs et la mémoire Chip de rendu restent **hors périmètre P0a** ; aucun swap implicite.

**Attention :** `Bnk.Reserve` (mécanisme utilisé par les anciennes commandes) efface une banque occupée **avant** de tenter la nouvelle allocation. Ce mécanisme ne suffit pas pour un remplacement sûr. Une représentation `AGBO` correctement testée sur PC ne prouve ni la transaction réelle AMOS, ni `Save`/`Load` réel dans WinUAE.

## Validation exécutée

```sh
python -B tools/test_m19_p0a_multi_bob_abk.py
python -B tools/test_m19_p0a_capture_transaction.py
```

- Tests existants : 11/11 PASS, hôte.
- Tests nouveaux : 14/14 PASS, hôte.
- **Gate A native 68020/AP20 : NON TESTÉE.**
- **Gate B WinUAE/AMOS : NON TESTÉE.**
- **Gate C AMOS Compiler : NON TESTÉE.**
- **Gate D matériel physique : NON TESTÉE.**

## Point bloquant avant intégration native

Établir à partir de la **vraie implémentation AMOS Professional 365** (et non d'un fork non identifié) un mécanisme de remplacement de banque qui réserve d'abord la nouvelle allocation sans détruire l'ancienne, puis modifie proprement le chaînage AMOS et notifie ses extensions. Vérifier l'ABI `Bnk.GetAdr` / `Bnk.Reserve` / `Bnk.Change`, l'ownership, l'ordre de libération et le comportement sous AMOS Compiler V2. **Ne pas coder une mutation de pointeur/numéro dans l'assemblage sur simple hypothèse**.

Après cette preuve, implémenter les wrappers natifs `Aga Bob Bank N` et `Get AGA Bob I,X1,Y1,X2,Y2`, puis les tester dans le vrai binaire AP20. Le nouveau test ASC actif sous `tests/current/` remplacera l'ancien *uniquement lorsque le binaire et ses ressources exactes seront prêts pour WinUAE* ; aucun ASC fictif n'est créé à ce stade.