# M19 P0e — premier palier public des Bobs persistants : Set / Off (source-only)

Date : 16 novembre 2026. Dépôt `anthea176/AMOSPro-AGA-Extension`, **`main`**.

## Statut

**Source + Gate A native MC68020 PASS** pour deux premiers tokens AP20 V2 expérimentaux :

| Instruction visée | Contrat technique source-only | AP20 |
| --- | --- | --- |
| `Aga Bob N,X,Y,I` | Crée ou met à jour l'objet 1..64 ; mémorise la banque actuellement sélectionnée et l'image 1..4096. Aucun rendu ni Swap. | Stub 89, `I0,0,0,0` |
| `Aga Bob Off N` | Désactive un objet existant de numéro 1..64, sans détruire sa banque source. Aucun rendu ni Swap. | Stub 90, `I0` |

**ATTENTION : les deux nouveaux tokens sont uniquement produits en mémoire.** Ils n'existent **PAS** dans la `dist/AMOSPro_AGA.Lib` P0d installable actuelle et ne constituent pas encore un programme AMOS utilisable. L'extension **n'a pas encore de `Aga Bob Draw` ni de reset d'objets lors de Screen Close/End**. Aucune nouvelle version installable ne doit être produite avant ces deux correctifs et une Gate A complète.

## Code source

- [`tools/m19_p0e_public_object_ops_emit.py`](../tools/m19_p0e_public_object_ops_emit.py) : **38 octets de nouveaux wrappers MC68020** après les 502 octets du pont déjà vérifié. `Aga Bob` consomme **I dans D3**, puis Y/X/N depuis `(A3)+` (**A3+12**), conserve tous les registres AMOS obligatoires et délègue à `object_bridge_put_selected`. `Aga Bob Off` prend **N dans D3**, ne modifie pas A3 et délègue à `object_bridge_off`. D2=0, D3=0/1.
- [`tools/build_m19_p0e_public_object_ops_in_memory.py`](../tools/build_m19_p0e_public_object_ops_in_memory.py) : repart exclusivement de la candidate P0e de pont vérifiée, **remappe** les anciens RBSR de groupe +2, ajoute les deux stubs GetP, préserve octet pour octet les groupes V2 C2P/IFF/AGA et le préfixe BOBS/Blitter P0d, audite tous les tokens et les distances PC16. Candidate générée **en mémoire uniquement**, sans fichier `.Lib` ni deuxième programme actif.
- [`tools/test_m19_p0e_public_object_ops_gate_a.py`](../tools/test_m19_p0e_public_object_ops_gate_a.py) : vrais wrappers exécutés sous **Unicorn MC68020**, Capstone 020 ; **48 contrôles**, deux placements simulant l'interpréteur/Compiler, véritable code ancien `AGA Init` exécuté, banques 10/11, coordonnées négatives, mise à jour, Off répété, ID absent, mauvais propriétaire A5, CPU<020, écran fermé, A3/ABI/A7, erreurs sans mutation. **Exec/graphics/Intuition restent simulés**, pas de B/C WinUAE.

**Preuve CI :** [Gate A publique Set/Off PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43967949075), avec les tests du registre privé et du pont P0e antérieurs.

## Candidate en mémoire, strictement non installable

| Élément | Valeur |
| --- | --- |
| Base de provenance | Pont P0e, 94 144 octets, SHA256 `f49037880fe75a3314364642336b3e5fb8f9e7854214cc1a23049fbc1becd0de` |
| Nouveau source natif dans BOBS | **38 octets** |
| Candidate totale | **94 232 octets** |
| SHA256 de la candidate en mémoire | **`a1aab227dd8c1e19be88f11878513f341edfc92bf19f33520a029625a3827969`** |
| API candidate | **85 commandes, 95 entrées AP20** |
| Groupe BOBS / AGA | 23 652 / 58 912 octets |
| Déplacement BSR.W max avant / après | 32 698 / **32 760** |
| Marge sous garde signé 32 766 | **6 octets** |
| Gate A source / native | **PASS** |
| Gates B/C sur P0e | **NON TESTÉES** |
| `Aga Bob Draw` et `Close/End` reset | **NON IMPLÉMENTÉS** |

### Point d'architecture bloquant : épuisement de la portée PC16

**Il ne reste que 6 octets avant le seuil de sécurité**. On ne peut plus simplement append du code dans BOBS, et **l'ajout d'un troisième token `Aga Bob Draw` ferait très probablement échouer l'accès à certains groupes V2 existants**. Les 85 tokens sont seulement un **palier de démonstration**, pas l'architecture finale pour 3+ commandes publiques.

Avant de continuer, il faut restructurer la répartition des unités natives AP20 afin de *déporter le code nouveau hors de la chaîne critique* du déplacement signé BSR.W, en prouvant pour les stubs originaux (notamment les premiers indices et les entrées réservées) que l'interpréteur comme le Compiler restent valides. Le code de 64 objets et les signatures P0d/P0e figées sont les sources d'autorité ; ni désassemblage de production, ni nouvelles adresses arbitraires.

Le futur `Aga Bob Draw` doit, pour chaque objet actif, accéder **à la banque mémorisée**, pas simplement à `bank_active_state` courant. Le peintre P0d vérifie la banque sélectionnée avant le Blit : prévoir transaction de sélection/restauration, staging Chip unique par banque, vérifications AGBO après Erase/Load, clipping/masque pixel exact et **aucun Swap implicite**. Pour `Close/End`, effacer le registre P0e avant de détruire l'ancre AGA State et les buffers Chip, sans modifier rétroactivement les Gates P0d.

## Protections conservées

- **`dist/AMOSPro_AGA.Lib` P0d toujours active** : 91 300 octets, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`. Elle seule a ses Gates B/C WinUAE rapportées PASS avec confirmation visuelle.
- **Seul ASC actif** : `tests/current/M19_P0D_BOB_BLIT_01.asc`, non modifié.
- **`dist/AMOSPro_AGA_LAST_GOOD.Lib` R84** : 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, intacte.
- Aucune promotion, nouveau dépôt, branche, release ou ZIP.
