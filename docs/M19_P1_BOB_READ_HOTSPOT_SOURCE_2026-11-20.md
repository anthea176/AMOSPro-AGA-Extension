# M19 P1 — lectures Bob et Hot Spot, amorçage source-only

**Date : 20 novembre 2026. Dépôt : `anthea176/AMOSPro-AGA-Extension`, branche `main` uniquement.**

## Référence P0 préservée

- `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` restent **strictement identiques**, **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, 89 commandes et 185 entrées AP20. Il n'existe **aucun token P1** à ce stade.
- Gate A P0 : PASS 225 contrôles MC68020 ; Gate B Runtime P0 : PASS fonctionnel sur journaux ; Gate C AMOS Compiler P0 : NON TESTÉE ; D physique : NON TESTÉE.
- `tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`, `tests/passed/`, archives, et les deux binaires `.Lib` sont **inchangés**.

## P1a — Lecture X/Y/image : infrastructure vérifiée, pas d'API publique

Le code natif préexistant [`m19_p0e_object_table_emit.py`](../tools/m19_p0e_object_table_emit.py) possède une table de **64 Bobs**, chaque entrée de **24 octets**, avec les champs suivants :

| Offset dans le Bob | Champ | Format |
| --- | --- | --- |
| +0 | Banque AMOS source | entier 32 bits |
| +4 | Image | entier 32 bits, ID 1..4096 |
| +8 | X | entier signé 32 bits, domaine accepté -32768..32767 |
| +12 | Y | entier signé 32 bits, domaine accepté -32768..32767 |
| +16 | Activité | 0 ou 1 |
| +20 | Réservé | 0 |

La primitive privée **`object_read`** exige un Bob 1..64 actif, le bon propriétaire AMOS `A5`, un pointeur de sortie valide ; elle renvoie **D3=1** en succès, **D3=0** en refus et ne modifie pas les 24 octets de sortie sur un refus. `Aga Bob Off` et `Aga Bob Bank Free` rendent les objets concernés inactifs. Cette lecture **ne crée aucun nouveau token**.

**Test livré :** [`test_m19_p1_bob_queries_hotspot.py`](../tools/test_m19_p1_bob_queries_hotspot.py) utilise le **véritable code émis MC68020** dans Unicorn, avec deux implantations mémoire, limites de coordonnées signées, IDs 1/32/64, images 1/2/4096, propriétaire étranger, Bob OFF/réactivation et lectures invalides. [CI P1 source-only : PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44827972362). Ce n'est **pas** une Gate A d'une API getter P1 inexistante, ni WinUAE.

**Noms de fonctions proposés, NON retenus à ce stade :** `Aga X Bob(N)`, `Aga Y Bob(N)`, `Aga I Bob(N)`. La sortie d'un objet absent/inactif n'est **pas définie** : 0 et -1 sont des coordonnées X/Y légales, donc ne sont pas des sentinelles universelles sûres. Choisir explicitement la politique d'erreur et l'ABI AP20/Compiler avant d'ajouter un token. Le chemin interprété et le chemin Compiler doivent tous deux être qualifiés sur le nouveau getter.

## P1b — Hot Spot par image : format AGBO exploité, moteur inchangé

Le format **AGBO v1** a **déjà** deux champs `hotspot_x` / `hotspot_y` signés 16 bits dans son entrée de répertoire de **40 octets**. Il est donc inutile et interdit d'inventer un nouveau format de banque pour P1.

Nouvelle opération **hôte uniquement** [`set_hotspot(payload,image_id,x,y)`](../tools/m19_p0a_multi_bob_abk.py) :

- image existante 1..4096, X/Y hotspot signés dans **-32768..32767** ;
- construction **copy-on-write** avec parse/validation avant sortie ; aucune mutation du payload d'entrée ;
- pixels planaires, masque, autres images et enveloppe `AmBk` préservés ;
- nouvelle génération **+1** uniquement en cas de changement, pour invalider le staging Chip à la prochaine sélection/validation ;
- mêmes coordonnées = même objet `bytes` renvoyé, génération inchangée ; modification interdite si génération saturée ; entrée absente ou arguments invalides refusés ;
- conservation des coordonnées lors de `Make Mask` / `No Mask` déjà assurée par le modèle P0.

La **position future du dessin** sera `X_dessin = X_Bob - hotspot_x`, `Y_dessin = Y_Bob - hotspot_y`, avec clipping et garde sur les domaines arithmétiques à vérifier. **Le rendu natif P0 actuel n'applique pas encore ces hotspots.** Aucune syntaxe AMOS `Hot Spot` n'est encore publiée et aucune écriture native des banques n'a été implémentée.

Le remplacement d'une image par `put_image` dans le modèle existant réinitialise son hotspot à (0,0) ; décider explicitement la sémantique de `Get AGA Bob` sur une image remplacée avant l'API publique P1.

## Décomposition P1 suivante

| Tranche | Travail | État |
| --- | --- | --- |
| **P1a** | Getter X/Y/I : contrat d'erreur, shim public, token AP20, relocalisation, tests CPU020 | Primitives privées testées ; **API à développer** |
| **P1b** | Hotspot : écriture AGBO, sélection/capture, application dans le dessin, clipping | **Modèle hôte et tests PASS** ; moteur natif à développer |
| **P1c** | Priorités : ordre initial par ID, modes Y et inverse, tri stable, gestion du fond | Non engagé |
| **P1d** | `Limit Bob` : clipping configurable au pixel, sans arrondi à 16 pixels | Non engagé |
| **P1e** | `Del Bob`/`Ins Bob` : choix de la réindexation, références de Bobs et génération Chip | Non engagé |

Le tri et le clipping doivent rester compatibles avec `Clear → Update → Aga Swap` explicite, aucune composition sur frame `READY`/`DIRTY` et aucun swap implicite. `Del/Ins` ne doit jamais laisser un pointeur Chip obsolète. Les Sprites AGA et M20 restent en attente.

## Commandes de vérification

```bash
python -B tools/test_m19_p0a_multi_bob_abk.py
python -B tools/test_m19_p1_bob_queries_hotspot.py
python -B tools/native_cpu_policy.py --self-test
python -B tools/check_aga_delivery_paths.py --self-test
```

**Statut :** CI source-only P1 **PASS** (Unicorn MC68020 pour le registre P0 et tests host AGBO). **Aucune API P1 ni nouveau binaire validés** ; Gates B/C/D P1 **NON TESTÉES**. En parallèle, le workflow global `Artifact integrity` du HEAD antérieur était rouge sur un test historique R71 qui exigeait encore l'ancienne SHA `LAST_GOOD` R84 ; ce défaut **précède P1** et n'est pas corrigé ici pour ne pas mélanger les chantiers.
