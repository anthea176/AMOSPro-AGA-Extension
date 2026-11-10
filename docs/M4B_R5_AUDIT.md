# Audit R4 -> R5 — issue #2

9 novembre 2026. Audit du code et des binaires à `dcd10a3`, publication après
le nettoyage `30ec44b`. R4/R5 et M4a n'ont pas été modifiés. Aucun R6 produit.

## Résultat

**R5 n'a ni déplacé ni modifié l'entrée Aga Screen Open par rapport à R4.**
Le code Open, son GetP, ses tokens, son offset et le Cold sont identiques.
L'hypothèse d'une corruption AP20 de cette entrée est écartée pour les
binaires du dépôt. Cela ne prouve pas l'identité de la bibliothèque installée
dans le disque Amiga avec celle du dépôt.

Deux défauts graves, déjà présents dans R4 et conservés par R5, sont prouvés :

1. **Collision état+28 : profondeur d'écran contre pointeur DBState.** Open
   laisse 8 à cet endroit après une ouverture réussie en 256 couleurs.
   Double Buffer prend cette valeur non nulle pour un pointeur déjà alloué,
   retourne 1 sans aucune allocation et laisse A3=8.
2. **A3 détruit par Close, Double Buffer, Swap et Back Fill.** Leurs MOVEM
   ne sauvegardent/restaurent pas A3, alors que ces routines l'écrasent.
   A3 est la pile de paramètres AMOS. R4 a corrigé D3 sans corriger A3.

Le dump fourni confirme un **crash du processus Windows WinUAE**. Il ne
permet pas d'attribuer avec certitude ce crash à une commande AMOS donnée.
**La cause exacte de l'aggravation R4 -> R5, avant le message OPEN visible,
reste non établie.** Les défauts hérités expliquent des chemins dangereux,
mais ne doivent pas être présentés comme la preuve d'une régression propre
à R5. L'issue reste ouverte sur ce point ; pas de nouveau binaire par essai.

## Diff structurel exhaustif

Offsets relatifs au début du code AP20 ; tailles en octets, GetP de l'entrée
suivante inclus dans le span précédent.

| # | Routine | Début R4 | Début R5 | Taille R4 | Taille R5 | Octets identiques |
|---|---|---:|---:|---:|---:|---|
| 0 | Cold/hooks/état | 0 | 0 | 188 | 188 | oui |
| 1 | vide/réservé | 188 | 188 | 4 | 4 | oui |
| 2 | réservée | 192 | 192 | 16 | 16 | oui |
| 3 | Probe | 208 | 208 | 16 | 16 | oui |
| 4 | Detect | 224 | 224 | 96 | 96 | oui |
| 5 | Demo | 320 | 320 | 334 | 334 | oui |
| 6 | Screen Open | 654 | 654 | 386 | 386 | oui |
| 7 | Screen Pattern | 1040 | 1040 | 150 | 150 | oui |
| 8 | Screen Close | 1190 | 1190 | 182 | 202 | non |
| 9 | Wait Vbl | 1372 | 1392 | 30 | 30 | oui |
| 10 | Double Buffer | 1402 | 1422 | 150 | 180 | non |
| 11 | Swap | 1552 | 1602 | 114 | 178 | non |
| 12 | Back Fill | 1666 | 1780 | 112 | 112 | oui |
| 13 | vide final | 1778 | 1892 | 0 | 0 | oui |

Les spans en mots R5 sont
`94,2,8,8,48,167,193,75,101,15,90,89,56,0`.
Header R4 : `(28,208,1778,60)` ; R5 : `(28,208,1892,60)`.
Fichier : 2136 -> 2248 octets. Les 114 octets de code ajoutés et le changement
de remplissage HUNK expliquent l'augmentation de 112 octets du fichier.

