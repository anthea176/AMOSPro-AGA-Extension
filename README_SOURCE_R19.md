# AMOSPro AGA - vrai source assembleur 68000 (R19 et releases futures)

## Objectif

Ce paquet **remplace les exports inutiles en DC.W** des outils V1/V2 par du
code assembleur Motorola lisible : `MOVE`, `MOVEA`, `MOVEM`, `JSR`, `BRA`,
`BTST`, etc., avec **labels des routines**, **table de tokens AP20**, données
et structures HUNK reconstituees.

Le code est reconstruit a partir de la **.Lib courante** et non a partir des
sources `.s` historiques M1/M3/M4, qui ne correspondent plus aux builds R19.

## Livrables

- `src/generated/AMOSPro_AGA_R19_NATIVE.s` : source **monolithique** du
  HUNK/AP20 R19 (30 entrees, noms des commandes, code 68000 et donnees).
- `src/AGA_MOUSE_R19_NATIVE.s` : source **manuel, propre et commente** des
  deux nouvelles fonctions X/Y ; les 108 octets de code **de chaque routine**
  ont ete reproduits exactement depuis les instructions de ce fichier, puis
  compares au binaire R19 valide.
- `tools/generate_aga_native_source.py` : export automatique, sans executer
  de builder ni toucher aux bibliotheques.
- `tools/decoder68k.py` : desassembleur 68000 conservateur sans dependance.
- `EXPORT_REAL_SOURCE.bat` : lanceur Windows.
- `src/generated/AMOSPro_AGA_R19_NATIVE.json` : rapport de couverture,
  empreinte SHA256 et controles.
- `tests/test_native_source.py` et `tests/fixtures/R19_MOUSE_*.bin` : tests
  de non-regression. Les fixtures contiennent **seulement 216 octets**.

## Installation Windows

Dezipper **a la racine** de `AMOSPro-AGA-Extension`, en conservant les
sous-dossiers (`tools/`, `src/`, `tests/`).

Double-cliquer sur **`EXPORT_REAL_SOURCE.bat`**. Aucun module Python externe
n'est necessaire (Python 3.10 ou plus recent). Le dossier contenant des espaces
ou des crochets (par ex. `F:\[Github] AMOSPro-AGA-Extension`) est pris en charge.

Equivalent en ligne de commande :

```bat
py -3 tools\generate_aga_native_source.py --lib dist\AMOSPro_AGA.Lib --out src\generated --baseline auto --strict
```

## Pour R20, R21, etc.

**Oui, l'export automatique est prevu pour les releases futures** utilisant
le meme conteneur HUNK/AP20 :

1. Le projet produit la nouvelle `.Lib` via son builder **habituel**.
2. Lancer `EXPORT_REAL_SOURCE.bat`.
3. L'export detecte automatiquement la nouvelle version depuis le titre
   interne (`R20`, `R21`, ...) et reconstruit toutes les entrees AP20.
4. Si le builder et son archive correspondent a la `.Lib` active, le script
   trouve le `BASE` du builder **par inspection de son AST** (sans execution),
   et liste dans le JSON les entrees modifiees/ajoutees.
5. Les routines historiques inchangées conservent la reconnaissance de leurs
   points d'entree internes grace aux empreintes SHA256 des segments.
6. Si une future release introduit un opcode/format non gere ou une region
   executable qui ne peut pas etre classifiee, `--strict` **arrete l'export**
   en indiquant les offsets. Il ne transforme pas silencieusement du code
   inconnu en une fausse routine source.

L'exporteur n'a pas besoin d'une mise a jour du nom de version. **En revanche,
une nouvelle instruction 68020 non prise en charge exigera d'etendre le
petit desassembleur** (ou de fournir un source manuel pour cette routine).

## Tests

```bat
py -3 -m unittest discover -s tests -p test_native_source.py -v
```

Le source specifique R19 X/Y est **verifie au niveau encodage d'instructions** :
le test parse ses mnemoniques et parametres, encode ces instructions avec
l'encodeur de reference et compare les octets exacts aux fixtures immuables
R19 et a la bibliotheque R19 si elle est courante.

Sur la bibliotheque R19 de SHA256
`32c99d9d83affda67058fede26731dace6511ebc033b7974330e6f9eef39e295`,
**10 770 / 10 936 octets (98,48 %) de la section AP20 code** sont identifies
comme des instructions 68000. Les 166 octets restants sont uniquement les
chaines/zonages d'etat et marqueurs AMOS `Rjsr` reconnus. Il n'y a aucune
region inclassable au controle `--strict` de la R19.

**Important : cette mesure est une couverture de desassemblage, pas une
preuve qu'un assembleur natif reconstitue le HUNK a l'identique.**

## Etape de validation assembleur (fortement recommandee)

Une fois `vasmm68k_mot.exe` installe sur le PC :

```bat
py -3 tools\generate_aga_native_source.py --lib dist\AMOSPro_AGA.Lib --out src\generated --strict --verify-vasm "C:\vasm\vasmm68k_mot.exe"
```

Ce mode demande a vasm de generer un **binaire plat HUNK** (`-Fbin`) et
compare tous les octets au fichier `.Lib` source. **Il echoue s'il ne peut
pas assembler ou si un seul octet differe.** Le resultat d'assemblage de test
est place sous `src/generated/`, jamais sous `dist/`.

**Cette verification native n'a pas pu etre executee ici** (vasm/Genam non
installes dans l'environnement). Le source complet est donc livre comme
**reconstruction de travail**, et non comme nouveau builder officiellement
valide ou comme un remplacement de la chaine Python en production.

## Securite projet

- Les builders existants et `tools/obsolete` ne sont pas modifies.
- Aucun script ne modifie `dist/AMOSPro_AGA.Lib`, `LAST_GOOD`, les archives
  ou les fichiers de test AMOS valides.
- L'export produit seulement des sources sous `src/generated/`.
- La Gate A (analyse) ne vaut pas la Gate B (WinUAE), C (AMOS Compiler) ou D
  (vrai Amiga AGA).
- Ne pas remplacer le builder Python en cours par ce source tant que la
  verification **vasm bit pour bit** n'est pas PASS.

## Workflow GitHub optionnel

`extras/native-source-export.yml` est un exemple de GitHub Actions a placer
**volontairement** dans `.github/workflows/` si tu veux un export automatique
a chaque mise a jour de `dist/AMOSPro_AGA.Lib`. Il ne cree pas de commit ni
nouvelle `.Lib` : il genere un artefact ZIP telechargeable depuis Actions.
Ce workflow **n'est pas installe automatiquement** par ce paquet.
