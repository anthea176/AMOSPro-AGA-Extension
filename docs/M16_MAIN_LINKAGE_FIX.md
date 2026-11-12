# M16 — correction de liaison AMOS, R53 0.12.8

12/11/2026. Travail local sur main, depuis HEAD 4111cea. Aucun commit, push,
branche nouvelle, ni promotion de LAST_GOOD.

## Cause établie dans le générateur

Les indices de R47 ont été calculés en comptant les Lib_Def/Lib_Par de
+Lib.s isolément. Mais +Lib.s:1710 inclut +ILib.s avant MainLibrary.
+ILib.s commence par Lib_Ini 0 et termine à la ligne 7743 par Lib_Pos 500.
MainLibrary est donc l'entrée 500, pas zéro.

La correction ne consiste pas à essayer un décalage arbitraire : le nouveau
résolveur rejoue les déclarations dans l'ordre d'inclusion, avec Lib_Ini,
Lib_Def, Lib_Par, Lib_Int et Lib_Pos. Il refuse les symboles ambigus.
La fixture est contrôlée par SHA256 et a été comparée aux fichiers officiels
de la révision figée 3e8f53196b80cbb2e01342a89a3545d080bf0de4.
Elle contient leurs Git blob IDs et SHA256, ainsi que les numéros de lignes.
Elle extrait les déclarations jusqu'à FnFalse, sans copier le runtime AMOS.

| Routine voulue | Ancien indice | Entrée réellement sélectionnée selon ces sources | Indice corrigé |
|---|---:|---|---:|
| Bnk.GetAdr | 297 | InSort | 797 |
| Bnk.Eff | 300 | AdSort | 800 |
| Bnk.Reserve | 316 | InLPrint | 816 |
| Bnk.Change | 319 | PrintF | 819 |
| FnOne (contrôle seulement) | 322 | LPrintX | 822 |

Origine locale : tools/m16_capture_r47_emit.py:23 (constantes erronées),
tools/build_m16_r50_fnone_probe.py:24 (IDX_FNONE=322).
Ces outils historiques restent reproductibles et ne constituent plus le
chemin de construction de la capture courante.

## Sources de référence

Toutes les références suivantes sont figées à la même révision :

