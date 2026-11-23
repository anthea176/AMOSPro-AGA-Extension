# S1-P1d — Première commande « Aga Sprite Bank N » (candidate)

**23 novembre 2026 — Code MC68020 et token AP20 en candidate MÉMOIRE seulement.** Ce n'est pas encore une commande disponible dans la bibliothèque P2d.

La [routine de sélection](../src/native/m19_s1/M19_S1P1D_BANK_PUBLIC_MC68020.s) reçoit le numéro de banque en D3 depuis une instruction `Aga Sprite Bank N`. Si la banque est absente, elle crée un payload **AGSP v1 vide de 32 octets** via le publisher transactionnel P1c, sans utiliser `Bnk.Reserve` destructif. Si le numéro est occupé, elle vérifie qu'il s'agit d'une banque DATA `AGASPRT `, puis applique le validateur intégral des pixels et palettes RGB24. Une banque d'un autre type est refusée, sans mutation.

Le contexte AMOS Main (A5) et le numéro de banque sont stockés dans les données privées du groupe natif, **pas un pointeur d'image**. Les vraies captures devront résoudre à nouveau la banque via `Bnk.GetAdr` et prouver sa stabilité.

**Tests source MC68020 :** [9 tests banc sélection](../tools/test_m19_s1p1d_public_bank.py) sous Unicorn MC68020 avec services Exec/AMOS Main simulés : banque absente, sélection répétée, banque chargée, flags DATA normalisés, conflits, corruptions, échec d'allocation. [Builder AP20 in-memory](../tools/build_m19_s1p1d_sprite_bank_ap20.py) et [tests GetP/token/HUNK](../tools/test_m19_s1p1d_public_ap20.py) : signature **`I0`**, une instruction un argument numérique, stub immédiatement après le `GetP` d'origine. Aucune des 100 commandes P2d ni aucun des 203 morceaux de code antérieurs n'est modifié ; le candidat ajoute uniquement `Aga Sprite Bank N` et un groupe natif V2. *Pas de fichier Lib produit*.

**Limite :** `Get AGA Sprite` n'est pas exposé à AMOS ; il faut construire son wrapper de paramètres et d'allocations temporaires pour appeler le pipeline de capture MC68020 déjà validé. Le chemin de création/chargement par la Lib installable devra être testé sous **WinUAE Runtime** séparément. La Gate C de la sonde DATA AGSP a été **sautée à la demande de l'auteur**, pas déclarée PASS. Aucun affichage matériel ni règle DMA finale.

Les prototypes restent sous `tests/proto/`. `dist/AMOSPro_AGA.Lib`, `LAST_GOOD` et le test Bob actif sont strictement protégés. La candidate ne doit pas être installée ni promue automatiquement.
