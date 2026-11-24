# L3 — T11A FICON/FICHIP : restaging et mémoire

24/11/2026. Bibliothèque P2d-L2b inchangée, 136708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, blob `2809b4b409eea9e234df1b96bf2b08bd393d8c85`. LAST_GOOD P2d protégée. Source [T11_CACHE_MEMORY.asc](T11_CACHE_MEMORY.asc), 6685 octets ASCII LF, SHA256 `d3e93b8e0d7c7c30a495795799cc795e54ffdfb459a3612e731b8698ca5549c9`, blob `fc87c8d2fc70a41fa48db71db2de5b6fd4970557`. Préflight local du skill AMOS PASS sur ces octets exacts ; **Gate B NON TESTÉE**.

Suite de [T14A PASS](../../../docs/evidence/T14_CLOSE_RUNTIME_PASS_L2B_2026-11-24.TXT), pour qualifier la partie FICON/FICHIP de T11. Aucun patch natif, ni changement de Lib ou ASC courant. WinUAE 68030/JIT ON/AGA PAL, projet vierge, Merge ASCII, Runtime. Banques **11, 12, 13, 27 libres**. Aucun fichier externe ni AMCAF nécessaire. Journal RAM:T11_CACHE_RUNTIME.TXT.

## Protocole

Une itération d'échauffement et six itérations mesurées. A chaque cycle, créer la banque chunky 13 (256 octets), FICON8 12 (1164 octets), cache FICHIP8 11 (1168 octets, baisse Chip Free positive, marqueurs ready initialement 0). Stage de l'icône 1, valeur uniforme 165. Open 320x256x256/DB, Fill 17 ; dessiner cinq zones et mesurer les indices planaires (capture CBlock 8x1 CPU, x aligné, y40, méthode déjà validée T06).

| Position X | Opération | Pixel attendu |
| --- | --- | --- |
| 32 | F Blit du cache préparé | 165 |
| 64 | F Blit après modification du FICON à 90, sans Stage | 165 |
| 96 | F Blit après nouveau Stage | 90 |
| 128 | F Icon CPU de la source modifiée | 90 |
| 160 | F Blit d'un slot non préparé : retour 0 | 17 |

Ce comportement avant restaging est normal selon le contrat. Stage doit publier ready=1 pour slot 1, laisser slot 2 à 0. Après les cinq contrôles valides, Swap avec reprise bornée si besoin, Close, Mouse X=-1. Vérifier les tailles des quatre banques AMOS encore présentes après Close, puis Erase uniquement les banques initialement libres ; ne pas effacer si Close ne confirme pas la fermeture. Comparer Chip/Fast aux mesures après l'échauffement, avant écriture du fichier RAM. Le delta Chip positif donne un indice de résidence du cache, et F Blit applique son contrôle natif TypeOfMem ; le banc ne mesure pas directement TypeOfMem. BANKS_PRESERVED vérifie les tailles, pas l'intégralité de chaque octet. Pas d'injection de panne d'allocation, pas de test AGPC, AGBO/Bank Free/ABA, B8, End, C2P ou Copper. Pas de benchmark. Un PASS ne clôt pas tout L3 ni tout T11.

Attendu RESULT 1, ERR 0, CYCLES 7, STAGES 14, PIXELS_OK 35, UNREADY_OK 7, BANKS_PRESERVED 7, SWAPS 7, CLOSE_RETURNED 7, CLOSED_MOUSE_X -1, CACHE_CHIP_MIN >0. OLD_PIXEL=STALE_PIXEL=165, RESTAGED_PIXEL=CPU_PIXEL=90, UNREADY_PIXEL=17. Si aucune variation après échauffement : CHIP_LOSS=FAST_LOSS=DIFF_CYCLES=0, MEM_STABLE 1, VERDICT PASS ; sinon REVIEW si fonctionnel. ERR10..16 préparation banque/stage, 20..29 écran/dessin/cache, 30..35 capture/pixel, 40 swap, 60/61 fermeture ou taille des banques. Le banc ne force pas les échecs de Reserve As Data. C reportée et D non testée.
