# Audit P2d — passage 11 : état initial Double Buffer et séquence de premier Bind B8

**24 novembre 2026 — `main` uniquement — lecture statique du HEAD `0772937068a3a199c5a522dcd93aff343d453c45`.** Aucun test, binaire, ASC, source native ni journal modifié. **P2d LAST_GOOD protégée, Sprite S1-P1e GELÉE**.

## 1. Les trois chemins natifs liés à auditer ensemble

| API P2d et entrée AP20 | Lieu natif réel | Fait source pertinent |
|---|---|---|
| `Aga Screen Open` — fonction index 12 | UNIT142+$0F4E2 | Ouvre le Screen privé, dont l'état est porté par `456(a5)`. Cet appel **n'implique pas** qu'un pool B8 Bob soit lié |
| `Aga Double Buffer` — fonction index 18 | [UNIT142+$00A80](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0772937068a3a199c5a522dcd93aff343d453c45/src/native/m19_p2d/M19_UNIT142_BLOCK_00A80_MC68020.s#L6-L70) | Alloue le DBState de 48 octets via **Exec AllocVec(-684)** avec flags `$00010001` (MEMF_CLEAR|MEMF_PUBLIC) ; crée les deux ports/messages, deux ScreenBuffers, associe l'état à `State+32`. La zone initialisée à zéro contient `DB+20=0` |
| `Aga Swap` — fonction index 181 | [BOBS+$0B606](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0772937068a3a199c5a522dcd93aff343d453c45/src/native/m19_p2d/M19_P2D_CONTROLS_MC68020.s#L73-L145) → [UNIT142 Swap](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0772937068a3a199c5a522dcd93aff343d453c45/src/native/m19_p2d/M19_UNIT142_BLOCK_00BA2_MC68020.s#L6-L89) | Avec **zéro Bob actif**, le wrapper P2d peut appeler directement le Swap historique ; une présentation réussie écrit **`DB+20=3`** (Safe+Disp pending), ce qui n'équivaut pas à une réception immédiate du message |

**Nuance :** `Aga Double Buffer` peut aussi retourner succès si un DBState existe déjà ; le scénario décrit ici correspond à la **première allocation réussie**. Les cas de Double Buffer appelé deux fois ou après réouverture sont des variantes de T01/T14, pas des preuves de nouveaux défauts.

## 2. Séquence conditionnelle atteignable par l'API publique (AGA-002)

1. `Aga Screen Open` puis premier `Aga Double Buffer` réussi : grâce à l'allocation `MEMF_CLEAR`, `DB+20 bit0=0`.
2. **Aucun Bob actif.** Premier `Aga Swap` (mode Auto éventuellement activé mais pool encore absent) : [`p2d_scan`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0772937068a3a199c5a522dcd93aff343d453c45/src/native/m19_p2d/M19_P2D_CONTROLS_MC68020.s#L98-L129) saute vers `p2d_swap` si les 64 slots sont inactifs. Le Swap historique peut réussir, **puis arme `DB+20=3`**.
3. Un Bob devient actif (bank valide, owner correct), puis Auto Update est activé ou demeure actif ; **aucune autre commande n'a acquitté SafePort**.
4. Au prochain `Aga Swap`, le wrapper P2d appelle `p2d_service_update` **avant** le Swap historique. Le premier Bind B8 passe par [`L_BOBS_0D738→0C51E→0BE32`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0772937068a3a199c5a522dcd93aff343d453c45/src/native/m19_p2d/M19_P2D_SERVICE_BODY_MC68020.s#L1402-L1457).
5. Le [sélecteur `L_BOBS_0BE32`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0772937068a3a199c5a522dcd93aff343d453c45/src/native/m19_p2d/M19_P2D_SUPPORT_TAIL_MC68020.s#L595-L671) **refuse immédiatement `DB+20 bit0=1` sans faire `GetMsg(-372)`**, même si la notification est déjà disponible. Il ne crée pas le root B8.
6. [`p2d_refused`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0772937068a3a199c5a522dcd93aff343d453c45/src/native/m19_p2d/M19_P2D_CONTROLS_MC68020.s#L130-L145) retourne 0 **sans accéder au Swap historique**, qui aurait pu acquitter le message. [`Aga Wait Vbl`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0772937068a3a199c5a522dcd93aff343d453c45/src/native/m19_p2d/M19_UNIT142_BLOCK_00A62_MC68020.s#L6-L15) appelle seulement `WaitTOF` ; répéter `Wait Vbl→Swap` sans autre `GetMsg` peut donc reproduire le même refus tant que le bit reste posé.

**Conclusion source :** les préconditions de AGA-002 ne sont **pas inhérentes au premier Swap après Double Buffer**. Il faut que la page ait déjà été présentée **ou qu'un état pending existe réellement** avant le premier Bind Bob. Le scénario ci-dessus est un **chemin d'API plausible atteignable dans le code**, pas une simulation CPU ni un test WinUAE exécuté. Un refus de Swap avant que le message Safe soit disponible est légitime ; le suspect est **l'absence d'acquittement lorsque le message est prêt**.

Cette distinction explique pourquoi le [banc P2 ALL IN ONE](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0772937068a3a199c5a522dcd93aff343d453c45/tests/current/M19_P2_ALL_IN_ONE.asc#L129-L152) peut réussir : il prépare le fond par `Aga Blit Fill`, déclenche son premier Swap dans une chronologie différente, puis acquiert Safe via le prochain Fill. Un PASS de ce banc n'est **pas** une validation du cas « Swap sans Bob → premier Bind avec Bob sous Safe pending ».

## 3. Discriminant T02 exact à spécifier (aucun programme créé)

| Variante de T02 | Prérequis contrôlés | Résultat attendu pour attribuer la cause |
|---|---|---|
| **A — DB neuf** | Open, Double Buffer neuf, bit Safe=0, aucun Bob, premier Swap | La voie directe doit être accessible ; aucune attente de Bind B8 par erreur |
| **B — premier Swap sans Bob puis Bind** | Premier Swap réussi, bit Safe=1, root B8 absent, Bank valide, Bob actif, Auto Update 1 ; **aucun GetMsg intermédiaire** | Si le second Swap refuse sans consommer Safe alors que le message est déjà prêt, AGA-002 est corroborée |
| **C — même séquence avec acquittement** | Même état que B, Safe réellement disponible, puis une **commande correctement gardée** (par ex. `Aga Blit Fill` retournant 1) avant le Bind | Si Bind réussit ensuite, localiser la dépendance Safe ; ne pas modifier artificiellement les Bobs/caches |
| **D — notification absente** | Même état mais port Safe sans message | Un refus 0 **sans écriture** est légitime, ne doit pas être étiqueté freeze |
| **E — pool B8 déjà alloué** | Bind réussi d'un cycle antérieur, Safe pending | Comparer la voie B8 d'exploitation qui possède déjà `GetMsg` à la voie initiale |

**Gate A après autorisation** : émuler AllocVec MEMF_CLEAR, ports Safe/Disp, ChangeScreenBuffer et GetMsg, avec journal des valeurs `DB+20`, nombre de Bobs et root B8 ; vérifier le retour D3, les opérations graphiques et l'absence de DMA non Safe. **Gate B/C après autorisation** : programme ASC minimal isolé distinct de `tests/current/M19_P2_ALL_IN_ONE.asc`, logs complets, P2d SHA réellement installée.

## 4. Risques à ne pas confondre

- **AGA-001/A010 P0** : écrivains directs IFF et SetRast sans GetMsg après Swap ; **problème de sécurité**, distinct d'un **refus** B8 de progresser.
- **AGA-002 P1** : la première constitution de pool B8 bloque le chemin qui acquitte le Safe, seulement selon la séquence précisée.
- **AGA-003 VM** : les images de fond doivent suivre **Clear → décor → Swap** si des snapshots B8 sont déjà actifs ; ce contrat n'explique pas un **premier Bind refusé** sur Safe pending.
- **AGA-013 P2** : `CLOSE_RETURNED=1` dans le banc historique signifie retour de contrôle, **pas** preuve de libération ; non pertinent comme oracle de Safe.
- **Préparation par Fill** : elle peut acquitter un Safe déjà disponible. **Sa présence peut masquer la dépendance**, mais aucun remplissage fictif ne doit être ajouté au banc de diagnostic pour obtenir un PASS.

## 5. Statut du passage 11

**AGA-002 : P1 structurelle conditionnelle, scénario source maintenant précisément atteignable.** Aucune cause exacte de l'`ERR 15` EDGE rapportée comme démontrée. **T01/T02/T05/T17 à enrichir**, sans écrire de nouveaux tests ni modifier les 19 scénarios existants en nombre.

**Aucune modification de la Lib P2d LAST_GOOD, de la candidate S1-P1e, des sources MC68020, des assets et des journaux.** La clôture exige encore les tests différenciant Safe absent / prêt non acquitté / déjà acquis et la Gate B Runtime WinUAE.
