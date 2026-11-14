# R80 — Aga Iff To Chunky (native Gate A PASS, WinUAE à tester)

## Objectif

Éliminer l'obligation de fabriquer un compagnon chunky `.chk` sur PC.
Ajouter une commande **native** qui décode un IFF/ILBM indexé directement
dans une banque AMOS DATA/WORK déjà réservée, indépendante de l'écran.

```amos
Reserve As Data 12,81920
_OK=Aga Iff To Chunky(_IFF$,12)
If _OK=1
   _OPEN=Aga C2P Open(12)
   _CONV=Aga C2P Convert
   _SWAP=Aga Swap
End If
```

## Signature et portée

- Fonction entière `_OK=Aga Iff To Chunky(File$,Bank)`, **2 paramètres**, retour **1** succès / **0** refus contrôlé.
- `Bank` est un numéro de banque **DATA/WORK existante**, de 5 à 65535.
  Réserve et libération appartiennent au programme AMOS ; minimum 81 920 octets.
- IFF accepté : `FORM ILBM`, dimensions **320×256**, profondeur **4..8 plans**,
  pixels indexés, `BMHD`, `CMAP`, `BODY`, compression **RAW 0** ou **ByteRun1 1**.
- HAM, EHB, dual playfield, masking non nul, fichiers malformés ou incomplets :
  **refus 0**, sans écrire dans la banque.
- Décodage **ligne par ligne et plan par plan** : bit `p` du pixel chunky
  reçoit le bit du plan `p`, MSB d'abord, 1 octet par pixel.
- Deux passes du BODY : la première valide intégralement les paquets
  et les bornes sans toucher la banque ; la deuxième remplit la banque.
  Pas de modification partielle sur fichier invalide constaté à la prévalidation.
- Ni ouverture d'écran, ni application de palette, ni `Aga Swap` implicite.
  Le code AMOS peut appliquer ensuite `Aga Palette Load(File$)`.
- Pas de nouveau fichier `.chk`, pas de dépendance SDK C2P pour charger les données.
  Le pipeline C2P R79 inchangé convertit ensuite la banque en planar AGA.
- Les autres fonctions R79, les offsets clavier/souris et la R73
  `LAST_GOOD` sont protégés.

## Validation

R80 est un **nouveau jalon**, distinct des Gates A/B/C PASS du C2P R79.
Le builder en mémoire doit préserver octet par octet les 75 entrées natives
R79 (hors séparateur GetP du précédent dernier segment), puis subir des
tests CPU du vrai code 68k et une CI source avant de remplacer
`dist/AMOSPro_AGA.Lib` par la candidate unique. Un seul ASC nouveau
dans `tests/current/` devra valider la commande en WinUAE interprété,
avec journal RAM et contrôle mémoire. La compilation réelle n'est pas
présumée. La R73 `LAST_GOOD` reste inchangée.

## Gate A native et candidate (14/11/2026)

Le builder épinglé sur R79 a généré une bibliothèque **R80 v0.13.25 de 59 708 octets**, SHA256 `24e05f7403c07d23db1ff65c9499a032b413fd7d0d140ce8a55e2fd6778b18c6`, **70 commandes / 77 entrées AP20**. L'unique nouvelle commande native occupe l'entrée 75. Les anciens corps natifs sont conservés octet pour octet hormis le marqueur de séparation `GetP` précédent. Le contrôle des sept LEA clavier/souris vers `$2F26` reste obligatoire.

**Gate A CPU 68000 PASS** : le vrai IFF de démonstration et **10 images synthétiques** (4 à 8 plans, RAW et ByteRun1) ont été décodés par le vrai code 68k, puis comparés sur **81 920 octets par image** au modèle de référence. Les refus couvrent notamment banques inexistantes, banque trop courte, mauvais flags, dimensions, profondeur, masking, compression, HAM, paquets ByteRun1 malformés, fichier absent et tronqué. Aucun octet de banque modifié lors des refus, canary intact, ABI A3 correctement consommé, ressources libérées. **CI complète SUCCESS :** [run 43611070380](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43611070380).

**Gate B WinUAE R80 NON TESTÉE** : lancer [l'ASC unique](../tests/current/C2P_R80_IFF_CHUNKY_01.asc) avec seulement l'IFF source, sans banque chunky préparée. Recueillir capture et `RAM:C2P_R80_RUNTIME.TXT`. **Gate C Compiler R80, Gate D Amiga physique NON TESTÉES ; R73 `LAST_GOOD` protégée.**
