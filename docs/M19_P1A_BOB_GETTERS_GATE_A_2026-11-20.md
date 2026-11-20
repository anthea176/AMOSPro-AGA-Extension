# M19 P1a — fonctions X/Y/I Bob, Gate A MC68020 source-only

**20 novembre 2026 — `main` exclusivement.** L'auteur a autorisé « ok go » après validation du contrat : fonctions numériques `Aga X Bob(N)`, `Aga Y Bob(N)`, `Aga I Bob(N)`, et retour `-32769` pour tout refus. **Une candidate AP20 a été produite UNIQUEMENT en mémoire ; aucune nouvelle bibliothèque n'a été installée.**

## 1. Base P0 verrouillée

| Élément | Valeur |
| --- | --- |
| Lib active et `LAST_GOOD` | **P0 promue**, 117 896 octets, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, blob Git `6e23a1dc783145adb41f1a9b02fc6fc8f3b80ff2` |
| P0 | 89 commandes, 185 entrées AP20, groupes MC68020 `[142,153,156,177,181]`, PC16 max **31 092** |
| P1a candidate **non installée** | **118 816 octets**, SHA256 `165a24edcd4c00074d6ddce4a98317f720ed3236d61ba006333574743b55063a` |
| Source native complète groupe 181 | SHA256 `9e9785488bf7fcf5b9062e38439ebdf4e1e032ee226df0a97850df95a386512e` |
| P1a | **92 commandes**, **188 entrées AP20**, mêmes 5 groupes, PC16 max **31 092** ; **838 octets natifs ajoutés** au groupe 181 |
| Stub `Aga X Bob(N)` | Fonction numérique, signature `00`, entrée 185, groupe 181, offset 13894 |
| Stub `Aga Y Bob(N)` | Fonction numérique, signature `00`, entrée 186, groupe 181, offset 13942 |
| Stub `Aga I Bob(N)` | Fonction numérique, signature `00`, entrée 187, groupe 181, offset 13990 |

La candidate est bâtie depuis **le builder exact de P0**, non depuis un désassemblage. Les 185 entrées et tokens antérieurs sont conservés, sauf les **quatre octets `GetP` append-only** ajoutés à la fin du stub P0 n°184 pour le premier getter. Chaque getter à argument supplémentaire est précédé de son marqueur `GetP` ; le dernier stub se termine par `RTS`. La nouvelle source native est strictement ajoutée au groupe 181, **sans aucun changement au groupe BOBS 177** ni aux autres unités.

## 2. Contrat numérique

| Fonction | Domaine en succès | Refus |
| --- | --- | --- |
| `Aga X Bob(N)` | X signé, -32768..32767 | `-32769` |
| `Aga Y Bob(N)` | Y signé, -32768..32767 | `-32769` |
| `Aga I Bob(N)` | Image n°1..4096 | `-32769` |

Le paramètre `N` désigne un **objet Bob actif** de **1 à 64**, et non la banque AMOS ni le numéro d'image. Une absence, `Aga Bob Off`, un propriétaire AMOS différent, un CPU non MC68020, une adresse native non reconnue, un callback perdu ou un `Bank Free` qui désactive le Bob doivent donner le refus, sans modifier la table d'objets.

ABI AMOS numérique : `D3` reçoit le paramètre, `D3` renvoie la valeur signée, `D2=0` ; `A3/A5`, pile et les autres registres AMOS sont préservés. Le bridge n'alloue pas de Chip, ne dessine pas, ne modifie pas de banque, n'effectue aucun Swap et lit la table P0e existante.

**Note :** `-1` et `0` sont des coordonnées légales et ne servent donc jamais de sentinelle.

## 3. Pourquoi le cinquième groupe natif

La première tentative de builder branchait les nouveaux stubs en fin d'AP20 directement vers BOBS groupe 177. Le garde-fou a **refusé** la distance PC16 `-44510` (maximum autorisé 32766 en valeur absolue). Aucun binaire de cette tentative n'a été distribué.

La réalisation correcte utilise le **groupe B8 n°181 déjà atteignable** :

1. Reproduire exactement le préfixe source du pont P0 `Bank Free` dans le cinquième groupe, puis **ajouter** un pont de lecture indépendant.
2. Résoudre le point d'entrée `relay_read_entry` de BOBS 177 à partir du vrai callback End A5+1CC/+1D0 et de décalages dérivés des **labels source vérifiés**, sans adresse physique ou branche PC16 entre groupes.
3. Vérifier MC68020, propriétaire A5, `TypeOfMem`, marqueur `B8RG`, deux formes de callback B7/B8 et les deux longs de signature native du relais avant `JSR`.
4. Retourner les champs stockés de l'objet actif uniquement si le relais a réellement réussi, sinon `-32769`.

Le Code MC68020 des groupes historiques, dont BOBS, reste **byte-identique**. La candidate conserve tous les offsets de groupe et passe le garde-fou PC16.

## 4. Tests et preuves

- **[GitHub Actions P1a Gate A — PASS, 110 contrôles](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44829476430)** : vrais octets natifs MC68020 dans Unicorn, deux placements mémoire simulant interpréteur et Compiler, plus simulation des stubs et dispatchers AP20 V2 ; signatures, `GetP`, ABI, valeurs négatives, Bob absent, OFF, propriétaire étranger, CPU insuffisant, callback invalide, et conservation de P0.
- **[Politique CPU et chemins de livraison — PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44829476435)**.
- Builder [`build_m19_p1a_getters_in_memory.py`](../tools/build_m19_p1a_getters_in_memory.py) : reconstruction deux fois, SHA/longueur de la candidate et SHA native désormais **figés** ; source [`m19_p1a_bob_getters_emit.py`](../tools/m19_p1a_bob_getters_emit.py) ; [banc MC68020](../tools/test_m19_p1a_getters_gate_a.py) ; [workflow dédié](../.github/workflows/m19-p1a-getters-gate-a.yml).
- Le banc de test reprend l'environnement P0 Bank Free exact ; aucun `.asc` de `tests/current`, de `tests/passed` ni fichier de `dist/` n'a été modifié.

**Gate A : PASS (sur les tests simulés décrits). Gate B Runtime : NON TESTÉE. Gate C vrai AMOS Compiler : NON TESTÉE. Gate D Amiga physique : NON TESTÉE.** Les deux modèles d'adressage de la Gate A ne prouvent pas un vrai exécutable AMOS Compiler.

## 5. Suite P1

**Pour proposer un essai WinUAE Gate B**, une décision explicite supplémentaire devra autoriser une **bascule** de l'unique `dist/AMOSPro_AGA.Lib` vers le SHA P1a et la préparation du seul ASC de campagne. `LAST_GOOD` P0 reste protégée et ne devra pas être remplacée par cette décision.

Sans cette bascule, la prochaine tranche source-only est P1b : appliquer les hotspots déjà présents dans le format AGBO v1 au dessin Bob, avec vérification des masques, du clipping pixel et du fond dans les deux buffers. P1c priorités et P1d `Limit Bob` restent ouvertes. Les sprites matériels et M20 attendent.

**CI globale :** la suite historique `Artifact integrity` a encore des contrôles antérieurs à P1 qui vérifient l'ancienne empreinte R84 `LAST_GOOD` (p. ex. R71). Ne pas confondre ce problème de migration historique avec la **Gate A dédiée P1a PASS** ni revendiquer que l'intégrité globale est verte.
