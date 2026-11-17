# M19 P0g — lecture native sécurisée d'un Bob avant Draw

**Périmètre : source-only sur `main`, cible MC68020 minimum.** Ce jalon ne publie pas `Aga Bob Draw` et ne modifie ni `dist/AMOSPro_AGA.Lib`, ni `tests/current/`, ni `LAST_GOOD`.

## Problème résolu

La lecture brute `relay_read_entry` de P0e indique qu'un objet est actif, mais ne vérifie pas si sa banque AMOS a été effacée ou rechargée depuis l'appel `Aga Bob N,X,Y,I`.

Nouveau point d'entrée **privé** `relay_checked_read_entry` dans BOBS : paramètres `D0=N`, `A1=destination 24 octets`, `A5=owner`. Il cible l'entrée native existante `identity_check_entry` de P0f dans l'unité AGA, à partir du pointeur de State vérifié et de l'offset source exact. Retour `D3=1/D2=0` uniquement si objet actif et banque encore conforme à son cachet (pointeur, génération, liste AMOS et taille). Sur échec, **aucun octet de la destination n'est modifié**. Registres AMOS et pile préservés.

La lecture brute **reste byte-exacte** : elle sera nécessaire pour distinguer, lors du futur `Draw`, un objet inactif à ignorer d'un objet actif devenu invalide (échec de frame avant DMA). L'API publique Set/Off, les 85 commandes et les 95 entrées AP20 de la source P0f ne changent pas.

## Fichiers

- [Émetteur](../tools/m19_p0g_checked_read_emit.py), extension native BOBS après la source P0f ; AGA et anciennes entrées préservées.
- [Builder](../tools/build_m19_p0g_checked_read_in_memory.py), repack AP20/HUNK en mémoire, provenance P0f vérifiée, PC16 strictement borné.
- [Banc natif](../tools/test_m19_p0g_checked_read_gate_a.py), réel MC68020/Unicorn en deux placements : succès, multi-banques, génération périmée, Erase simulé, mauvais owner, sortie intacte en échec, CPU non 020, Off et Reset.

**Statut :** **Gate A native MC68020 PASS** ([CI M19 44150293973](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44150293973)), **52 cas** réussis en deux implantations AP20 V2. Émetteur natif **16 444 octets**, SHA256 `a30d4a4bc9c2ea1e50aa9a69fe62df6f684f58d1ffa0737559cd891becdc8f87`. Image AP20 source-only **96 752 octets**, SHA256 `e1f8f8c04e24a38651ade50b6878cffb1dd288a766b104fb5c9fa9ae314d9536`, 85 commandes/95 entrées/4 groupes, portée PC16 32 590 octets et marge 176. **Gates B/C/D non exécutées pour ce code privé inédit.** Le scénario courant à quatre unités garde ses validations B/C historiques. La prochaine étape sera la *prévalidation de toute la liste* des Bobs actifs avant un rendu sur le back buffer Safe, puis le dessin sans `Aga Swap` implicite ; aucune de ces opérations n'est prétendue terminée ici.