Le code commence à l'offset fichier 290 dans les deux versions. Open commence
donc à **944** ; son GetP à **940**. Token Open à +52 dans la table :
index fonction 6, signature `00,0,0,0`. Le patch de paramètres s'effectue
sur le même GetP et vise le même corps de routine. L'autre dispatcher
paramétré, Back Fill #12, suit correctement son nouveau cumul.

SHA256 du segment Open (386 octets, données et GetP suivant inclus) :
`df7a21603b67089693a703ea571e6be1b6056b2c80ef891b6699e9119efa95af`.
Même segment dans M4a. Les branches et LEA PC-relative internes sont
inchangés. Aucun mot aligné `$FE?1` de pseudo-relocation AMOS n'est présent
dans les blocs de code R4/R5. Les nouvelles branches 16 bits R5 ont été
désassemblées : leurs cibles restent dans les routines concernées.

**Équivalence prouvée :** pour le même état initial, les mêmes arguments et
les mêmes services OS, le chemin Open est identique. **Non prouvé :** mêmes
adresses d'allocation absolues, même état de la machine au lancement, même
librairie installée, comportement de WinUAE/JIT identique.

Empreintes des fichiers audités :

```text
R4 1f982aea0ffb29112a1a4c8b28d71810bf0e8dad2391da3c95dd6902ca9a2da1
R5 b6ce097684f104509e67c627bf122c319b14f64f1392b92740eac8d54c4164af
M4a ae4b863083e32c38e85192ac760aa143d3585c51d600449056075111da213b0e
```

## État partagé : défaut démontré

Désassemblage de l'entrée #6, offsets internes :

```asm
00c4 move.l d6,d1           ; nombre de couleurs
00c6 moveq #0,d0
00c8 lsr.l #1,d1
00ca addq.l #1,d0
00cc cmpi.l #1,d1
00d2 bne.w $00c8
00d6 move.l d0,$001c(a2)    ; profondeur, 8 pour 256 couleurs
...
0134 moveq #1,d3           ; succès
0136 bra.w $0152           ; aucun effacement de +28 sur succès
013a clr.l $001c(a2)        ; chemin d'échec seulement
```

Dans Double Buffer R5 :

```asm
0018 movea.l $001c(a2),a3
001c move.l a3,d0
001e tst.l d0
0020 bne.w $0080            ; 8 != 0 : branche prise
...                        ; AllocVec/CreateMsgPort/AllocScreenBuffer sautés
0080 moveq #1,d3
0082 bra.w $00a8
```

Le test ciblé suit les déplacements du binaire : D3=1, A3=8, zéro appel OS.
Ce n'est donc **pas une preuve d'allocation réussie** d'observer DOUBLE BUFFER=1.
R4 possède le même chemin avec une autre position de cible. Swap R5 lit
ensuite `12(A3)`, donc l'adresse Amiga `$14` si A3=8 ; R4 commençait par
`8(A3)`, donc `$10`. Ces adresses basses ne sont pas des DBState valides.
Cette différence change les effets du défaut hérité, mais ne prouve pas
que Swap ait été atteint dans l'incident rapporté.

Close R4/R5 lit également le faux DBState, même sans appel à Double Buffer.
Un test Open/Close R5 n'est donc pas anodin. Il faut réserver +28 exclusivement
au pointeur, garder la profondeur dans un registre/champ distinct et publier
le pointeur seulement après initialisation complète. Conserver M4a archivé.

## Registres AMOS

`48e7ffee` / `4cdf77ff` sauvegardent/restaurent D0-D7,A0-A2,A4-A6 : **A3 absent**.
`48e7efee` / `4cdf77f7` excluent également D3, mais toujours A3.
Ces masques sont utilisés par les quatre routines qui chargent DBState en A3.

