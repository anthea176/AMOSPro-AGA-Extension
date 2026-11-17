# M19 P0j-b2 — préparation Chip sans sélection globale

Source privée MC68020. Deux nouvelles entrées natives s'appuient sur les labels P0c de **zéro octet machine** : l'une récupère directement la banque AGBO d'origine via `Bnk.GetAdr` puis rejoint le validateur complet P0c ; l'autre réutilise la recherche et publication atomique des nœuds du registre P0c. Aucun appel `Aga Bob Bank` ni accès au shadow `bank_active_state`.

[Émetteur](../tools/m19_p0j_explicit_bank_stage_emit.py), [builder source-only](../tools/build_m19_p0j_explicit_bank_stage_in_memory.py), [test MC68020](../tools/test_m19_p0j_explicit_bank_stage_gate_a.py). La Gate A doit tester les sources 10 et 11 avec banque 11 sélectionnée, l'intégrité des octets Chip et l'absence d'écritures sur la sélection.

**Gate A à confirmer. Gates B/C/D non exécutées.** Ancienne Lib active 96 908 octets SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`, ASC actif et `LAST_GOOD` R84 protégés. **Le résolveur d'image P0d et le painter nécessitent encore une voie explicite par banque avant de supprimer entièrement la projection P0i et exposer `Aga Bob Draw`.**
