# P5 — 3 unités AP20 réelles : AGA / C2P / décodeur IFF

**Base strictement immuable : R82 \`LAST_GOOD\` v0.13.27.**
Branche de travail : \`experiment/ap20-v3-multiunit-64k\` uniquement.
\`main\` et \`LAST_GOOD\` restent figés. Sur la branche expérimentale, **\`dist/AMOSPro_AGA.Lib\` est désormais la P5 active**. Le programme ASC courant est inchangé.

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

## P5 -- preuves WinUAE du vrai decoupage en trois modules (14/11/2026)

**Gate A CPU/CI : PASS** (CI run 43640114763, huit tests positifs,
simulation MC68020 des trois dispatchers, 78 relocalisations RBSR
contrôlées et quatre BSR.L de palette vérifiés).

**Gate B Runtime : smoke PASS (capture utilisateur).**
Le test `P5_R82_3UNITS_SMOKE.asc` montre à l'écran
`AGA -1`, `C2P OPEN 0`, `CLOSE 0`, `IFF REJECT 0`,
`RESULT 1`, `ERR 0` et erreurs d'ouverture/fermeture du log nulles.
La capture ne fournit pas de mesure mémoire détaillée ni de journal
Runtime archivé ; ne pas extrapoler.

**Gate C Compiler : smoke PASS (journal utilisateur archivé).**
[Journal P5 compilé](evidence/AP20_V3_R82_3UNITS_P5_COMPILED_2026-11-14.TXT) :
`RUN_MODE COMPILED`, `PRG_STATE -1`, `RESULT 1`,
`VERDICT PASS`, `R82_DETECT -1`,
`C2P_OPEN_REJECT 0`, `C2P_CLOSE_REJECT 0`,
`IFF_REJECT 0`, `ERR 0`. Chip Free `1765976 -> 1765976`
et Fast Free `137868480 -> 137868480` : deltas nuls.
Le fichier original utilisateur fait 260 octets CRLF, SHA256
`bfccacf184a51a2f161c9f6432061a4a9fcbf29274bfa3e11881146882bdda00`.

**Conclusion prouvée :** chargement et dispatch fonctionnels sous
WinUAE en Runtime et en compilé pour trois véritables unités natives
R82, d'une taille native cumulée de 73 040 octets, sans modification
d'AMOS Compiler.

**Périmètre restant :** tests fonctionnels positifs des images/palettes
AGAPIC, C2P et décodage `Aga Iff To Chunky` avec cette P5 ; les
résultats complets de la P4 ne valent pas validation P5. Aucune
qualification sur Amiga physique ni mode purement interprété.
Aucune fusion / promotion R83 / modification de `main` ou `LAST_GOOD`.

## Candidat actif sur la branche expérimentale

La **seule bibliothèque active** est `dist/AMOSPro_AGA.Lib`, **76 188 octets**, SHA256 `db55149f19f2d4753232cb5768167f38c82e86c5e2613a056e093fa9c23897af`.
`dist/AMOSPro_AGA_LAST_GOOD.Lib` reste la **R82 historique** (64 112 octets), SHA256 `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36`.

Dans AMOS Extension n°14, le titre P5 attendu contient `THREE GENUINE NATIVE UNITS` ; `TRUE SPLIT C2P/AGA` correspond à l'ancienne P4.
La CI reconstruit la P5 et compare octet par octet la sortie à `dist/AMOSPro_AGA.Lib`.
