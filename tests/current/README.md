# Test actif — M11 R26 Safe/Disp multi-swap

**Un seul `.asc` courant :** [`M11_R26_SAFE_SWAP_02.asc`](M11_R26_SAFE_SWAP_02.asc). Il utilise **la bibliothèque R26 0.9.2 inchangée** ; **ce scénario multi-swap n'a pas encore été exécuté sous WinUAE**. Le [test R26 de premier affichage](../passed/M11_R26_AGA_TEXT_01.asc) demeure PASS et archivé à l'octet près.

Importer le programme par **Project → Merge ASCII**, sélectionner `examples/demo.iff` (PAL 320×256×8). L'écran AGA doit alterner **FRAME A - GREEN** (texte et voyant verts) et **FRAME B - RED** (texte et voyant rouges) pendant **40 swaps**, puis conserver la dernière image pendant 120 VBL pour une capture. Le programme se ferme automatiquement et revient à AMOS.

Le programme appelle `Aga Text` pour **vérifier la disponibilité du back buffer avant chaque `Aga Blit Clear/Fill`**. Si ce contrôle renvoie 0, il attend un VBL et réessaie au maximum 12 fois ; même limite pour `Aga Swap` si la notification d'affichage (`Disp`) est en attente. **Aucune boucle sans borne**, aucun appel au `Text` natif AMOS.

### Résultat console attendu

```text
M11-R26-SAFE-SWAP-02
IMAGE 320 X 256 PLANES 8
OPEN 1 DB 1 LOAD 1
DONE 40 PROBEOK 40
PROBE0 <variable> SWAP0 <variable>
SAFEERR 0 SWAPERR 0 DRAWERR 0
CLOSED -1 RESULT 1
CLOSE RETURNED
```

Les valeurs **`PROBE0` et `SWAP0` peuvent être nulles** : il ne faut ni imposer un minimum, ni interpréter chaque 0 de `Aga Text` comme la preuve que l'attente Safe était la seule cause. En cas de `RESULT 0`, signaler les compteurs exacts, le comportement visuel et toute erreur AMOS. **40 swaps ne constituent pas une mesure de 50 FPS**, ni un stress exhaustif de toutes les conditions de course. [Contrat R26](../../docs/M11_TEXT_R26.md).
