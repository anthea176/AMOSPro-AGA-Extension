# M5 — incident WinUAE après Swap / Close (10 novembre 2026)

**STATUT : BLOCAGE SÉCURITÉ MÉMOIRE. NE PAS TESTER LE CHEMIN DB+SWAP+Close SUR R6. NE PAS MERGER.**

## Faits runtime observés

- `Clown.iff` (320 × 200, 8 plans, ByteRun1, CAMG 0) fonctionne plusieurs fois.
- `Amiga fallout.iff` (640 × 512, 4 plans, ByteRun1, CAMG $00029000) ouvre le Screen ; crash WinUAE à l'appui sur une touche / sortie, et un autre essai plante à la relance.
- `Jeff-Flag.iff` (736 × 482, 4 plans, ByteRun1, CAMG $00019004) : `Aga Screen Open` retourne 0 sur la capture ; crash WinUAE également signalé.
- Le fichier utilisateur de test ILBM a été modifié avec `Aga Wait Key` ; sa séquence exacte n'est pas disponible.
- Quatre minidumps WinUAE 6.0.3 x64 reçus : tous `0xC0000005` (violation d'accès **en lecture**) au RIP `0x10559285`, avec un pointeur lu à `0x7606AAA3` dans trois cas, `0x2BA8FEB3` dans le quatrième. Ces adresses ne prouvent pas à elles seules l'élément fautif dans la mémoire Amiga.

## Anomalie de code constatée (source, non hypothétique)

La lib actuelle R6 hérite de `tools/build_m4b_r6b_r4.py` :

- `swap_nonblocking()` **retire** les notifications précédemment livrées par `GetMsg` sur les ports Safe/Disp, puis peut appeler `ChangeScreenBuffer`, mais **ne mémorise pas** de notification Safe/Disp encore attendue.
- `close_nonblocking()` appelle `WaitBlit`, puis `FreeScreenBuffer` sur SB1 et SB0 et `DeletePort` sur Safe/Disp **sans attendre les réponses du dernier `ChangeScreenBuffer` et sans traiter ses notifications**.
- Le helper `ctrl_c_cleanup_helper()` dans `tools/build_intuition_input_r3.py` comporte le même risque dans son chemin Double Buffer.
- Le builder R3-R6 a corrigé la fermeture de la **Window** avant le **Screen**, mais n'a pas modifié cette synchronisation Double Buffer.

L'ancien `tools/build_m4b_r6b_r1.py` possédait un indicateur `DBState+20` (allocation de 24 octets) : `swap_once()` le mettait à 1 après un Swap réussi et `cleanup()` attendait les messages Safe/Disp avant les libérations. **Ce protocole a disparu** lors de la réécriture non bloquante R6B-R4.

La spécification Amiga distingue les réponses :
- `dbi_SafeMessage` : l'ancien bitmap est disponible en écriture ;
- `dbi_DispMessage` : le nouveau bitmap a été affiché et une autre permutation est possible.

Elles sont asynchrones : **`WaitBlit` ne les remplace pas**. Pour la fermeture, il faut récupérer toutes les réponses attendues avant `FreeScreenBuffer` et `DeletePort`.

Sources publiques :
- https://d0.se/autodocs/graphics.library/AllocDBufInfo
- https://wiki.amigaos.net/wiki/Intuition_Screens
- https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node039A.html

## Diagnostic révisé

Le précédent `tests/current/M5_ILBM_INPUT_EXIT_DIAG.asc` enchaînait 3 phases, dont une avec `Aga Iff Load -> Aga Swap -> Aga Wait Key -> Aga Screen Close`. Cette phase est **retirée** : elle est inadaptée au protocole de fermeture actuel.

Remplacer par une seule phase **sans Double Buffer, sans Swap, sans IFF Load** :
`Aga Screen Open -> Aga Wait Key -> Aga Screen Close -> Amos To Front`.
Comparer une résolution 320×200 et la géométrie Fallout 640×512 uniquement dans des sessions WinUAE propres.
Tant que le chemin DB n'est pas corrigé, éviter les tests en boucle, l'appel immédiat à Close après Swap et les tests de charge répétés.

## Correctif requis (nouvelle version, R6 conservée)

1. Rétablir un état **explicitement suivi** des notifications Safe/Disp en vol. `DBState+20` existe déjà et peut servir de base, après vérification des autres usages.
2. Pour le `Swap`, ne pas écraser un état « en cours » ; ne pas supprimer silencieusement une notification indispensable.
3. Pour `Close` normal, cleanup extension et Ctrl+C : si un Swap est en vol, poll `GetMsg` sur **les deux** ports concernés et attendre coopérativement avec `WaitTOF` jusqu'à avoir obtenu les accusés de réception attendus.
4. **Interdiction de `WaitPort` ou Exec `Wait`**. Ne jamais détruire les buffers/ports tant qu'une notification les concernant peut encore arriver. Gérer l'échec de Swap, sans attente infinie ni double libération.
5. Tests CPU sur notifications immédiates/différées, plusieurs Swaps, double Close, échec `ChangeScreenBuffer`, Ctrl+C en Swap en vol, registres/ABI et stabilité en fin de vie. La suite doit d'abord **reproduire l'échec du R6**.
6. Les segments Generic ILBM R2 et PicInfo doivent rester identiques octet pour octet.
7. Reprise WinUAE uniquement après préflight : interprété, puis compilé, avec Clown et Fallout, relance à froid, puis répétition sans crash.

## Conclusion

**Une anomalie réelle de libération potentiellement prématurée est établie par le code.** Qu'elle cause précisément l'exception WinUAE observée reste à démontrer par une séquence isolée ou un dump invités/trace API. Il serait incorrect d'attribuer directement le crash au décodeur ByteRun1, dont les tests statiques passent sur Clown et Fallout. Ne pas corriger le loader par spéculation.

## WinUAE : contrôle écran seul confirmé (10 novembre 2026)

Retour utilisateur avec image Fallout (640 × 512, 4 plans, ModeID 167936, 16 couleurs) : **trois exécutions sans crash** de `M5_ILBM_INPUT_EXIT_DIAG.asc` (version sans Double Buffer, Swap, chargement ILBM ni dessin direct). `Aga Screen Open=1`, `Aga Wait Key` retourne 64, `Aga Screen Close` puis `Amos To Front` et `End` normaux. **Validation runtime PASS pour le chemin simple seulement.**

Cette observation ne valide PAS `Aga Double Buffer`, `Aga Iff Load`, `Aga Swap` ni le cleanup d'une permutation en vol. Le crash original reste attribué à un état non isolé. Prochain test minimal : `tests/current/M5_DB_NO_SWAP_EXIT_DIAG.asc` = Open → Double Buffer → Wait Key → Close → Amos To Front, **sans Swap, IFF Load, Pattern**. Un seul essai sur session propre avant de poursuivre ; pas de test Swap/Close sur R6.

## Correctif isolé R7 : un défaut d'allocation supplémentaire

Le test Fallout **sans** Double Buffer est confirmé trois fois.
Le test **avec** Double Buffer mais sans Swap se bloque avant que
`OPEN =` soit visible. Le diagnostic ne localise pas à lui seul
la commande responsable.

L'inspection du générateur historique `build_m4b_r6b_r1.py` et
du binaire R6 a révélé un défaut indépendant, antérieur au Swap :
deux opcodes `2068 4A80` traitent `$4A80` comme déplacement pour
`MOVEA.L`, au lieu de charger `sb_DBufInfo` à +4 et exécuter un
`TST.L D0`. Des pointeurs invalides peuvent recevoir les écritures
des ports Safe/Disp.

**R7 0.5.8** corrige ces deux accès seulement dans le segment AP20 10,
branche `codex/intuition-input-r1`. [Preuve et validation](DB_POINTER_R7.md).

**Cette correction ne résout PAS** la libération des messages
en vol après `Aga Swap` qui reste un chantier séparé.



## Validation runtime R7 — 10 novembre 2026 (5/5 PASS)

**Retour utilisateur confirmé sous WinUAE : cinq exécutions consécutives sans crash** du test `tests/current/M5_DB_POINTER_R7.asc`, à la géométrie Fallout 640×512×4 plans (ModeID 167936).

`OPEN RETURNED 1` ; `DB RETURNED 1` ; `Aga Wait Key = 64` ; `Aga Screen Close` terminé ; retour AMOS et `End` normaux.

**PASS limité au chemin Open → Double Buffer → Wait Key → Close, sans Swap, sans IFF Load.** Le chemin `ChangeScreenBuffer` puis fermeture reste non validé et potentiellement dangereux. Suite : [contrat Safe/Disp](M5_DB_SWAP_SYNC_DESIGN.md). Ne pas merger sur main.
