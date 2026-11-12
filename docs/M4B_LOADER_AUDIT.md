# Audit du chargement M4a -> M4b (issue #1)

Date : 9 novembre 2026. Dépôt audité : `d9d1342`, fichiers locaux sur F:.

## Conclusion et niveau de preuve

**Défaut structurel démontré : absence d'alignement pair de chaque token.**
Les trois M4b contiennent la même table invalide. Le chargeur AMOS365 lit
`Aga Back Fill` avec les index instruction/fonction **3072/353**, au lieu de
**12/1**. Comme cette commande possède un paramètre, `Library_GetParams`
utilise ces index pour lire des pointeurs hors de la table des routines,
avant `Library_Init` et avant toute commande utilisateur.

Ce défaut explique un échec au démarrage et n'est corrigé ni par R1
(registres BackFill), ni par R2 (restauration du Cold de M4a).
La chaîne de lecture hors limites est prouvée statiquement. **Le PC exact du
Software Failure 80000004 observé sous WinUAE n'est pas établi** : aucun dump
CPU ni trace du binaire AMOS365 installé n'a été fourni. Selon le contenu de
la mémoire hors limites, le chargeur peut atteindre son `illegal` explicite
ou échouer lors de l'accès mémoire. Ce rapport ne prétend pas avoir reproduit
le Guru dans un émulateur ni exclu tout autre défaut runtime.

Une correction de table est testée **en mémoire uniquement**, à partir de
R2. Aucune nouvelle `.Lib` n'est écrite, installée ou publiée. M4a et les trois
M4b historiques restent inchangés. Les générateurs historiques restent
inchangés pour conserver les preuves et leurs empreintes.

## Références primaires

Sources AMOS365 consultées au commit
`3e8f53196b80cbb2e01342a89a3545d080bf0de4` :

