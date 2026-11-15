# M19 P0a — `Get AGA Bob` multi-images, candidat dérivé exclusivement de R88

**État initial du présent rapport : CODE NATIF PRODUIT ; Gate A CPU à confirmer par la CI ; Gate B/C NON TESTÉES.**

## Base autorisée et limites

- Référence binaire stricte : R88 v0.13.33 `dist/AMOSPro_AGA.Lib`, SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`, commit historique `7c575a02087d550611b8e966a7708b5f6a8c4b71`.
- `dist/AMOSPro_AGA_LAST_GOOD.Lib` : R84, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, non modifiée.
- Aucun exemple, builder ou source R89/R90 n'a été utilisé ; les nouveaux modules `P0a` sont ceux développés depuis R88.
- Bibliothèque candidate **reconstruite exclusivement en mémoire** : aucun `dist/` changé ; aucune installation WinUAE ni promotion.

## Commandes de l'expérience

- `Aga Bob Bank N` : sélectionne ou initialise de manière non destructive la banque DATA `AGBO`, n° 5..65535.
- `Get AGA Bob I,X1,Y1,X2,Y2` : instruction à **5 entiers** sans `To`, `I=1..4096`, coordonnées **inclusives**. Lit les bitplanes du back buffer privé **Safe** et `WaitBlit`; crée ou remplace l'image dans la banque `AGBO` active. Largeurs arbitraires, données **plan-major**, mask **absent** pour l'image capturée, opaque pour la couleur 0.

L'opération vérifie la sélection encore active, les en-têtes AMOS et AGBO, le répertoire complet, la contiguïté des données, les limites d'image, les masques préexistants, le padding nul, le contenu physique `BitMap` en Chip, les dimensions et la profondeur. La transaction finale crée une **nouvelle allocation AMOS** avant tout changement de liste, notifie `Bnk.Change`, puis libère l'ancienne banque. L'échec avant publication conserve l'ancien contenu, et le scratch Exec est toujours libéré.

Les masques des **autres images** sont recopiés inchangés. Pour l'image remplacée, le masque précédent disparaît délibérément : une nouvelle capture est opaque jusqu'à `Make AGA Bob Mask` (commande P0b non intégrée).

## Tests proposés

Depuis la racine du dépôt :

```sh
python -B tools/test_m19_p0a_get_bob_emit.py
python -B tools/build_m19_p0a_r88_get_in_memory.py
python -B tools/test_m19_p0a_r88_get_gate_a.py
```

La dernière commande exige `unicorn==2.1.4` et `capstone==5.0.9`. Les deux placements simulés (interprété / disposition compilée) exécutent réellement le **code MC68000** avec services AMOS/Exec/graphics simulés ; il ne s'agit **ni** d'un lancement AMOS sous WinUAE **ni** d'un exécutable produit par AMOS Compiler.

[Workflow GitHub Actions](../.github/workflows/m19-p0a-r88-get-gate-a.yml). Aucune sortie **Gate B/C** n'est revendiquée par ce document.

## Suite autorisée seulement après Gate A

Préparer l'ASC unique `tests/current/` **pour la candidate exacte**, installer uniquement dans `dist/AMOSPro_AGA.Lib` après accord et validation, essayer dans WinUAE (Gate B), puis AMOS Compiler (Gate C). Conserver R84 LAST_GOOD ; aucune promotion automatique.