- [+Lib.s:1710](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BLib.s#L1710) : inclusion de +ILib.s.
- [+ILib.s:7743](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BILib.s#L7743) : Lib_Pos 500.
- [+Equ.s:2177–2217](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BEqu.s#L2177) : macros de comptage.
- [+CEqu.s:76](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BCEqu.s#L76) : Rjsr.
- [+B.s:2254](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BB.s#L2254) : construction de la table et Ll_Rts.
- [+B.s:2574–2599](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BB.s#L2574) : transformation Rjsr et accès à la table.
- [+APComp.s:2002](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BAPComp.s#L2002) et [2143](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BAPComp.s#L2143) : copie de routine, retrait du GetP terminal, relocation interbibliothèques.
- [+Lib.s:7888](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BLib.s#L7888), 7938, 8441, 8553, 8663 : services de banques et FnOne.

## AP20, GetP et cible réelle

Le HUNK unique contient les tailles de sections, la signature AP20, une table
de tailles de routines en WORDs, les tokens, le code et le titre.
Le chargeur double chaque taille pour construire les adresses de début.
Une routine de taille zéro reçoit l'adresse de Ll_Rts : malgré son nom,
le source de Ll_Rts contient ILLEGAL.

Rjsr émet six octets FE11 F700 index16. F7 identifie l'appel direct, 00 la
bibliothèque principale. Le chargeur remplace FE11 par 4EB9 et lit :

    *(AdTokens[0] - LB_Size - 4 - 4*index), avec LB_Size=36.

L'index est donc un numéro d'entrée global, ni un offset en octets ni un
rang local au fichier +Lib.s. Le générateur ne doit pas le multiplier par 4 :
le chargeur le fait. FE31 est distinct : Rbsr vise une entrée de la
bibliothèque courante.

Lib_Par écrit GetP AVANT son label L<n>, puis incrémente Lib_Count.
Le GetP appartient à la fin de la routine précédente. Le debug éventuel
ajoute aussi ses octets avant ce label. L'appel direct à FnOne vise donc
7601 7400 4E75, sans saut de préambule à inventer. Le collecteur de
paramètres et l'appel interne Rjsr ont des contrats distincts.

LPrintX (322) est défini parmi les entrées consécutives PrintE..UsingS de
+ILib.s:5339–5350 : sa taille source est zéro. Le modèle de chargeur reproduit
un JSR correct vers Ll_Rts/ILLEGAL. Le fichier généré +Internal_Jumps.s n'est
pas présent dans le dépôt officiel consulté ; Library_Patch peut remplacer
des entrées internes. Nous n'avons ni dump mémoire ni PC de l'AMOS installé :
la destination effective observée sous WinUAE n'est donc pas mesurée ici.
La sélection de 322 au lieu de 822 est, elle, démontrée par les sources.

## Rapport avec les résultats utilisateur

- R48 RESULT 1 : token, six arguments et retour de l'extension fonctionnent.
- R47/R49 : l'appel supposé Bnk.GetAdr sélectionne InSort. Ce dernier appelle
  GTablo pour un tableau, ce qui rend l'erreur Non dimensioned array cohérente.
  Cela n'explique pas à lui seul le crash du processus Windows WinUAE :
  son minidump et le PC Amiga n'ont pas été analysés.
- R50 : l'indice 322 ne désigne pas FnOne. L'entrée vide et ILLEGAL du modèle
  expliquent le Guru 80000004 de manière cohérente, sans inventer un PC mesuré.
- R51 RESULT 1 : compatible avec un chargeur correct appliqué à un mauvais indice.
- R52 RESULT 2, communiqué dans la demande du 12/11 : les mots cibles diffèrent.
  Pris seul, ce résultat ne prouve pas une mauvaise adresse. L'audit de l'ordre
  d'inclusion apporte la preuve indépendante de l'erreur d'indexation.

## ABI et pont Compiler

Le dispatcher C1 de 32 octets reste inchangé. L'entrée publique 56 appelle
par Rbsr le monolithe 57 et transmet l'offset natif inline. Le dispatcher
préserve D0/A0, ajuste l'adresse de retour et la pile CPU, puis entre dans
la routine native. Les tests exécutent ce vrai code, avec un stub et un
monolithe placés séparément dans le scénario de copie Compiler simulée.

A5 reste la base AMOS : le wrapper ne la réaffecte pas. A3 consomme les cinq
arguments empilés (H,W,Y,X,Bank), soit +20 octets ; D3 fournit l'index de
transparence. A2 pointe le frame local et est préservé par les services
de banques examinés. A6 est rechargé avec Exec avant chaque LVO Exec.
Bnk.GetAdr utilise A5 et rend A0/A1, modifie D1, et seulement D0.w en cas
de succès. Le wrapper contrôle A0, pas une valeur D0 inventée.
Bnk.Reserve reçoit D0=numéro, D1=flags, D2=taille, A0=nom ; préserve
A2/D2-D5 et renvoie D0/A0. Bnk.Eff sauvegarde D0-D2/A0-A2 ; Bnk.Change
sauvegarde D0-D7/A0-A3 autour de ses notifications.
En sortie : D3=0/1, D2=0, A3 avancé, autres registres restaurés et A7 équilibré.

Les flags de banque restent 1 (DATA, bit Chip non imposé). Cela autorise
l'allocation publique AMOS sans prouver le placement physique Fast RAM.
La véritable allocation et les notifications des autres extensions restent
à valider sous AMOS. Les tests de services sont des mocks contractuels.

## Correctif source et delta

- tools/amos_main_abi.py : résolution des noms depuis les déclarations figées.
- tools/m16_capture_emit.py : même capture native, indices tirés du résolveur.
- tools/build_m16_capture.py : dérive de LAST_GOOD C1, ajoute le token existant
  de capture à six paramètres, puis termine par wrap_native_ap20.
- tools/build_aga_current.py : vérifie aussi la reproductibilité de la candidate active.
- Les cinq mots d'index sont le seul delta du code natif par rapport à R47.
  Les tests le vérifient octet par octet. Aucun patch d'un binaire expérimental.
- Les 56 parties natives R46 sont conservées, sauf le GetP terminal requis
  pour la nouvelle entrée. Aucun changement aux signatures Draw ou Font Bank Select.
- Les outils R47–R52 restent historiques ; leur rangement global a été refusé
  par l'auto-review et n'a pas été réalisé. Aucun outil courant ne les importe.

## Tests locaux effectivement exécutés

Python 3.12.10, Unicorn 2.1.4, Capstone 5.0.9, Windows. Gate A locale :

| Contrôle | Résultat |
|---|---|
| Indexation source, FnOne CPU, ancien 322 vers ILLEGAL, GetP avant label | PASS |
| Capture via entrée publique, disposition interprétée simulée | 31 scénarios PASS |
| Capture via entrée publique, disposition Compiler séparée simulée | 31 scénarios PASS |
| Compresseur 68000 | 325 cas PASS |
| Dessin R46, flags 0/1/3, pixels et rejets | 258 scénarios PASS |
| Modèle de capture | 130 cas PASS |
| Format AGAPIC | 432 roundtrips, 1344 rendus, 2 masque/index zéro, 31 rejets PASS |
| Désassemblage capture | 525 instructions, 5 marqueurs, frontières valides PASS |
| Pont C1, AP20, GetP, plafond 32 Kio, double wrapping | PASS |
| Reproductibilité, empreintes/HUNK, LAST_GOOD | PASS |

Le test R46 contenait un NameError préexistant (Path non importé) :
ajout de l'import puis exécution réussie, sans changer ses assertions.
Le nouveau banc de capture lie les services par leurs noms issus d'une
table indépendante, à des adresses permutées. Il refuse l'ancienne R47
sur InSort. Il couvre aussi l'absence d'écran, les overflow, collision avant
allocation et tardive, mémoire indisponible, Safe absent et nettoyage de
la seule banque créée après un résultat de réservation invalide.

Ce n'est pas l'exécution du vrai chargeur ni du Compiler AMOS. La copie
Compiler est modélisée ; les services banques/Exec sont simulés.
Aucune CI distante n'a été lancée. Aucun PASS WinUAE B/C/D n'est revendiqué.

## Candidate et recette réelle

- dist/AMOSPro_AGA.Lib = dist/experimental/AMOSPro_AGA_M16_v0.12.8_IMAGE_CAPTURE_LINK_FIX_R53.Lib
- 32 008 octets ; 51 commandes ; 58 entrées AP20.
- Monolithe 29 890 octets, inférieur à 32 768.
- SHA256 : 4cc7d78998720748e70a1498ec28375b03a4f5b98e02b3510d253f797af7ae26.
- LAST_GOOD R46 C1 inchangée :
  d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b.
- Seul programme actif : tests/current/M16_R53_IMAGE_CAPTURE_01.asc.
  R52 est archivé à l'identique dans tests/diagnostics/.

Installer la candidate sous son nom exact dans APSystem et le même slot ;
vérifier taille/SHA puis redémarrer complètement AMOS. Importer le programme
par Project → Merge ASCII dans un éditeur vide. Banques 11 et 12 libres,
écran AGA de l'extension fermé au départ.

Attendus : CAP 11 12 = 1 1, NOSCREEN 0, FLAGS 0 1, COLL 0, PRES 1,
INVALID tous à 0, DRAW O/M/RELOAD = 1 1 1, RL 1, RESULT 1 et CLOSE RETURNED.
Vérifier visuellement opaque/masqué, absence de corruption des sources,
Save/Erase/Load ABK et retour éditeur. Le contrôle de collision compare aussi
la somme de tous les octets de la banque. Le relevé Chip final est fait après
effacement des deux banques créées ; il n'est pas une preuve exhaustive de fuite.

Après PASS interprété, compiler un NOUVEL exécutable du même programme et
le tester séparément. Ne pas réutiliser un ancien exécutable qui embarque
l'ancienne bibliothèque. Consigner B et C séparément. Ne promouvoir
LAST_GOOD qu'après validation réelle et décision de l'utilisateur.