- [+B.s : chargeur](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BB.s#L2177), notamment `Library_Load` 2177–2281, `Library_Reloc` 2359–2488, `Library_GetParams` 2694–2813 et `Library_Init` 2818–2845.
- [+Equ.s : macros](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BEqu.s#L2177), `Lib_Ini`, `Lib_Def`, `Lib_Par`, `Lib_End`, `Lib_Empty`, `MCInit`, `MC`.
- [+Request.s : extension officielle](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BRequest.s), dont le binaire de référence est embarqué dans `tools/build_probe.py`.
- [+CompExt.s](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BCompExt.s) : header, tokens, Cold et placement de `Lib_End`.
- [Library_Digest.Asc](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/c/Library_Digest.Asc) : comptage des labels et génération de `Lib_Size`.

Ces références décrivent la version source consultée. L'identité du binaire
AMOS365 effectivement installé avec cette révision n'a pas été vérifiée.

## Conteneur HUNK et quatre champs AP20

Les quatre valeurs sont des **tailles/différences entre sections**, pas des
offsets absolus : `C_Tk-C_Off`, `C_Lib-C_Tk`, `C_Title-C_Lib`, `C_End-C_Title`.
Le header AP20 occupe 22 octets. La table des tailles commence au fichier
`32+22`, les tokens à `32+22+off`, le code après les tokens.

| Fichier | Octets fichier | off | Tokens | Code | Titre | Entrées |
|---|---:|---:|---:|---:|---:|---:|
| M4a validé | 1612 | 22 | 150 | 1320 | 60 | 11 |
| M4b initial | 2212 | 28 | 208 | 1856 | 60 | 14 |
| M4b R1 | 2212 | 28 | 208 | 1856 | 60 | 14 |
| M4b R2 | 2136 | 28 | 208 | 1778 | 60 | 14 |
| Candidat structurel R2, mémoire seulement | 2136 | 28 | 208 | 1778 | 60 | 14 |

Les tailles HUNK déclarées correspondent aux tailles réelles. Un seul
HUNK_CODE, puis HUNK_END ; absence de relocation HUNK externe. Sections
paires, corps HUNK multiple de quatre, C_End et remplissage nuls présents.
L'alignement longword de chaque routine n'est pas requis par ce chargeur :
il construit les adresses en cumulant des tailles en mots.

Tables de tailles en mots :

```text
M4a:    94,2,8,8,48,167,193,75,52,13,0
M4b/R1:133,2,8,8,48,167,193,75,91,15,75,57,56,0
M4b R2: 94,2,8,8,48,167,193,75,91,15,75,57,56,0
```

La somme multipliée par deux égale exactement la taille du code, pour chaque
fichier. **Passer de 11 à 14 entrées est légal.** `Library_Load` calcule le
nombre à partir de `off/2`, réserve la table correspondante et parcourt ce
nombre d'entrées. Aucun nombre 7 ou 11 n'y est imposé. Le générateur M4b
emploie bien `len(jumps)*2` pour le nouveau `off` ; il suppose 11 entrées
uniquement pour lire sa base M4a explicitement figée par SHA256.

## Trace exacte des tokens

Dans `Library_Reloc`, après le nom et la signature, `.RDoke` arrondit
l'adresse suivante par `(adresse+1)&~1`. `Library_GetParams` et `Ll_TkNext`
font également ce réalignement. Chaque entrée doit donc inclure son propre
octet de remplissage si nécessaire. Aligner uniquement la table complète
ne suffit pas.

Offsets ci-dessous relatifs au début de la table des tokens :

| Entrée voulue | Début encodé M4b | Début lu AMOS | Mots lus AMOS | Conséquence |
|---|---:|---:|---|---|
| Aga Probe | 6 | 6 | 3 / 1 | Signature sans paramètre ; entrée suivante mal alignée |
| Aga Detect | 21 | 22 | 256 / 1121 | Défaut hérité ; nom lu `ga detect`, zéro paramètre |
| Aga Double Buffer | 144 | 144 | 1 / 10 | Entrée longue de 23 octets, remplissage absent |
| Aga Swap | 167 | 168 | 256 / 2913 | Nom lu `ga swap`, zéro paramètre |
| Aga Back Fill | 181 | 182 | 3072 / 353 | Nom lu `ga back fill`, signature `I0`, un paramètre |

À l'offset 182, les quatre octets sont `0c 00 01 61` :
`0c00` = 3072 et `0161` = 353. Le dernier octet est le `a` du nom !
`.RInst` considère aussi le second mot >1 comme une fonction et pose les
deux flags. L'index instruction devient le déplacement `-(3072+1)*4`.
`Library_GetParams` ajoute `-LB_Size` (36), soit une lecture à
**base_tokens-12328**. La table ne contient que 14 routines ; la dernière
adresse valide est à base_tokens-92. Le chemin fonction sélectionnerait
ensuite base_tokens-1452, s'il était atteint.

La routine `.Doke` lit ce faux pointeur, examine les quatre octets qui le
précèdent pour chercher `GetP`, et exécute `illegal` si elle ne reconnaît ni
`GetP` ni un dispatcher déjà installé. Il n'y a pas de contrôle de borne
des index de tokens sur ce chemin.

**Pourquoi M4a peut démarrer malgré son défaut hérité :** son entrée Detect
mal lue ne déclare aucun paramètre. `.Entier` quitte alors sans accéder au
pointeur erroné. Ce constat n'annule pas la validation WinUAE rapportée de
M4a, mais ne permet pas de considérer sa table entière comme conforme.
Il faut éviter de réutiliser aveuglément cette table comme référence saine.

Le défaut hérité apparaît dans `build_detect.py` (concaténation de Probe et
Detect sans remplissage individuel), puis est conservé dans les bases
suivantes. `build_m4b_doublebuffer.py` reproduit la même erreur dans `token()`.
R1 ne modifie que deux instructions machine ; R2 conserve les tokens R1.

## Lib_Par, GetP, Lib_End et terminateurs

`Lib_Par` émet `GetP` **avant** le label de la routine. `MC` encode la
différence entre deux labels successifs divisée par deux ; les quatre octets
GetP appartiennent donc à la fin du segment précédent. M4a et M4b respectent
ce placement pour leurs entrées réelles, notamment #6 (Screen Open), #10
(Double Buffer), #11 (Swap), #12 (Back Fill). Les mauvais index proviennent
des tokens, pas du placement des dispatchers.

Avec les tokens corrigés, seules #6 (quatre paramètres) et #12 (un paramètre)
nécessitent un patch GetP. Le test vérifie les octets immédiatement avant
ces adresses calculées, et non leur simple présence quelque part dans le code.

`Lib_End` définit un dernier label et incrémente le compteur d'assemblage ;
il n'émet pas une instruction de fin ni un marqueur magique. `Library_Digest`
compte les définitions/entrées vides, et `MC` produit les différences entre
labels. Les entrées de taille zéro sont traitées individuellement par le
chargeur, **elles ne terminent pas son parcours**. Son symbole `Ll_Rts`
contient en réalité une instruction `illegal` dans la source consultée.

Requester conserve deux `Lib_Empty` finaux selon sa convention documentée.
M4a utilise déjà l'une des anciennes places pour Wait Vbl ; M4b étend la
table et conserve une entrée vide finale. Cette différence mérite d'être
documentée, mais n'explique pas ce crash : le chargeur utilise le compte,
pas une recherche de deux zéros finaux. La somme des spans reste cohérente.

Le terminateur des tokens est distinct : un mot zéro suivi d'un long zéro.
Il est présent dans les fichiers audités. Les sept octets nuls finaux de
M4b résultent du remplissage global ; ils ne réparent pas les décalages entre
tokens.

## Cold, Warm et PC-relative (après vérification des tables)

Les déplacements du Cold pointent vers les bonnes positions relatives :

| Fichier | champ PC+12 -> état | PC+20 -> hook | PC+32 -> état | État |
|---|---:|---:|---:|---|
| M4a / R2 | 156 | 56 | 156 | 32 octets nuls |
| M4b / R1 | 234 | 56 | 234 | 32 octets nuls |

Le Cold R2 est identique aux 188 octets de M4a. M4b initial/R1 ont déplacé
l'état après le cleanup agrandi et ajusté les deux déplacements concernés.
Le hook reste à +56 ; les écritures a5+$1c8/$1cc/$1d0 et le numéro retourné
13 sont conservés. La branche de refus de version reste interne au Cold.

Les routines conservées sont déplacées en bloc ; leurs déplacements
PC-relative internes ne changent pas. Le petit émetteur M4b `A.br()` calcule
ses déplacements depuis le mot d'extension (`pos+2`), ce qui est la base
attendue pour ces branches 16 bits. Aucun mot aligné correspondant au
préfixe de pseudo-relocation AMOS `$FE?1` n'est présent dans les quatre
blocs code audités. Le scanner de relocation AMOS n'a donc aucune de ces
pseudo-instructions à réécrire ici.

Cela ne constitue pas un désassemblage/une exécution exhaustive de toutes
les routines graphiques. L'audit de sûreté du double buffering reste séparé.
R2 conserve notamment les hooks RESET/END de M4a, non adaptés aux ressources
M4b, comme l'indique déjà sa documentation. Le candidat structurel ne doit
pas servir à valider ce cycle de vie.

`src/AMOSPro_AGA.s` décrit encore un candidat Genam M1 ;
`src/M4_DOUBLEBUFFER_68020.s` contient des constantes/commentaires de
conception, pas l'implémentation assemblée de ces binaires. Les générateurs
Python et les `.Lib` sont donc les preuves effectives pour cet audit.

## Diff structurel M4a -> candidat R2 corrigé en mémoire

- Table : 11 -> 14 entrées, `off` 22 -> 28.
- Tokens : 150 -> 208 octets ; les dix commandes possèdent des débuts pairs.
- Correction héritée : insérer le remplissage après Probe, supprimer le
  remplissage global hérité déplacé après Detect ; les commandes suivantes
  retrouvent les mêmes offsets. M4a sur disque reste inchangé.
- Correction M4b : insérer le remplissage après Double Buffer ; Swap commence
  à 168 et Back Fill à 182 ; le terminateur commence à 202.
- Code : 1320 -> 1778 octets ; Cold conservé, Close remplacé par le cleanup
  M4b, trois routines ajoutées, GetP ajouté aux frontières nécessaires.
- Titre : 60 octets dans les deux cas. Fichier : 1612 -> 2136 octets.
- Par rapport à R2 historique : **50 octets différents, tous dans les tokens**.
  Header, spans, code, titre, taille HUNK et taille fichier sont identiques.

Empreintes SHA256 :

```text
M4a       ae4b863083e32c38e85192ac760aa143d3585c51d600449056075111da213b0e
M4b       03d48deefc90345f6d8cb9c109ba9a53b8046a6041f93fc9cb8fab91b3a95e20
M4b R1    219ae629c4286794ee58d71522c8c7b9f9b3207bd8998e03759b46d4a1abec64
M4b R2    314d024e45da8f04aea8e315e6e91463fba2c3fe1c062c9a0fa5461e62228a63
R2 mémoire 036bd744c57f6206d40c5ab8eb1088dc58fc322b6e108e619b14d4e86a3d8c4b
```

## Tests et suite de validation

Depuis la racine du dépôt :

```powershell
python -B -m unittest discover -s tools -p test_ap20_loader.py -v
python -B -m unittest discover -s tools -p 'test_m4*.py' -v
python -B tools/audit_ap20.py archive/AMOSPro_AGA_M4a_v0.0.5_WinUAE_OK.Lib dist/experimental/AMOSPro_AGA_M4b_v0.0.6_R2.Lib
```

Résultats : 13 nouveaux tests passent ; les 29 tests M4 historiques passent
aussi, montrant pourquoi leurs contrôles de hash/tailles/sous-chaînes ne
détectaient pas le défaut. L'auditeur en ligne de commande **retourne 1 sur
les fichiers historiques**, volontairement : M4a a un défaut latent et M4b
des accès de paramétrage hors limites. Les tests de régression attendent ces
rejets ; ils ne déclarent pas les anciens binaires conformes.

Les nouveaux tests vérifient aussi le binaire officiel Requester (empreinte
Git contrôlée, sept entrées). Ils couvrent le parcours pair, les bornes des index, les
dispatchers GetP, la conservation du Cold R2, les cibles PC-relative du
Cold, le conteneur HUNK, les spans, le terminateur et des corruptions
injectées. L'auditeur est limité au format simple et aux signatures de ce
dépôt : il rejette les métadonnées/signatures non prises en charge et ne
prétend pas être un validateur universel d'extensions AMOS.

Avant une validation runtime complète, il faut une trace WinUAE du crash
historique (PC et registres) pour rattacher sans ambiguïté le Guru observé
à ce chemin du chargeur. Si un binaire de test est ensuite produit, le
premier essai utilisateur doit rester **le lancement d'AMOS365 uniquement,
sans charger ni exécuter de programme AMOS**. L'interprété, le compilé et
les opérations de double buffering viennent après ce premier contrôle.
