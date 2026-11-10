# Export assembleur depuis les builders Python (lecture seule)

## Installation

Placer `EXPORT_ASM.bat` a la racine du depot `AMOSPro-AGA-Extension` et
`export_aga_asm.py` dans son dossier `tools/`. Python 3.9 ou plus recent
est necessaire. **Aucune installation de module n'est requise pour obtenir
la version exacte en `dc.w` / `dc.b`.**

## Utilisation Windows

Double-cliquer sur `EXPORT_ASM.bat`. Le journal complet se trouve dans
`asm_export/export.log` : en cas d'echec, une trace Python (type d'erreur,
ligne et appels) y est conservee. Les chemins Windows comprenant des espaces
ou des crochets sont acceptes (le BAT cite les chemins fixes). Il cherche automatiquement dans `tools/`
le builder dont l'archive versionnee correspond exactement a la bibliotheque
`dist/AMOSPro_AGA.Lib`, et exporte **cette bibliotheque sans relancer `build()`**.
Le nom du builder et l'archive strictement identique sont conserves dans le
rapport JSON. Le binaire etant deja produit par Python, cet export est la
reconstruction assembleur exacte des octets contenus dans la .Lib. Si aucun
builder n'est reconnu, les octets de la bibliotheque sont exportes directement.
Pour vraiment rappeler `build()` et comparer les octets, utiliser
`--verify-builder` (option distincte, mode diagnostic).

Les fichiers apparaissent dans `asm_export/` :

- `AMOSPro_AGA_Rxx_vx.y.z.s` : **assembleur Motorola**, reconstruction exacte
  du HUNK/AP20 avec `dc.w` / `dc.b` et commentaires d'instructions.
- `AMOSPro_AGA_Rxx_vx.y.z.lst` : listing 68000 par entree AP20, noms de
  commandes lorsque connus et offsets absolus.
- `AMOSPro_AGA_Rxx_vx.y.z.json` : SHA256, tailles, tokens, entrees et verification.

### Options

```bat
REM Builder courant identifie automatiquement (double-clic):
EXPORT_ASM.bat

REM Reconstruire EN MEMOIRE avec le builder identifie et comparer la .Lib :
EXPORT_ASM.bat --builder auto --verify-builder

REM Builder specifique (produit le binaire en memoire) :
EXPORT_ASM.bat --builder tools\build_m8_mouse_position_r19.py

REM Pour verifier que le builder et la Lib active sont identiques :
EXPORT_ASM.bat --builder tools\build_m8_mouse_position_r19.py --check-dist

REM Pour exporter sans aucun appel au builder :
EXPORT_ASM.bat --builder none

REM Pour choisir la version archivee :
EXPORT_ASM.bat --builder none --lib dist\experimental\AMOSPro_AGA_M7_v0.8.2_COPPER_RASTER_R18.Lib

REM Sortie dans un dossier personnalise :
EXPORT_ASM.bat --out C:\Temp\AGA_ASM
```

**Lecture des instructions 68000 :** installer facultativement Capstone :

```bat
py -3 -m pip install capstone
```

Sans Capstone, la source reste integrale et exacte, mais la colonne des
mnemonics du listing sera remplacee par des octets hexadecimaux. Capstone
peut prendre du code embarquant des donnees pour des instructions : ces
comments sont une **aide a la lecture**, pas une source symbolique prouvee.

### Fidelite et limites importantes

Les builders du depot injectent parfois des segments **herites d'archives
binaires**. Il n'existe donc pas de conversion mathematique du Python
vers le *source Genam original* avec labels, macros et commentaires.
Le fichier `.s` genere est **sans perte octet pour octet** (HUNK + AP20 +
fragments 68000, tokens, titre et padding) et utilisable comme source
reconstructible **en mode binaire plat**, sans oublier les donnees.

La generation ne modifie ni `dist/`, ni `LAST_GOOD`, ni les sources, ni les
scripts de test. La comparaison complete SHA256 avec le binaire source
est affichee. Ne pas remplacer un builder Python de production par un
fichier desassemble sans campagne de validation et reassemblage reel.

Si `vasmm68k_mot` est installe, exemple de verification du `.s` :

```bat
vasmm68k_mot -Fbin -o controle.Lib asm_export\AMOSPro_AGA_R19_v0.8.3.s
certutil -hashfile controle.Lib SHA256
certutil -hashfile dist\AMOSPro_AGA.Lib SHA256
```

Le nom du fichier depend de la version reelle ; consulter la sortie du BAT.
L'export est un outil de diagnostic, pas une confirmation d'assemblage natif.

## Correctif V2

La V1 appelait inutilement la fonction `build()` du candidat courant
en mode automatique. Un `assert` du builder sans texte pouvait provoquer
un simple `[ERROR]` vide. V2 utilise l'archive identique pour le flux
automatique ; `--verify-builder` reste disponible pour diagnostiquer
les builders eux-memes, avec traceback. Aucun `.Lib` n'est ecrase.
