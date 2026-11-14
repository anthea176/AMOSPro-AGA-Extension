# P5 — 3 unités AP20 réelles : AGA / C2P / décodeur IFF

**Base strictement immuable : R82 \`LAST_GOOD\` v0.13.27.**
Branche de travail : \`experiment/ap20-v3-multiunit-64k\` uniquement.
Aucun changement de \`main\`, de \`dist/\` ou du programme ASC courant.

## Nouvelle découpe physique

- **Unité native 80 — C2P** : cinq entrées historiques 70–74,
  soit 5 524 octets de corps + 34 octets de dispatcher = **5 558 octets**.
  Conserve Open, Convert, Close, Blit et Zoom.
- **Unité native 81 — IFF → chunky** : entrée 75 seule,
  2 474 octets natifs + 34 octets de dispatcher + 12 000 octets
  de NOP *uniquement pour la contrainte de taille* = **14 508 octets**.
- **Unité native 82 — AGA + AGAPIC / palettes** : anciennes entrées
  0–69, puis 76–79, 52 940 octets natifs + 34 octets de dispatcher
  = **52 974 octets**.
- **Somme des unités : 73 040 octets** ; chacune reste sous la
  limite individuelle 65 534 octets AP20 / Compiler.
- Les 74 commandes publiques, indices, paramètres et \`GetP\`
  restent **identiques à R82**.

Les trois unités sont physiques et contiennent du code natif R82 réel.
Aucune entrée publique fictive ajoutée. Le remplissage NOP est placé
après le décodeur IFF, jamais exécuté.

## Dépendances et protections

- L'AGA historique conserve ses liens BSR.W / BRA.W connus, son
  état d'entrée clavier/souris et les sept références LEA.
- Les quatre BSR.L internes des palettes sont recalés vers les entrées
  historiques 41–44 sans changer leur longueur.
- Les entrées C2P 70–74 et l'entrée IFF 75 sont indépendantes au
  niveau des branches PC-relatives directes inspectées ; toutes les
  routines restent intactes.
- Le chargeur \`AMOS365\` remplace \`RBSR\` par \`BSR.W\` : **contrôler
  chaque displacement** de chaque commande native, y compris celui
  du dernier groupe 82. Un groupe lointain déclencherait
  \`Software Failure 80000004\`.

La simple découpe ne prouve **pas** une architecture à nombre de
modules illimité. Les dispatchers restent tous atteignables en BSR.W
depuis les stubs ; il faudra un contrat de liaison distinct au-delà de
cette portée pour dépasser cette contrainte durablement.

## Validation

- **Gate A** : tests de structure, API inchangée, cas négatifs, contrôle
  des 78 RBSR, émulation des vrais dispatchers sur MC68020, rebase des
  quatre BSR.L. CI doit réussir.
- **Gate B/C** : essais réels sous WinUAE 68020+, Runtime et Compiler
  (séparés) ; non revendiqués avant les journaux utilisateur.
- **Fonctionnel** : reprendre le banc AGAPIC R82 et la démo C2P
  avec image IFF, plus un essai réel \`Aga Iff To Chunky\` R80.
- **D** : machine Amiga physique non testée.

P4 (2 modules) reste disponible comme référence historique validée.
Aucune promotion en R83 ou remplacement de \`LAST_GOOD\` par cette P5.
