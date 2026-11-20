# M19 P0 — préparation Chip lors de `Aga Bob Bank N`

> **Historique :** ce document décrit la préparation Chip validée comme source-only avant son intégration. Depuis le 20 novembre 2026, elle figure dans la nouvelle **Lib active P0**, avec `Aga Bob Bank Free N`. Voir [rapport P0](M19_P0_BANK_FREE_GATES_2026-11-20.md). Les mentions ci-dessous « S1 active », « Free non implémenté » sont des constats **antérieurs à la livraison P0**.


**Statut : candidate native expérimentale, SOURCE ONLY.** B8 S1 reste la seule Lib active (116 104 octets, SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a`). `LAST_GOOD` R84 n'est pas modifiée. Pas de nouvel ASC, pas de Compiler demandé. **Gate A candidate : PASS — 104 contrôles MC68020 sur deux relocations, OS/Chip/Blitter simulés ([CI 44796391673](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44796391673)).** Gates B/C/D non testées.

## Objectif de cette sous-étape, avant `Aga Bob Bank Free N`

Le contrat initial [M19 multi-images](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md), sections 2/4/5, impose une préparation automatique en **Chip RAM** à la sélection d'une banque existante contenant des images. La B8 S1 courante préparait à la première opération de dessin ; la préparation par sélection n'y est pas encore intégrée.

La proposition réutilise strictement les routines source natives antérieures :

- **P0a `bank_bank_select`** : sélection/création AGBO par banque AMOS, sans destruction d'une autre banque.
- **P0j-b2 `explicit_registry_prepare_entry`** : vérification AGBO complète, copie privée `MEMF_CHIP`, cache par identité/génération, validation des plages et allocation transactionnelle.
- **P0c `registry_lookup_entry` / `registry_free_entry`** : réutilisation identique du cache, `WaitBlit` avant libération, `FreeVec` du contexte privé.
- **B8/B7 `b8_b7_arm_end_nodraw_entry`** : armement du callback End existant, sans dessin avant capture.

### Contrat exact testé

1. **Banque absente** : l'ancien `Aga Bob Bank N` crée la banque AGBO vide, **sans allocation Chip** ; la capture d'images reste possible, l'étape de préparation n'est pas forcée inutilement.
2. **Banque pleine, écran AGA ouvert** : après sélection, validation de l'identité de la banque, de l'état écran et de `GfxBase`, puis préparation Chip **avant tout dessin**.
3. **Banque inchangée** : la préparation est idempotente pour le même numéro, pointeur AGBO, génération et propriétaire ; **aucune copie Chip répétée**.
4. **Après `Get AGA Bob`, `Load` ou remplacement** : si l'identité/génération a changé, la nouvelle sélection doit provoquer un restage vérifié, sans conserver de pointeur DMA périmé. Les écritures en place via `Poke` restent hors contrat.
5. **Absence d'écran, échec mémoire, banque erronée ou callback étranger** : la sélection antérieure est restaurée, aucun Bob n'est dessiné et aucun Swap n'a lieu. Un cache créé pour un armement de callback refusé doit être libéré avec la routine Chip contrôlée ; un cache préexistant valide est conservé.
6. **Propriété** : l'AGBO DATA appartient toujours à AMOS (`Save`/`Load`), le cache Chip et le nœud de registre appartiennent à l'extension. Aucune nouvelle banque AMOS numérotée.
7. **`Aga Bob Bank Free N`** : toujours **NON implémenté**. Sa future transaction devra désactiver les Bobs dépendants avant libération et respecter le garde READY/DIRTY de B8 S1.

**Restriction volontaire :** Gate A est maintenant verte, mais le nouveau comportement ne peut pas être promis dans B8 S1 sans décision explicite d'intégration, ni être qualifié Runtime avant un essai WinUAE. En attendant, **l'ancienne API B8 S1 ne change pas**.

## Source, provenance et qualification

**Candidate AP20 exacte (en mémoire, NON installée) :** **116 548 octets**, SHA256 `577fe698f040a13ea0a12c88fc80f31fd316eed011a305955eb5be635c8613bf`, **+432 octets natifs**, PC16 maximum **30 394**, 88 commandes / 184 entrées inchangées, groupes `[142,153,156,177,181]`. Seul le stub de `Aga Bob Bank N` (index AP20 **164**) est redirigé ; le code BOBS préexistant et l'unité B8 S1 restent identiques octet pour octet. **Gate A PASS ([104 contrôles natifs MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44796391673))** : banque vide sans allocation, état AGA absent sans allocation, préparation d'une banque remplie avant le dessin, réutilisation et deuxième banque, allocation Chip et metadata refusées, End étranger et rollback. **Contrôles de remplacement supplémentaires :** après modification d'une image avec `Get AGA Bob`, la banque est re-préparée, l'ancien bloc Chip est libéré après `WaitBlit` et la génération est mise à jour ; si la seconde préparation manque de mémoire, le cache précédemment alloué reste intact, la sélection est restaurée et une nouvelle tentative peut réussir. Les corrections de banc portent sur la bonne déclaration `TypeOfMem(graphics.library)` et sur l'initialisation explicite de l'état AGA ; les gardes de sécurité natifs ne sont pas affaiblis.


- [Nouveau wrapper MC68020](../tools/m19_b8_s1_bank_prestage_emit.py) : ancien code B7/B8 inchangé en préfixe, nouvelle entrée native uniquement.
- [Builder AP20 en mémoire](../tools/build_m19_b8_s1_bank_prestage_in_memory.py) : reconstruire B8 S1 par son builder SHA-pinné, modifier *seulement* le stub public existant `Aga Bob Bank N` et ajouter le code privé au groupe BOBS.
- [Banc MC68020](../tools/test_m19_b8_s1_bank_prestage_gate_a.py) : deux implantations natives relocalisées, Exec/Graphics/AMOS simulés ; capacité d'allocation, cache et rollback.
- [Workflow Gate A](../.github/workflows/m19-p0-bank-prestage-gate-a.yml) : CPU policy, construction byte-exacte, tests CPU, protection de S1/R84/ASC.

Pour une vérification locale (environnement Python avec Unicorn 2.1.4, Capstone 5.0.9) : `python -B tools/test_m19_b8_s1_bank_prestage_gate_a.py`.

**Aucune preuve WinUAE ni véritable exécutable produit par AMOS Compiler** pour cette sous-étape. Le mot « compiled » dans le banc désigne uniquement une deuxième implantation mémoire des instructions MC68020.

## Point de décision suivant

Valider d'abord les refus, caches multiples et callbacks pendant les transitions `Clear → Update → Swap`. Ne pas intégrer `Bank Free` tant que la désactivation groupée des objets Bobs actifs n'est pas prouvée sûre. Ne pas passer à M20 : le chantier M19 P0/P1/P2 reste ouvert.
