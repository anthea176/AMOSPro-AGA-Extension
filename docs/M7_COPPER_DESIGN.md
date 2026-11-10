# M7 — Copper AGA : architecture et sécurité des listes utilisateur

**Statut 10/11/2026 : noyau Copper RGB4 validé sous AMOS interprété/WinUAE**, avec les scénarios R16 Clear, R17 On/Off (3/3) et R18 Wait/Move/End (bandes rouge/vert/bleu/noir visibles ; fin AMOS ligne 95). Voir [R18](M7_COPPER_R18.md). **Gates C/D, stress/fuites et palette AGA 24 bits non testés.** Archives R16/R17/M6 et LAST_GOOD R10 conservées.

## Choix d'architecture confirmé par les références AmigaOS

Utiliser exclusivement le mécanisme **`UCopList` de `graphics.library`**, lié au **`ViewPort` de l'écran Intuition créé par l'extension**. C'est le chemin système prévu pour ajouter `CWAIT` et `CMOVE` à la liste Copper du ViewPort. **Ne jamais remplacer directement `COP1LC` / `COP2LC`**, ni forcer des écritures de DMA, de bitplane pointers ou des registres non autorisés.

Contrat des commandes disponibles en R18 (fonctions entières à employer dans une expression/affectation) :

| Commande future | Rôle |
|---|---|
| `Aga Copper Clear` | Réinitialiser la liste **en préparation**, sans casser la liste actuellement visible |
| `Aga Copper Wait(v,h)` | R18 validée : attente faisceau relative au ViewPort |
| `Aga Copper Move(register,value)` | R18 validée : écriture couleur COLOR00..COLOR31, RGB4 |
| `Aga Copper End` | R18 validée : sceller la liste toujours terminée par `CEND` |
| `Aga Copper On` | Installer la liste complète dans `ViewPort.UCopIns` et appliquer via Intuition |
| `Aga Copper Off` | Désinstaller **uniquement notre liste**, restaurer l'affichage, libérer les ressources possédées |

**Périmètre graphique du premier véritable effet raster :** uniquement `COLOR00..COLOR31` (offsets matériels pairs $0180..$01BE), RGB4 sur 12 bits. Aucune écriture BPLCON3, BPLCON0, bitplane pointers ou arbitraire. La gestion des 256 entrées AGA/24 bits viendra dans un sous-jalon spécifique, après validation du Copper de base.

**Bornes conservatrices initiales :** `CWAIT` vertical 0..255, horizontal 0..222 (Autodocs), positions strictement croissantes. Taille maximale du plan préparé : 64 instructions dont la terminaison, à confirmer après intégration native. Aucune boucle d'attente sur le Copper depuis AMOS.

## Point dangereux identifié : propriété et libération des listes

**Ne pas utiliser `FreeVPortCopLists(vp)` comme un simple équivalent de `Aga Copper Off`.** L'Autodoc indique que cette fonction libère aussi les listes intermédiaires `DspIns`, `SprIns` et `ClrIns`, et les remet à NULL, pas seulement `UCopIns`. Sur un ViewPort Intuition actif, cela peut casser un affichage sans reconstruction correcte.

La première implémentation native **ne sera autorisée** qu'après avoir établi et contrôlé :

1. L'offset exact et la propriété de `Screen.ViewPort.UCopIns`, ainsi que la taille exacte de `UCopList` dans `graphics/copper.h`.
2. Le couple allocation/libération `AllocMem` / `FreeMem` et la durée de vie des `CopList` internes allouées par `UCopperListInit`/macros.
3. Un stockage de propriété **par écran**, rattaché au runtime partagé existant (pas d'état global caché ni de réutilisation arbitraire de `DBState+20`).
4. La transition `On`/`Off` sans fuite, double free ni liste Copper encore utilisée par DMA.
5. L'interaction avec `Aga Screen Close`, `Aga Screen Open` répété, les erreurs d'allocation et les `Aga Swap`.
6. La nécessité éventuelle de `MakeScreen`/`RethinkDisplay` uniquement selon le chemin Intuition officiel, sans réintroduire la reconfiguration palette/mode déjà rejetée dans M5.
7. L'absence de commande autorisant AMOS à écrire librement un registre matériel ; liste blanche initiale uniquement.

**Un test qui ne couvre pas la fermeture et le nettoyage n'autorise pas à activer le Copper.** Si la propriété ne peut pas être prouvée, laisser le binaire R15 intact et résoudre ce contrat avant R16.

## Préflight en place (sans exécution Copper)

- `tools/m7_copper_contract.py` : représentation **Python seule** d'une liste préparée, `Clear/Wait/Move/End/On/Off`, garde-fous de paramètres.
- `tools/test_m7_copper_contract.py` : neuf groupes de tests pour registres interdits, bornes des WAIT, ordre, couleurs, état final et limites d'instructions.
- Ces outils servent à définir les validations **des futurs appels 68000**. Ils **ne génèrent ni liste matérielle, ni .Lib, ni preuve d'ABI AMOS**, et ne simulent pas `graphics.library`.

## Portes de validation R16, une fois l'implémentation native sûre

- **Gate A** : builder reproductible depuis R15 archivée, HUNK/AP20, table des tokens, 68000 CPU et ABI AMOS, conservation de M5/M6, structures exactes, allocation/désallocation testées et absence d'écritures matériel arbitraires.
- **Gate B R16 : PASS** sur un test AMOS/WinUAE de cycle d'écran, archivé à l'identique dans [`tests/passed/`](../tests/passed/M7_R16_COPPER_CLEAR_01.asc). **Gate B R17 : PASS (3/3)** pour `On/Off` d'une liste vide, [test archivé](../tests/passed/M7_R17_COPPER_ON_OFF_01.asc). `tests/current/` est vide de `.asc`. **Gate B R18 : PASS** sur le [test corrigé archivé](../tests/passed/M7_R18_COPPER_RASTER_01.asc), bandes raster visibles et fin AMOS ligne 95.
- **Gate C** : AMOS Compiler réellement testé, distinct de l'interpréteur.
- **Gate D** : vrai Amiga AGA quand disponible ; tests de timing et modes avancés ensuite.

**Ne pas créer de faux PASS R16**, ne pas modifier `LAST_GOOD`, `EXTENSION_SOURCE_RULES.md`, `PROMPT_REPRISE_UNIVERSELLE.md` ni les routines validées de M6 pour contourner le problème de propriété.

## Références techniques

- [AmigaOS — Classic Graphics Primitives, User Copper Lists](https://wiki.amigaos.net/wiki/Classic_Graphics_Primitives)
- [NDK graphics/view.h — structure ViewPort / UCopIns](https://d0.se/include/graphics/view.h)
- [NDK graphics/copper.h — UCopList](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_2._guide/node00AD.html)
- [Autodoc CINIT / UCopperListInit](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node02BE.html)
- [Autodoc CWAIT](https://d0.se/autodocs/graphics.library/CWAIT)
- [Autodoc FreeVPortCopLists](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_2._guide/node0444.html)
