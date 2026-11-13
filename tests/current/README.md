# OPT020/P1e R69 — test actif unique, Gate B WinUAE interprétée

**Programme actif unique :** [`OPT020_P1E_R69_INTERPRETED_01.asc`](OPT020_P1E_R69_INTERPRETED_01.asc). L'ancien ASC R68 est conservé à l'identique dans [`tests/passed/`](../passed/M18_R68_COMPILER_FINAL_01.asc) ; il n'est plus actif.

**Statut :** Gate A CPU Musashi PASS (321 cas P1e + régressions P1–P1d) ; **Gate B WinUAE interprétée PASS** sur deux captures utilisateur (graphique et console : `RESULT 1`, `CLOSE RETURNED`, Chip Free stable). [Rapport Gate B](../../docs/OPT020_P1E_R69_WINUAE_GATE_B_2026-11-13.md). **Gate C AMOS Compiler réelle non exécutée : conserver l'unique essai final.** Candidate R69 NON PROMUE.

## Prérequis

- WinUAE avec chipset **AGA**, CPU **68020 ou 68030**, **JIT OFF** pour les vérifications. Relever CPU/fréquence/RAM de la configuration.
- Installer exactement [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) (candidate R69) dans le slot de l'extension déjà configuré sous `APSystem`, puis **redémarrer AMOS**. La bibliothèque **R68 LAST_GOOD** reste séparée, inchangée dans [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib).
- Banque 10 libre, session WinUAE jetable : le programme charge et remplace la banque 10. Copier [`M16_AGAPIC_SAMPLE_BANK10.abk`](M16_AGAPIC_SAMPLE_BANK10.abk) dans le répertoire courant d'AMOS.
- Dans AMOS Pro : nouveau programme vide puis **Project → Merge ASCII** sur le fichier ASC actif.
- **Exécuter en interprété, ne pas lancer AMOS Compiler.**

## Vérifications Gate B

L'essai couvre les 4 sous-images, source maskée/opaque, groupes de 16 pixels, fragment non aligné, recadrage, clipping sur quatre bords, deux cas additionnels à droite/en bas, image complètement hors écran, banques/rectangles/modes invalides, commande Image Draw historique, fermeture et refus post-fermeture.

Valeurs attendues et observées sur la capture console du 13/11/2026 : `FRAMES 1 1 1 1 SHIFT 1`, `CLIP 1 1 1 1 OUT 1`, `EDGE/PART/MASK OPAQUE 1 1 1`, `BAD BANK/X/Y/W/M 0 0 0 0 0`, `LEGACY 1`, `RESULT 1`, `CLOSE RETURNED`, sans Guru, et rendu visuel correct des masques et pixels en bord. Leurs valeurs ont bien été **observées sous WinUAE** ; le contrôle visuel est cohérent, sans vérification automatique pixel par pixel.

Gate B validée sans changement du binaire. Suite : figer la candidate, puis **une seule Gate C Compiler** sur la candidate définitivement arrêtée. Mesures de vitesse séparées sous **WinUAE JIT OFF**, configuration CPU notée ; ne pas déduire un gain de Musashi ni du compteur FPS.
