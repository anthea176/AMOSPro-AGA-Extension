# M7 / R16 0.8.0 — Copper Clear : validation historique

**Statut : PASS CPU/CI + PASS AMOS interprété/WinUAE pour le test R16 du 10/11/2026.** **Le candidat actif suivant est R17 On/Off ; voir [R17](M7_COPPER_R17.md).** Aucun effet raster visible n'est attendu : ce premier incrément valide **l'initialisation d'une `UCopList` et sa libération avec l'écran Intuition**. Il ne fournit pas encore `Wait`, `Move`, `End`, `On` ni `Off`.

## Livrables

| Objet | Chemin et propriété |
|---|---|
| Bibliothèque candidate | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **R16 0.8.0**, **10 036 octets** |
| Archive R16 identique | [`dist/experimental/AMOSPro_AGA_M7_v0.8.0_COPPER_CLEAR_R16.Lib`](../dist/experimental/AMOSPro_AGA_M7_v0.8.0_COPPER_CLEAR_R16.Lib) |
| SHA256 des deux | `ba55e92f1d50339b50a06c5b1903767bde549e6738dae320a0ef9ead6251bab1` |
| Base figée | `dist/experimental/AMOSPro_AGA_M6_v0.7.2_BLIT_CLEAR_R15.Lib` (SHA256 `44530d28cc33ab2aa1bb9bd81aa3f9799e3aca67a714c36891888c3ece4c6e6e`) |
| LAST_GOOD | R10 0.6.1 **inchangée** |
| Builder | [`tools/build_m7_copper_clear_r16.py`](../tools/build_m7_copper_clear_r16.py) |
| Test CPU/ABI | [`tools/test_m7_copper_clear_r16.py`](../tools/test_m7_copper_clear_r16.py) |
| **Test AMOS passé** | [`tests/passed/M7_R16_COPPER_CLEAR_01.asc`](../tests/passed/M7_R16_COPPER_CLEAR_01.asc), contenu inchangé |

## API et usage exact

```amos
_C1=Aga Copper Clear
_C2=Aga Copper Clear
```

**Résultat entier :** `1` si l'initialisation a réussi ou si la même liste est déjà présente ; `0` si aucun écran/graphics.library valide, si la mémoire manque ou si des pointeurs Copper étrangers sont présents. **Aucun paramètre**, donc A3 ne doit pas avancer, D3 contient le retour et D2=0. L'exécution répétée est prévue idempotente. Il ne s'agit **pas encore** du futur `Aga Copper Clear` qui devra réinitialiser un plan préparé après `Move/Wait`, ni d'un `Aga Copper On` visible.

## Implémentation et propriété mémoire

- La routine AP20 **22** est la seule nouvelle routine 68000. **Les 22 entrées R15 0..21 demeurent octet pour octet identiques** ; aucun correctif écran, Swap, IFF, Blitter ou clavier.
- L'état extension est lu depuis `A5+$1C8`, puis `Screen* = STATE+0` et `GfxBase = STATE+8`. **`DBState+20` est déjà occupé par le masque de notifications Safe/Disp**, ne pas y écrire.
- L'objet propriétaire est un `UCopList` de **12 octets** alloué `MEMF_PUBLIC|MEMF_CLEAR` par Exec, initialisé par `UCopperListInit(ucl,2)`, terminé par la séquence macro `CEND` : `CWait(ucl,10000,255)` puis `CBump(ucl)`.
- La liste vide, terminée, est reliée à **`Screen.ViewPort.UCopIns = Screen+64`** et le même pointeur est conservé dans **`Screen.UserData = Screen+342`**, pour contrôler l'appartenance et l'idempotence. Un pointeur étranger n'est pas remplacé.
- Aucune nouvelle fusion de Copper (`MakeScreen`/`RethinkDisplay`) n'est demandée : **aucun changement matériel ni raster** n'est recherché pour R16. L'écran privé Intuition est détruit par le chemin **`Aga Screen Close` déjà validé**, lequel appelle `CloseScreen`, détenteur de la libération de `UCopIns`. Le test effectue fermeture puis réouverture.
- En cas d'échec `UCopperListInit`, les ressources sont libérées avant retour 0 ; le programme ne modifie alors pas les pointeurs de Screen.
- Ne jamais utiliser `FreeVPortCopLists` comme un simple `Aga Copper Off` : la fonction libère aussi `DspIns`, `ClrIns` et `SprIns`.

**Limite non résolue par R16 :** le détachement d'une *liste active* et sa substitution pendant un affichage feront l'objet d'un autre candidat, avec analyse du cycle `MakeScreen/RethinkDisplay`. L'absence d'effet visible ici est volontaire.

## Validation et essai sous AMOS/WinUAE

- **Gate A : PASS** ([CI #42864040653](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42864040653), 13 scénarios 68000) : build reproductible, HUNK/AP20/SHA, préservation registres/SP/A3, aucune écriture directe au matériel, allocation/erreur, listes étrangères, `CINIT/CWAIT/CBump`, conservation des 22 anciennes entrées, régressions R13/R14/R15.
- **Gate B : PASS pour le scénario exécuté sous AMOS interprété/WinUAE le 10/11/2026.** Capture finale du test `M7-R16-COPPER-CLEAR-01` avec image déclarée `320 × 256 × 8` : `C1 1 C2 1 C3 1`, `OPEN 1 REOPEN 1`, `SWAP 1 KEY 67`, `CLOSE X2 RETURNED`, fin AMOS normale à la **ligne 74**. Aucune erreur système ni blocage apparent. Cette capture de sortie ne constitue pas une comparaison visuelle avant/après de l'image ni une mesure de fuite mémoire.
- **Gate C (Compiler) / Gate D (Amiga réel) : NON TESTÉES.**

**Suite :** le `.asc` exact est archivé dans `tests/passed/` et `tests/current/` ne contient plus de `.asc`. Le prochain développement Copper portera sur la composition et l'activation/désactivation sûres de la liste (`Wait/Move/End/On/Off`). La fermeture du programme R16 est observée, mais les listes *actives* n'ont pas été testées. Ne jamais promouvoir `LAST_GOOD` automatiquement.

## Sources techniques

- [Autodoc CINIT / UCopperListInit](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node02BE.html)
- [Macros CEND, CWAIT et CBump de gfxmacros.h](https://d0.se/include/graphics/gfxmacros.h)
- [User Copper Lists — AmigaOS](https://wiki.amigaos.net/wiki/Classic_Graphics_Primitives)
- [Autodoc CloseScreen](https://developer.amigaos3.net/autodocs/intuition.library/CloseScreen.html)
