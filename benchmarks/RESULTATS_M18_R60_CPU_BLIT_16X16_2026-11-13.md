# M18 / R60 — benchmark 16×16 CPU AGAPIC vs copie Blitter (13/11/2026)

**Source :** [programme ASC](m18_r60_cpu_vs_blit_16x16.asc) · [protocole](README_M18_CPU_BLIT_16X16.md). **Preuve : une capture WinUAE transmise par l'auteur le 13/11/2026.** **Conditions précisées par l'auteur après la capture : AMOS interprété sous WinUAE, processeur 68030 avec JIT activé (configuration boostée).** La capture seule ne permettait pas de le savoir. La fréquence exacte, le réglage cycle-exact et la configuration RAM ne sont pas consignés. Ce relevé ne constitue **pas** une référence de performance 68020/68EC020 sans JIT.

La sortie indique PAL 320×256×16 couleurs (4 bitplanes), 3 essais par géométrie, 1 tick Timer = 20 ms, N = 1 200 appels par essai.

## Ticks bruts de la capture

| Géométrie | CPU Aga Image Region | Blitter Aga Blit Copy | Médiane CPU | Médiane Blitter | Rapport Blitter/CPU |
|---|---|---|---:|---:|---:|
| **ALIGNÉ** — source X=16, destination X=160 | **3 / 2 / 2** | **8 / 7 / 8** | **2 ticks** | **8 ticks** | **4×** |
| **SHIFT X+1** — source X=17, destination X=161 | **2 / 1 / 2** | **12 / 12 / 11** | **2 ticks** | **12 ticks** | **6×** |

Médiane CPU 2 ticks = 40 ms / 1 200 appels, soit ~0,033 ms/appel ; Blitter aligné 8 ticks = 160 ms / 1 200, soit ~0,133 ms/appel ; Blitter décalé 12 ticks = 240 ms / 1 200, soit ~0,200 ms/appel. Ces moyennes **ne sont pas des chronométrages individuels**. La quantification de 20 ms est très grossière lorsque le CPU n'utilise que 1 à 3 ticks par série : rapports indicatifs, non des facteurs précis.

## Fin d'exécution constatée

- **ERR 0** : aucune erreur relevée par le programme. Attention : le script ne vérifie que le dernier code de retour de chaque série de 1 200 appels, pas la totalité des retours.
- **CLOSE -1** : valeur relevée après Aga Screen Close par Aga Mouse X.
- **CHIP BEFORE/END 1799968 1799968** : même valeur Chip Free avant ouverture et après fermeture / effacement de la banque.
- **BENCH FINISHED - CLOSE RETURNED** : fin normale du test visible, pas de Guru à l'écran.
- Aucun contrôle bit à bit des images n'est effectué. La capture ne prouve pas l'identité SHA du binaire effectivement chargé. Le mode interprété et le profil WinUAE 68030 + JIT sont confirmés par le témoignage de l'auteur, pas déductibles de la capture elle-même.

## Interprétation et limites

**Observation :** dans ce test précis, la commande CPU Aga Image Region (décodage RLE AGAPIC + dessin) termine plus rapidement les séries que Aga Blit Copy (copie 16×16 depuis le back buffer Chip prérempli). Décaler X de 1 pixel pénalise davantage la copie Blitter.

**Hypothèses NON démontrées :** le coût fixe de validation Safe, de préparation et de synchronisation Blitter pourrait dominer sur une surface de 16×16. Les opérations supplémentaires sur les mots non alignés pourraient expliquer une part de l'écart. Les résultats ne prouvent pas que le Blitter est intrinsèquement moins rapide que le CPU. **Le JIT modifie fortement les coûts du code CPU et du pilotage du Blitter : les rapports 4×/6× ne doivent pas être transposés à un 68020 réel, ni à un 68020 WinUAE sans JIT.**

**Comparaison asymétrique :** CPU lit une banque AGAPIC compressée et décode à chaque appel ; la source Blitter est déjà en Chip RAM (staging exclu du chronomètre). Aucun des deux chemins n'est le futur moteur Fast Icon natif non compressé. Le banc teste **4 plans (16 couleurs)**, alors que le prototype Fast Icon Unity AGA cible **8 plans (256 couleurs)**. Ne pas utiliser ces rapports pour choisir un backend AUTO CPU/Blitter.

## Suite

1. **Prochain relevé prioritaire :** relancer le **même ASC inchangé** en **AMOS interprété** sous WinUAE configuré comme un **A1200 PAL 68020/68EC020 (~14 MHz), JIT désactivé et émulation CPU cycle-exact si disponible** ; relever la configuration effective (vitesse CPU, RAM, réglages d'émulation), les quatre séries et Chip Free. Garder séparé le relevé 68030 + JIT actuel.
2. **Ensuite :** compiler ce même ASC dans un **nouvel exécutable** et effectuer la mesure avec le **même profil 68020 sans JIT**. Ne pas comparer deux modes AMOS avec des réglages CPU différents.
3. Pour une précision temporelle supérieure, envisager ensuite un banc distinct avec davantage d'appels (par exemple 12 000), **sans modifier le programme de référence actuel**, afin de réduire le poids d'un tick Timer sur les durées CPU.
4. Réaliser ensuite le moteur Fast Icon natif et mesurer **CPU Fast→Chip contre Blitter Chip→Chip**, y compris le staging, les attentes et le résultat pixel par pixel en opaque/masqué. Garder M18 actif pour CBlock après les icônes.

**Dépôt :** R60 v0.13.5 LAST_GOOD non modifiée, 35 056 octets. Pas de R61, pas de nouvel ASC actif, pas de promotion. Gate D Amiga physique non testée.
