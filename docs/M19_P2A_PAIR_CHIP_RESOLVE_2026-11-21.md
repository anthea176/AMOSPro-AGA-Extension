# M19 P2a — Pont natif P0f + P0j-b3 / images Chip

**21 novembre 2026 — source-only MC68020 — Gate A du pont privé PASS**

## Livrables et provenance

- [Émetteur MC68020](../tools/m19_p2a_pair_chip_resolve_emit.py) : **946 octets**, SHA256 `7ee9fa70673b8827bde31d12e1023982a7439f80c77c34e84d9c73438e678548`
- [Tests natifs](../tools/test_m19_p2a_pair_chip_resolve_gate_a.py) : **8/8 PASS**
- [CI complète P2a](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44903500981) : 66/66 tests fonctionnels PASS
- [Raccord P0f 328 octets](M19_P2A_PAIR_CHECKED_READ_2026-11-21.md) et [noyau de collision 764 octets](M19_P2A_COLLISION020_NATIVE_2026-11-21.md) conservés byte-for-byte

Le nouvel émetteur reprend sans les modifier les 328 octets du contrôleur de paire P0f et ajoute une entrée privée utilisant les vraies routines sources natives P0f et P0j-b3. La bibliothèque P1e active et LAST_GOOD restent identiques : **124 444 octets**, même blob Git `5bb0c476c2b286495a1d0cf7d4415dbbc4eec369`, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`.

## Interface privée — non accessible depuis AMOS

| Entrée | Signification |
| --- | --- |
| D0 / D1 | Identifiants Bob A et B, distincts, 1..64 |
| A1 | Sortie **120 octets** : zone moteur alignée, writable, contiguë |
| A4 | Adresse **interne de confiance** de P0f identity_check_entry |
| A6 | Adresse **interne de confiance** de P0j-b3 explicit_image_resolve_entry |
| A5 | Propriétaire AMOS courant |

Retour : D3=1 succès, D3=0 refus et **aucune modification des 120 octets de sortie** ; D2=0. Tous les autres registres AMOS et la pile sont préservés. Le tampon contient [Bob A : 24][Image Chip A : 36][Bob B : 24][Image Chip B : 36]. Les 36 octets d'image P0j décrivent pointeurs des plans et masque Chip, largeur, hauteur, pas de ligne, profondeur, taille de plan et bornes de l'allocation.

## Séquence vérifiée

1. Rejeter les identifiants égaux/hors limites, les pointeurs privés nuls/impairs et un tampon de destination rejeté par TypeOfMem.
2. Lire deux objets actifs via le **vrai identity_check P0f** : banque d'origine, Bnk.GetAdr, propriétaire, génération et stamp.
3. Résoudre les deux images via **P0j-b3**, sans modifier la banque sélectionnée ; vérifier la résidence Chip et les bornes des plans et masques.
4. **Relire les deux identités P0f et comparer les 48 octets** : refuser une mutation survenue pendant la résolution.
5. Publier les deux couples de descripteurs uniquement si les quatre étapes précédentes réussissent.

**Précondition : les deux banques doivent déjà avoir leur cache Chip préparé.** Le pont n'alloue et ne libère rien, ne dessine pas, ne modifie pas le sélecteur de banque et ne fait aucun Swap. Les deux callbacks sont uniquement des adresses privées résolues depuis la source, jamais des pointeurs fournis par un programme AMOS. TypeOfMem aux deux extrémités ne prouve pas qu'un tampon arbitraire est complètement valide : le moteur doit fournir un scratch de 120 octets réel et détenu. Les pointeurs Chip ne valent que pendant cette opération synchrone.

## Validation et limites

**8 tests MC68020 PASS**, sur deux implantations distinctes, avec services Amiga simulés : deux banques et masques AGBO exacts ; absence de cache de la seconde banque ; génération périmée première/seconde banque ; mutation tardive de la première banque pendant la résolution de la seconde ; Bob OFF, mauvais propriétaire, mauvais IDs/callbacks/alignement ; garde CPU 020 ; préservation des registres, objets, données Chip et banque sélectionnée. Le premier essai utilisait l'adresse AGA Init 0x300000 pour charger le banc privé ; le banc corrigé utilise 0x380000/0x480000 et la CI est PASS.

**66 tests applicatifs PASS** : 17 géométriques + 23 raccord AGBO hôte + 9 noyau de collision 68020 + 9 vérifications P0f 68020 + 8 nouveaux P0f/P0j-b3 68020.

**Gate A du pont privé : PASS sous Unicorn. Gate A de la chaîne de collision complète : NON TESTÉE. Gate B WinUAE, Gate C vrai Compiler et Gate D physique : NON TESTÉES.** Aucune commande AP20, nouvelle Lib ou ASC n'a été publié.

## Suite

Récupérer les hotspots AGBO signés par une voie P1b validée, appliquer le clipping écran/P1d (limite globale + limites locales), construire les deux descripteurs de collision de 40 octets et relier le noyau natif 764 octets. L'interface publique Aga Bob Col reste une proposition, non implémentée.
