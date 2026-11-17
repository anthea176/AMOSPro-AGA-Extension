# M19 P0j-b1 — lecture du cache Chip explicitement par banque

## Contrat MC68020

Jalon privé, source-only sur `main`. Nouvelle entrée `explicit_bank_lookup_entry` après le bytecode P0j-a figé. Entrées D3 = numéro de banque source, A1 = descripteur de sortie de 28 octets, A5 = propriétaire AMOS. Recherche du contexte P0c directement dans `registry_state` par numéro, vérifie `Cur_Banks`, `Bnk.GetAdr`, l'identité/génération AGBO, puis réutilise la vraie routine `chip_lookup_entry` et contrôle MEMF_CHIP. Aucune lecture/écriture de `bank_active_state`. Sortie validée en mémoire et publiée **uniquement après succès** (7 entiers 32 bits, sans publication partielle).

Le descripteur porte : AGBO payload, génération, Chip base et taille, pointeur du contexte Chip (node+8), numéro de banque, tête de la liste AMOS. Le caller devra revalider avant DMA, car un effacement/rechargement pendant le dessin reste interdit.

[Émetteur](../tools/m19_p0j_explicit_bank_lookup_emit.py), [builder AP20](../tools/build_m19_p0j_explicit_bank_lookup_in_memory.py), [banc MC68020](../tools/test_m19_p0j_explicit_bank_lookup_gate_a.py). Le banc prépare deux sources Chip avec le moteur P0i déjà validé, puis vérifie la recherche **par banque**, indépendamment de la sélection courante, et les rejets génération périmée, liste effacée, banque absente, propriétaire incorrect, CPU000, fermeture.

**Statut : Gate A à confirmer en CI. Gates B/C/D non exécutées.** Aucun binaire installable ni commande publique Draw modifiés.

## Périmètre restant

Ce n'est **pas encore** un remplacement des trois chemins P0c/P0d. La préparation Chip P0c et le résolveur d'image P0d utilisent encore la sélection globale. Le test P0j-b1 fait d'abord préparer les deux banques via l'ancien P0i puis appelle la **nouvelle recherche indépendante**. Il faudra une préparation explicite par banque, puis un résolveur/painter explicite et enfin un rendu 64 Bobs **sans aucune projection temporaire**, avant d'envisager `Aga Bob Draw`. L'ancienne librairie quatre unités (96 908 octets, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`), l'ASC et `LAST_GOOD` R84 sont protégés.
