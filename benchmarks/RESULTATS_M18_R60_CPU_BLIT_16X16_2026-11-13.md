# M18 / R60 — benchmark 16×16 CPU AGAPIC vs copie Blitter (13/11/2026)

**Source :** [programme ASC](m18_r60_cpu_vs_blit_16x16.asc) · [protocole](README_M18_CPU_BLIT_16X16.md). **Preuve : une capture WinUAE transmise par l'auteur le 13/11/2026.** La capture ne permet PAS de déterminer le mode AMOS **interprété ou Compiler** ; ne pas attribuer arbitrairement ces chiffres à un mode.

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
- Aucun contrôle bit à bit des images n'est effectué. La capture ne prouve ni l'identité SHA du binaire effectivement chargé, ni le mode interprété/compilé.

## Interprétation et limites

**Observation :** dans ce test précis, la commande CPU Aga Image Region (décodage RLE AGAPIC + dessin) termine plus rapidement les séries que Aga Blit Copy (copie 16×16 depuis le back buffer Chip prérempli). Décaler X de 1 pixel pénalise davantage la copie Blitter.

**Hypothèses NON démontrées :** le coût fixe de validation Safe, de préparation et de synchronisation Blitter pourrait dominer sur une surface de 16×16. Les opérations supplémentaires sur les mots non alignés pourraient expliquer une part de l'écart. Les résultats ne prouvent pas que le Blitter est intrinsèquement moins rapide que le CPU.

**Comparaison asymétrique :** CPU lit une banque AGAPIC compressée et décode à chaque appel ; la source Blitter est déjà en Chip RAM (staging exclu du chronomètre). Aucun des deux chemins n'est le futur moteur Fast Icon natif non compressé. Le banc teste **4 plans (16 couleurs)**, alors que le prototype Fast Icon Unity AGA cible **8 plans (256 couleurs)**. Ne pas utiliser ces rapports pour choisir un backend AUTO CPU/Blitter.

## Suite

1. Confirmer si cette capture a été faite sous AMOS interprété ou compilé, et exécuter le même ASC dans **l'autre mode** sans changer la source.
2. Pour une précision temporelle supérieure, faire un second banc avec davantage d'appels pour les deux méthodes (par exemple 12 000), afin de réduire le poids d'un tick Timer sur les durées CPU.
3. Réaliser ensuite le moteur Fast Icon natif et mesurer **CPU Fast→Chip contre Blitter Chip→Chip**, y compris le staging, les attentes et le résultat pixel par pixel en opaque/masqué. Garder M18 actif pour CBlock après les icônes.

**Dépôt :** R60 v0.13.5 LAST_GOOD non modifiée, 35 056 octets. Pas de R61, pas de nouvel ASC actif, pas de promotion. Gate D Amiga physique non testée.