Le contrat décrit par [+Music.s, section ABI](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BMusic.s#L2340)
exige de restituer A3 au niveau précédant la collecte des paramètres et de
préserver A4-A6/D6-D7. Les fonctions sans argument ne doivent pas modifier
A3. Back Fill n'a qu'un argument, fourni dans D3 : il n'a rien à dépiler.

Dans une future correction, sauvegarder/restaurer A3 ou utiliser un registre
autorisé ; conserver l'exclusion de D3 pour les résultats. Vérifier la
symétrie des masques et tous les retours, pas seulement la valeur retournée.
Open dépile bien ses trois premiers arguments et prend le dernier dans D3.

## NDK : structures et vecteurs vérifiés

Calcul à partir des déclarations assembleur, pas d'un layout C hôte :
[screens.i](https://raw.githubusercontent.com/kusma/amiga-dev/master/targets/m68k-amigaos/ndk/include_i/intuition/screens.i),
[view.i](https://raw.githubusercontent.com/kusma/amiga-dev/master/targets/m68k-amigaos/ndk/include_i/graphics/view.i),
[ports.i](https://raw.githubusercontent.com/kusma/amiga-dev/master/targets/m68k-amigaos/ndk/include_i/exec/ports.i).

| Champ 68k | Offset/taille |
|---|---:|
| ScreenBuffer.sb_BitMap | 0 |
| ScreenBuffer.sb_DBufInfo | 4 |
| Node | 14 octets |
| Message.mn_ReplyPort | 14 |
| Message | 20 octets |
| DBufInfo.dbi_SafeMessage | 8 |
| SafeMessage.mn_ReplyPort relatif au DBufInfo | 22 = $16 |
| DBufInfo.dbi_DispMessage | 40 |
| DispMessage.mn_ReplyPort relatif au DBufInfo | 54 = $36 |
| MsgPort.mp_Flags / mp_SigBit / mp_SigTask / mp_MsgList | 14 / 15 / 16 / 20 |
| MsgPort | 34 octets |

R5 emploie correctement `sb_DBufInfo+4` puis `ReplyPort+$16`. Le port est
obtenu par CreateMsgPort, pas alloué avec une taille de structure inventée.
Le test vérifie l'arithmétique des includes ; ce n'est pas un test du protocole.

| Appel | LVO | Entrées principales | R5 |
|---|---:|---|---|
| CreateMsgPort | -666 | aucune, résultat D0 | correct |
| DeleteMsgPort | -672 | A0=port | correct |
| WaitPort | -384 | A0=port, résultat D0 | correct |
| GetMsg | -372 | A0=port, résultat D0 | correct |
| AllocVec | -684 | D0=taille,D1=flags | correct |
| FreeVec | -690 | A1=bloc | correct |
| AllocScreenBuffer | -768 | A0=screen,A1=bitmap,D0=flags | correct |
| FreeScreenBuffer | -774 | A0=screen,A1=buffer | correct |
| ChangeScreenBuffer | -780 | A0=screen,A1=buffer | correct |

Les LVO Exec correspondent aussi aux includes `lvo/exec_lib.i` de la
référence AMOS locale. Bases A6 Exec/Intuition et registres vérifiés dans
le désassemblage. Ce sont les valeurs de pointeurs en amont qui sont invalides.

## SafeMessage : ce qui est correct et ce qui manque

Selon [AllocDBufInfo](https://developer.amigaos3.net/autodocs/graphics.library/AllocDBufInfo.html),
SafeMessage annonce que **l'ancien bitmap** n'est plus lu ; DispMessage
annonce que le nouveau a été affiché au moins une fois. Avec
[AllocScreenBuffer](https://developer.amigaos3.net/autodocs/intuition.library/AllocScreenBuffer.html),
le DBufInfo est obtenu via le ScreenBuffer fourni à ChangeScreenBuffer.
Ne pas confondre le buffer porteur du message et l'ancien bitmap protégé.

Attendre le SafeMessage dans le même appel Swap n'est **pas intrinsèquement
un deadlock** : la tâche peut dormir pendant que l'affichage progresse.
R5 attend seulement après succès de ChangeScreenBuffer et emploie WaitPort
puis GetMsg ; WaitPort ne retire pas le message. Son retry utilise WaitTOF.
Le manque de DispMessage ne prouve pas, à lui seul, le crash avant Open.

En revanche, R5 ne suit pas explicitement les messages en vol, n'identifie
pas le message attendu, ne synchronise pas DispMessage et n'a pas de sortie
de retry/attente contrôlée. Le protocole robuste proposé est :

1. Après correction état/A3, allouer deux ScreenBuffers et les ports ;
   initialiser les champs Safe/Disp des DBufInfo concernés et un état explicite
   des messages attendus. Pas d'attente avant le premier changement.
2. Avant rendu, attendre la sécurité de l'ancien bitmap ; avant un nouveau
   changement, attendre l'affichage de la transition précédente si nécessaire.
   Identifier chaque message par son adresse et son type, puis le retirer.
3. Attendre la fin du blitter, tenter ChangeScreenBuffer ; ne mettre à jour
   l'index courant et les messages attendus qu'après succès.
4. Pour une API bloquante simple, collecter Safe **et** Disp de cette
   transition avant retour. Ne pas traiter les notifications déjà répondues
   comme de nouvelles requêtes à ReplyMsg.
5. Sur Close/RESET/END, achever les notifications en vol, vider les ports,
   attendre le blitter, libérer les ScreenBuffers, puis les ports, puis
   DBState et l'écran. Rendre le nettoyage idempotent.

L'ordre est cohérent avec les autodocs et le
[RKRM, Screens under Release 3](https://developer.amigaos3.net/sites/default/files/downloads/2024-02/RKRM%20changes%20and%20additions-%282024-02-21%29.pdf).
R4 reste une base **de diagnostic**, pas une implémentation sûre à remettre
en service sans corriger ses défauts hérités.

## Nettoyage et Back Fill

R5 libère les deux ScreenBuffers avant DeleteMsgPort, mais cet ordre seul
ne prouve pas que tous les messages ont été collectés. Il n'existe aucun
suivi d'attente dans Close. Sous V39, il faut explicitement attendre le
blitter avant FreeScreenBuffer ; voir
[FreeScreenBuffer](https://developer.amigaos3.net/autodocs/intuition.library/FreeScreenBuffer.html).
Les échecs d'allocation avant publication ont un chemin de libération,
mais sont normalement court-circuités par le faux pointeur de profondeur.

Cold/RESET/END sont toujours ceux de M4a. Ils ne libèrent ni ScreenBuffers
ni MsgPort/DBState ; après correction de l'allocation, ce sera un défaut
de cycle de vie effectif. Mettre tous les chemins de fermeture en cohérence.

Back Fill n'a pas changé en R5. Il modifie temporairement le RastPort de
l'écran et souffre d'A3 et du faux pointeur. Préférer un RastPort de rendu
distinct après avoir défini l'ownership et la synchronisation ; aucune
validation de Back Fill ne découle du présent audit.

## Minidump fourni : faits et limites

Fichier local analysé, **non publié** :
`winuae_x64_6.0.3_R_2026.11.09_11.44.33.dmp`, 277216 octets.
SHA256 `c48d36b77ecd45ebacfa0fed269faf0e0208cc68a688f3731b9ed2b3db9eb57c`.

- Exception Windows `0xc0000005`, lecture invalide à `0x19a19585`.
- Thread `0xcd54`, RIP `0x10559285`, module WinUAE base `0x10000000`,
  donc RVA `0x559285`.
- Contexte de l'exception : RAX=`0x19a19582`, RSP=`0x15abb8`.
  Instruction capturée : `movsx r8d, byte ptr [rax+3]`. L'adresse calculée
  correspond exactement à l'adresse fautive.
- La séquence voisine ressemble au handler OR.B immédiat de
  [WinUAE cpuemu_0.cpp](https://github.com/tonioni/WinUAE/blob/master/cpuemu_0.cpp).
  C'est une **inférence de désassemblage**, pas une résolution par symboles
  de cette build ni un PC Amiga retrouvé.
- La configuration embarquée confirme 68030/68882, `cachesize=16384`,
  `comp_catchfault=true`, modes cycle-exact désactivés. Le JIT est configuré,
  ce qui ne prouve pas qu'il soit la cause du défaut.
- Pas de Memory64List/full memory dans ce dump ; l'état global des registres
  invités et la mémoire Amiga nécessaires à l'attribution ne sont pas inclus
  aux adresses examinées. Le contexte des threads au moment de l'écriture
  est distinct du contexte d'exception : seul ce dernier est utilisé ici.
- Les streams privés contiennent un bootlog et une configuration utiles,
  mais aussi un journal daté du 25 juillet mentionnant WinUAE 2.3.2 : ce journal
  ancien n'est **pas** une trace d'exécution du crash R5 de novembre.

L'absence de `OPEN =` visible ne suffit pas à conclure que Open n'a pas
retourné : un écran Intuition peut masquer l'écran AMOS et le test ne force
pas le retour au premier plan. C'est une explication possible, pas une
observation confirmée de cette session. Il faut des étapes séparées.

## Vérification, test minimal et prochaine preuve

```powershell
python -B -m unittest discover -s tools -p test_m4b_r5_audit.py -v
python -B -m unittest discover -s tools -p test_m4b_r5.py -v
python -B tools/audit_m4b_runtime.py dist/experimental/AMOSPro_AGA_M4b_v0.0.6_R5.Lib
python -B tools/inspect_winuae_dump.py "CHEMIN_LOCAL_DU_DUMP"
```

Résultat : **9 nouveaux tests et 6 tests R5 existants passent**.
Les deux comparaisons tuple/liste de `build_m4b_r5.py` et
`test_m4b_r5.py` ont été corrigées : elles provoquaient une AssertionError
indépendante du crash Amiga. Le générateur reproduit ensuite exactement
le binaire R5 existant, en mémoire, sans écrire de nouvelle bibliothèque.

Neuf nouveaux tests : identité Open/Cold, diff des spans, dispatchers,
mutations contrôlées (span équilibré mais faux, index valide mais mauvaise
routine, octet Open altéré), détection du conflit +28 et d'A3, chemin de faux
succès sans allocation, offsets NDK et contrôle du test AMOS minimal.
L'auditeur runtime renvoie **1** sur R4/R5, volontairement ; les tests passent
parce qu'ils attendent ces rejets. Ils ne constituent pas une approbation
runtime ni un validateur exhaustif du code 68k/protocole.

`tests/historical/M4B_AUDIT_01_OPEN_CLOSE.asc` n'utilise que Open/Close, des marqueurs,
Amos To Front et des pauses. Contrôle de référence avec M4a ; réservé à un
futur candidat corrigé pour M4b. **Ne pas l'utiliser comme validation de R5
actuel : son Close est dangereux même sans Double Buffer.**

Le test est écrit avec If/End If, sans Then imbriqué. Le
[manuel AMOS](https://amospromanual.dev/05-04-control-structures.html) autorise
If/Then en général, mais interdit son mélange dans les tests structurés.
Le stress test historique mélangeait les deux. Il reste retiré ; le nouveau
test est relu statiquement, **pas encore parsé/exécuté par AMOS365**.

Pour lever le blocage de causalité : vérifier l'empreinte de la Lib réellement
installée, capturer PC/A3/A5 et la zone ExtAdr au point de rupture du crash
dans le débogueur WinUAE (ou un état complet exploitable). Comparer une
session neuve avec et sans JIT, à configuration identique par ailleurs,
sans prendre un succès sans JIT pour une correction de l'extension.
Après correction revue, suivre : chargement seul, Open/Close seul,
allocation seule, un Swap, puis N swaps ; pas de stress monolithique initial.
