# M19 P0a — transaction native de banque AMOS (base R88)

**Statut : CODE MACHINE 68000/68020 EMIS + PREFLIGHT LOCAL PASS ; NON INTEGRE A L'AP20 ; GATES A/B/C/D NON TESTEES.**

## Sources exactes, sans code provenant de R89/R90

- Extension AGA de depart : **R88 v0.13.33**, commit `7c575a02087d550611b8e966a7708b5f6a8c4b71` ; `dist/AMOSPro_AGA.Lib` SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`.
- Code AMOS d'origine (lecture seule) : [`marc365/AMOS-Professional-365`](https://github.com/marc365/AMOS-Professional-365/tree/3e8f53196b80cbb2e01342a89a3545d080bf0de4), SHA exact `3e8f53196b80cbb2e01342a89a3545d080bf0de4` : `+B.s` blob `ab9a438c0a88ea485cfbfe51f2ecea1098f902ad`, `+Lib.s` blob `c37fde6517ce00701779e044308d7ae803015412`, `+Equ.s` blob `c5ac16e3c9cc68d7c6e84c98afb187130fc8242e`.
- Fichiers déjà développés en P0a : `tools/m19_p0a_multi_bob_abk.py`, `tools/m19_p0a_capture_transaction.py` et leurs **25 tests modèle** ; aucun exemple ni binaire expérimental après R88 utilisé.
- Symboles `Rjsr` de la table `tests/fixtures/amos_main_declarations.json` R88 : `Lst.Cree=91`, `Lst.Del=93`, `Bnk.GetAdr=797`, `Bnk.Change=819`. `Bnk.Reserve=816` **interdit sur une banque existante**.

## Audit des vraies structures AMOS Professional 365

- `+Equ.s` : `RsReset` ligne 1147 → `Cur_Banks` ligne 1327 donne **`Cur_Banks(A5) = +$05EA`** (1 514 octets). Calcul recompte les `rs.l`, `rs.w`, `rs.b` et le tableau `ExtAdr` ; ne pas reutiliser cet offset sur un autre AMOS sans verification.
- `+B.s` (sections `Lst.Cree`, `Lst.Del`, `Lst.Insert`, `Lst.Remove` autour des lignes 1 200) : une liste est un chaînage de nœuds. `Lst.Cree` reçoit **A0=adresse de la cellule de tête**, `D0=longueur hors en-tête liste`, `D1=flags memoire` ; il alloue **D0+8**, écrit `[next.l,size.l]` et préfixe le nœud à cette liste. `Lst.Del` détache et libère l'allocation depuis cette même cellule.
- `+Lib.s` : un nœud de banque DATA est `[next.l,size.l,bank_number.l,flags.w,reserved.w,name[8],payload]`. **Payload = nœud+24**, `size.l = longueur du payload +16` ; `Bnk.GetAdr(D0=bank)` renvoie le payload en `A0/A1` ou zéro. `Bnk.Reserve` appelle d'abord `Bnk.EffA0` avant l'allocation, ce qui est **non transactionnel** en cas de manque mémoire.
- `Bnk.Change` notifie les extensions de la nouvelle liste de banques, puis met à jour les références des Sprites/Bobs natifs.

## Implémentation ajoutée

`tools/m19_p0a_amos_bank_transaction_emit.py` émet un sous-programme **natif privé** de 874 octets (SHA256 `53624df54661761ee7161131ad6ffddb98ffbf2b4eeb6d9c7f03215327d4621e`). Ce n'est pas une nouvelle commande AMOS visible.

**Entrées contrôlées :** `D3 = numero banque 5..65535`, `A0 = adresse payload AGBO V1 déjà validé en totalité par l'appelant`, `D1 = longueur exacte en octets pairs`, `A5 = contexte AMOS Professional 365`. Sortie : `D3 = 1` en succès ou `0` en refus, `D2 = 0` type entier ; ABI préserve les registres selon l'émetteur R88.

1. Contrôler ID, en-tête AGBO et taille du nouveau payload ; trouver l'ancienne banque avec `Bnk.GetAdr`. Refuser un nom/format étranger.
2. **Créer un nouveau nœud détaché** via `Lst.Cree` sur une cellule privée de la frame. Copier le payload et ses métadonnées. Cela n'occupe **aucun autre numéro de banque AMOS**.
3. Vérifier à nouveau l'identité de l'ancienne banque avec `Bnk.GetAdr` et le pointeur de tête `Cur_Banks`. Parcourir au maximum 65 535 éléments de liste avant de refuser un chaînage incohérent.
4. Publier le nouveau nœud par **une seule écriture LONG de pointeur** dans la vraie liste. Ancienne allocation détachée mais conservée vivante.
5. Appeler `Bnk.Change` **avant** de libérer le vieux nœud. Détruire ensuite uniquement ce dernier via `Lst.Del` appliqué à la cellule privée.
6. En cas d'échec **avant publication**, libérer uniquement le nœud privé et ne rien modifier dans la liste active.

**Limites non masquées :** cette primitive ne parse pas complètement la table des images et les masques. C'est le travail obligatoire de son futur appelant `Get AGA Bob`. Elle ne vérifie pas les migrations de pointeurs internes d'autres extensions au-delà du contrat `Bnk.Change`, ni l'exécution CPU réelle. Une source temporaire doit rester valide pendant toute la transaction. Aucun Blitter/DMA ni Chip staging dans cette étape.

## Validation réellement effectuée

```sh
python -B tools/test_m19_p0a_amos_bank_transaction_emit.py
python -B tools/test_m19_p0a_multi_bob_abk.py
python -B tools/test_m19_p0a_capture_transaction.py
```

- **7/7 contrôles statiques de l'émetteur PASS**, génération déterministe, embranchements relatifs valides, signature binaire, ABI, pointeurs, nombre des appels principaux, absence de `Bnk.Reserve`, ordre notification/libération.
- **25/25 tests hôte P0a PASS** : images ABK, masques, capture, transactions modèle.
- **32/32 contrôles locaux PASS au total** ; `py_compile` des nouveaux fichiers PASS.
- **Gate A CPU 68020 / AP20 réel : NON TESTÉE** (pas d'exécution 68k sous Unicorn/AMOS).
- **Gate B WinUAE interprété : NON TESTÉE** ; **Gate C AMOS Compiler V2 : NON TESTÉE** ; Gate D : NON TESTÉE.
- `dist/AMOSPro_AGA.Lib`, `dist/AMOSPro_AGA_LAST_GOOD.Lib`, builder R88 et ASC actif conservés octet pour octet.

## Étape suivante : API réelle

Raccorder ce sous-programme à `Aga Bob Bank N` et au producteur planaire `Get AGA Bob I,X1,Y1,X2,Y2`, avec une source candidate entièrement validée (répertoire, masques, padding, mémoire et back buffer Safe). Puis seulement produire une **candidate AP20 en mémoire dérivée exactement de R88**, vérifier indices/`GetP`/relocation et exécuter la Gate A **CPU** avant toute installation. Les futures commandes restent non exécutables sur R88 à cette étape.
