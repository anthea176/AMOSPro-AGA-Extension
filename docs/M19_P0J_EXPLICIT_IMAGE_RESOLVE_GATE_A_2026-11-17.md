# M19 P0j-b3 — résolution d'image Chip par banque d'origine

**Source-only MC68020+, Gate A à valider.** Après P0j-b1 (lookup) et P0j-b2 (Chip staging) validés, le résolveur P0d doit accepter le numéro original de banque sans dépendre de `bank_active_state`.

Le point d'entrée privé `explicit_image_resolve_entry` reçoit D3=banque, D0=image, A1=sortie de 36 octets, A5=owner. Il interroge P0j-b1 dans un scratch **local à la pile**, puis rejoint la fonction P0d originale au label **zéro octet** `resolve_live_payload`. Le répertoire AGBO, les dimensions, profondeurs, masques, offsets et limites de l'allocation Chip sont vérifiés par **le vrai code P0d non modifié**, et le résultat n'est écrit qu'en succès.

[Émetteur](../tools/m19_p0j_explicit_image_resolve_emit.py), [builder AP20 en mémoire](../tools/build_m19_p0j_explicit_image_resolve_in_memory.py), [banc natif](../tools/test_m19_p0j_explicit_image_resolve_gate_a.py). Les tests doivent comparer les neuf champs réels et leurs octets de pixels pour les banques 10/11, refuser image absente et génération périmée, surveiller les écritures sur la sélection, et vérifier la fermeture.

**Gates B/C/D non effectuées ; aucune Lib ni ASC modifiés.** Il reste le wrapper **Safe/Blitter** original P0d, qui appelle encore l'ancien résolveur sélectionné. Pour obtenir 64 Bobs sans shadow temporaire, adapter ce dernier appel puis le parcours multi-objets, sans exposer `Aga Bob Draw` avant validation.
