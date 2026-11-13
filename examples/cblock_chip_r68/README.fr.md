# CBlock Chip Lab — R68 v0.13.13

[English](README.md) · [Tous les exemples](../README.fr.md) · [Contrat technique](../../docs/M18_CBLOCK_DESIGN.md)

Exemple **AMOS interprété, autonome et sans ressource externe** pour sauvegarder rapidement un fond AGA dans une banque temporaire **RAW planaire en Chip RAM**, avec `Aga C Block Capture`, `Draw` et `Restore`. Aucun IFF, ABK, fichier de palette ou AMCAF nécessaire.

**Source :** [CBLOCK_CHIP_LAB.asc](CBLOCK_CHIP_LAB.asc). Utiliser la [candidate R68](../../dist/AMOSPro_AGA.Lib) v0.13.13 (ou une version compatible ultérieure). **L'API elle-même a passé les Gates A native et B WinUAE interprétée** sur les tests archivés ([Gate B](../../docs/M18_R68_CBLOCK_WINUAE_GATE_B_2026-11-13.md), [PERF-02 sur 6 tailles](../../docs/M18_R68_CBLOCK_PERF_02_WINUAE_2026-11-13.md)). **Cette nouvelle démo simplifiée n'a pas encore été exécutée séparément dans WinUAE** : pas de preuve runtime ni de Gate C Compiler pour l'exemple.

## Le programmeur choisit Method — aucun automatisme

| Valeur | Chemin | Alignement horizontal |
|---:|---|---|
| `0` | CPU8, octet planaire | X et Width multiples de **8 pixels** |
| `1` | CPU16, mot planaire | X et Width multiples de **16 pixels** |
| `2` | Blitter Amiga, DMA Chip→Chip | X et Width multiples de **8 pixels** |

`Method` est **obligatoire sur chaque appel**, y compris `Restore`. L'extension **ne choisit pas automatiquement** selon le CPU ou la taille. Coordonnées non alignées, banque/dimensions invalides, dépassement d'écran : retour `0`, sans clipping. Les mesures sans JIT montrent que le plus rapide varie selon les dimensions et le processeur ; **aucun mode n'est imposé**.

## Exécution

1. Vérifier que **la banque AMOS 11 est LIBRE**. La démo crée une banque DATA `AGACBLK ` temporaire dans la vraie Chip RAM et la libère par `Erase 11` après fermeture. Ne pas utiliser la démo si la banque 11 existe déjà.
2. Installer `dist/AMOSPro_AGA.Lib` sous `APSystem/AMOSPro_AGA.Lib` dans **le même slot** d'extension ; redémarrer AMOS.
3. Dans AMOS : **New → Project → Merge ASCII** sur `CBLOCK_CHIP_LAB.asc`, puis **Run en interprété seulement**. La Gate C Compiler manuelle est réservée à la **fin de M18**.
4. Écran AGA 320×256×256 : un **carré blanc à centre noir** dans la partie haute, puis trois copies identiques sur fond bleu : **CPU8 X8**, **Blitter X96**, **CPU16 X176** (Y144). Affichage ~180 VBL PAL, puis fermeture.
5. Console attendue : `DRAW CPU8/BLIT/CPU16 1 1 1`, `RECAP/SAME 1 1`, `BANK LEN 1064`, Chip Free identique avant/après, `ERROR 0`, `RESULT 1`, `CLOSE RETURNED`. Il s'agit de **valeurs attendues, pas d'un résultat utilisateur déjà observé** pour ce nouvel exemple.

## Cycle principal

```amos
_CAPMODE=2
_OK=Aga C Block Capture(11,16,48,32,32,_CAPMODE)

' Retour au fond original, à la position de capture :
_RESTMODE=1
_OK=Aga C Block Restore(11,_RESTMODE)

' Trois destinations, même banque Chip :
_OK=Aga C Block Draw(11,8,144,0)
_OK=Aga C Block Draw(11,96,144,2)
_OK=Aga C Block Draw(11,176,144,1)

' Recapture sur place, sans nouvelle allocation :
_OK=Aga C Block Capture(11,16,48,32,32,0)
Erase 11
```

Extrait simplifié : ouvrir d'abord l'écran AGA privé, le double buffer, attendre le back buffer Safe, dessiner ; synchroniser, fermer, puis libérer la banque. Le programme ASC complet respecte cet ordre. **L'index de palette 0 reste opaque** : ce n'est pas un masque de transparence.

Source de la démo sous [licence MIT](../../LICENSE), sans illustration externe.
