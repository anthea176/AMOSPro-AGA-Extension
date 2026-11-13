# M18 — Cache dynamique Fast Icon FICON8 → FICHIP8 en Chip RAM

**Statut : CONTRAT DE CONCEPTION (étape suivante de M18), pas de commande implémentée.** Accord de principe de l'auteur le 13/11/2026 (« oui ok ») pour poursuivre après R65 A/B PASS. Les **signatures détaillées restent proposées**, pas encore des commandes livrées. Aucun ASC de test R66, aucun nouveau binaire et aucune Gate A/B déclarée pour cette étape.

## Problème à résoudre

`Aga F Icon` (CPU) peut lire la banque source `FICON8  ` en Fast RAM, mais `Aga F Blit` (Blitter) exige une banque **distincte**, `FICHIP8 `, **physiquement en Chip RAM**, avec masque de visibilité, plans réordonnés et un marqueur `ready` par slot. Aujourd'hui la banque cache est préparée sur PC, puis chargée et déplacée en Chip via AMCAF. **Déplacer FICON8 en Chip ne convertit PAS son format en FICHIP8.**

## Deux commandes proposées, étapes séparées

```amos
_OK=Aga F Chip Bank Create(11,32)
_OK=Aga F Chip Stage(10,11,3)
```

1. **`Aga F Chip Bank Create(CacheBank,Count)`** : créer une banque DATA `FICHIP8 ` AMOS, **en Chip RAM réelle** (allocation Chip demandée à AMOS, puis contrôlée par `TypeOfMem & MEMF_CHIP`). Refuser une banque occupée, toute allocation non-Chip ou trop petite, sans laisser de fuite ni toucher aux banques existantes. Initialiser l'entête de 12 octets avec `Count`, 16×16×8 et taille `12+289×Count`, initialiser les 288 octets par slot et **tous les `ready` à 0**. `Erase CacheBank` assure la libération via AMOS. Seuils proposés : numéro 5…65535, Count 4…4096 ; aucune garantie qu'un grand cache tiendra dans la Chip RAM.
2. **`Aga F Chip Stage(SourceBank,CacheBank,IconID)`** : lire un slot `FICON8` existant dans la source (Fast ou Chip), vérifier son format canonique et convertir **sur le CPU** les 288 octets dans le slot de même index du cache `FICHIP8`. La source et le cache doivent être **deux banques distinctes** avec `IconID` valide dans chacune. Ne pas déplacer `SourceBank`, ne pas allouer de RAM à chaque appel. Si le slot cache est déjà valide, permettre un **re-staging** explicite après `Aga F Icon Bank Put` ou une future `Aga F Icon Capture`.

## Format cache existant — inchangé

- Entête `12` octets `size.l,count.w,16.w,16.w,8.w`.
- `Count` slots de **288 octets**, puis **Count octets** de marqueurs `ready` à la fin.
- Slot `FICHIP8` = **32 octets masque visible** (inverse du masque `FICON8`) + **8 × 32 octets** de bitplanes contigus.
- Les lignes de la source sont **18 octets** chacune : masque préservation puis 8 mots plans.
- Sur `Stage`, `ready[IconID]=0` **avant le premier octet du slot**, copier/réordonner et vérifier les zones mémoire, puis seulement **`ready[IconID]=1`** après écriture complète.
- `Aga F Blit` existant refuse un slot avec `ready=0` ; il peut dessiner celui avec `ready=1` et valide son masque. Aucun cache LRU, aucune éviction automatique ou mise à jour implicite dans `Aga F Icon Bank Put`.

## Contrat de sécurité

- Validation stricte des deux banques AMOS, du nom, des flags DATA tolérés `0/1/3` uniquement si le type réel est compatible, des tailles exactes, de la capacité `Count`, des entêtes et des bornes de 32 bits.
- **Exiger la Chip réelle** pour toute donnée remise au Blitter (test `TypeOfMem` sur la plage pertinente), jamais seulement le nom `FICHIP8`, un drapeau ABK ou un `Bank To Chip` présumé.
- **Refuser les erreurs avant toute écriture** lorsque possible ; en cas d'incident détecté après le premier octet, **maintenir `ready=0`** pour empêcher le DMA d'utiliser une icône incomplète.
- Ne pas créer de dépendance obligatoire à une banque de test extérieure ou à un fichier ABK préfabriqué. Aucune modification des écrans privés, palettes, curseur, back buffer, `Swap` ni `Wait Vbl`.
- Aucune promesse de cohérence automatique après modification de la source : **l'appelant doit appeler `Stage` à nouveau**. Un cache peut survivre aux `Aga Swap` mais doit être libéré par `Erase` une fois le dernier Blit achevé.

## Validation requise

1. **Gate A CPU / AP20** : création 4/32/256 slots et limites, refus d'allocation non Chip, doublons, conversion exacte sur 8 plans, marqueurs `0→1` et rejets atomiques, 68000 effectif sur layouts interpréteur et Compiler V2 simulé ; format/ABI et intégrité des banques environnantes.
2. **Gate B WinUAE interprétée** : **un seul ASC actif après passage du jalon R65**, créer source et cache depuis AMOS, remplir une icône avec `Aga F Icon Bank Put`, `Stage`, dessiner `Aga F Icon` CPU versus `Aga F Blit` Chip, vérifier fond transparent, opaque, clipping, re-staging après changement et récupération de la Chip RAM après `Erase` ; vérifier les octets de validité en AMOS.
3. Mesurer séparément **`T_create`**, **`T_stage`**, **`T_cpu`**, **`T_blit`** et un seuil d'amortissement pour N utilisations, idéalement 68020/68030 sans JIT.
4. **Gate C Compiler** une seule fois **à la fin de M18** ; Gate D matériel séparée.

**Aucun binaire `R66` ni nouvelle commande AP20 tant que le choix de l'API et des contraintes est confirmé**. R65 reste candidate non promue et R63 `LAST_GOOD` protégée.

Références : [cache M18 validé](M18_FAST_ICON_CACHE.md) · [modèle de cache et staging hôte](../tools/m18_ficon_chip_cache.py) · [noyau staging 68000 historique P2](../tools/m18_ficon16_native_stage_emit.py) · [commande Blitter actuelle](../tools/m18_ficon_chip_ap20_emit.py) · [règles](../EXTENSION_SOURCE_RULES.md).
