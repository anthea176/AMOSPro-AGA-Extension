# R80 — Aga Iff To Chunky (proposition technique intégrée, Gate A en cours)

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
