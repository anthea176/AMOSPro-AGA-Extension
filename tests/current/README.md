# M18/R66 — Gate B WinUAE interprétée à exécuter

**Unique candidate R66 v0.13.11** : [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **41 804 octets**, SHA256 `e57840e0c4f1379840e1254f1fb9ab800ce1ad712556efbd872047ea8822c7ca`, 60 commandes / 67 AP20 ; **122 tests natifs 68000 Gate A PASS** sur [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43453950765). **R63 `LAST_GOOD` protégée**. Gate B **NON encore réalisée** ; une seule Gate C Compiler manuelle **en fin M18**.

**Unique ASC actif** : [`M18_R66_FICHIP_DYNAMIC_01.asc`](M18_R66_FICHIP_DYNAMIC_01.asc). Ouvrir un programme AMOS vierge, **Project → Merge ASCII**, exécuter **en interprété sans Compiler**. Banques **11, 12 et 13 libres obligatoires** ; `Reserve As Data 13,256` écrase une banque 13 préexistante. Le test écrit `RAM:M18_R66_FICHIP8.ABK` (écrasement éventuel) : utiliser une configuration WinUAE jetable.

Le test crée une banque source `FICON8` et une banque cache `FICHIP8` **en Chip réelle**, crée une source chunky, remplit un slot et le stage. Il modifie ensuite la source puis constate que le cache reste ancien (`STALE`) avant d'appeler explicitement `Stage` à nouveau. Le masque visible ligne1 doit passer de **65535 à 49155**, le plan 0 ligne1 valoir **32771**. Marqueurs `ready` des icônes 1/2 = 1, icône 3 = 0. Les appels invalides (bank/Count/ID/alias/source/destination) doivent renvoyer 0 ; Chip/Fast Free avant/après l'effacement de toutes les banques doivent être égales. Un deuxième cycle vérifie la sauvegarde ABK à `RAM:` puis `Load` ; les deltas mémoire après fichier RAM: ne sont pas des fuites.

**Visuel AGA 256 couleurs :** cadre blanc avec diagonales rouges et vertes, sur fond bleu. **X=30 : CPU masqué** ; **X=90 : Blitter masqué**, même rendu (intérieur bleu) ; **X=150 : Blitter opaque**, intérieur noir ; **X=210 : rien** (icône 3 non prête). Attendre les deux captures (graphique + console) **`RESULT 1`, `CLOSE RETURNED`** avant de déclarer Gate B PASS.

Le programme historique R65, Gate B PASS, est [archivé à l'identique](../passed/M18_R65_FICON8_PUT_01.asc).
