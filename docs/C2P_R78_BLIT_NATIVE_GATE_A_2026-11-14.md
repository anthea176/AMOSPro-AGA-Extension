# R78 C2P Blit — Gate A CPU native PASS (14/11/2026)

**Statut du jalon natif :** Gate A native PASS. **Mise à jour : Gate B WinUAE fonctionnelle PASS** sur journal utilisateur du 14/11/2026 ; Gate C Compiler et Gate D physique NON TESTÉES. R73 `LAST_GOOD` protegee ; R77 Close Gate B fonctionnelle PASS.

## Identite de la candidate

- Version **R78 v0.13.23** ; binaire `dist/AMOSPro_AGA.Lib` candidat.
- **55 772 octets**, SHA256 **`9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c`**, 68 commandes publiques / 75 entrees AP20.
- Base strictement epinglee R77 v0.13.22 SHA256 `81940e4950f8c21237fb3a9a033f3df0fee4ffaae0d959231ecb20df0d51af11`.
- 1358 octets de code natif **68000-safe** ajoutes comme entree AP20 73. Seules les modifications append-only [72 + GetP, 73 code] sont autorisees ; entrees precedentes et le bloc clavier/souris (`$2F26`) byte-identiques.
- Source `tools/c2p_r78_blit_emit.py` et constructeur deterministe `tools/build_c2p_r78_blit.py`.

## Contrat de Blit

```amos
_OK=Aga C2P Blit(SrcBank,SrcPitch,SrcX,SrcY,W,H,DstX,DstY)
```

Copie CPU opaque de pixels 8 bits indexes d'une banque DATA/WORK distincte vers la banque chunky C2P liee par `Aga C2P Open`. `SrcPitch` en octets ; 320x256 en destination, clipping aux quatre bords. Aucune conversion, Swap, Blitter, allocation persistante ni modification de palette implicites.

La routine relit **les deux adresses de banques a chaque appel** via `Bnk.GetAdr`, inspecte classe, identite, longueur reelle, adresses de debut/fin valides, absence de chevauchement physique et presence d'un contexte C2P vivant. Elle verifie le rectangle source complet avec multiplication 32 bits sans troncature (shift/add et detection d'overflow) puis seulement effectue les ecritures. Retour 1 lorsqu'au moins un pixel est copie, 0 sinon. `D3` = huitieme argument (DstY), les sept autres arguments passes par `A3` comme sur R60 ; `D2=0` au retour.

## Gate A validee

**CI GitHub : [run 43599864385](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43599864385)**, statut **SUCCESS**, avec execution du vrai corps 68k sur machine68k/Musashi et verification Capstone 68000. Resultat de la suite : **`R78 C2P BLIT NATIVE GATE A PASS 46`**.

Les 46 scenarios couvrent :
- cinq profondeurs 16/32/64/128/256 couleurs ;
- pixels reels, copie de l'index 0 opaque, hauteur/largeur et stride source ;
- clipping gauche, droite, haut, bas et quatre coins, cas 32x32, une seule ligne avec pitch grand ;
- absence de contexte, banques manquantes, mauvais en-tetes DATA, flags invalides, destination courte, meme banque et recouvrement physique ;
- largeur/hauteur/pitch invalides, coordonnees et rectangle source hors limites, multiplications qui debordent, rectangles hors ecran ;
- refus CPU68000 avant tout acces banque ;
- conservation des canaries, de l'etat de l'ecran, du double buffering, du contexte et des registres AMOS ; absence d'appel SDK/Blitter, de copie sur erreur, de changement de code natif historique ou de LEA clavier/souris.

Le SHA256 du flux binaire extrait de cette CI a ete **recaclule independamment** sur 55 772 octets et correspond exactement a `9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c`.

## Prochaine etape

**Gate B WinUAE avec le seul `tests/current/C2P_R78_BLIT_01.asc` :** copie opaque d'un sprite DATA 13 (32x32) vers DATA 12 (320x256), quatre clips, cinq rejets, verification de pixels `Peek`, conversions C2P et Swap explicites, R77 Close/reopen, cinq profondeurs, journal texte `RAM:` et `Amos To Back` avant Echap.

Retour attendu : `RESULT 1`, `PASS_DEPTH 5`, `BLIT_COPY_OK 5`, `BLIT_PIXEL_OK 5`, `BLIT_REJECT_OK 5`, `BLIT_REOPEN_OK 5`, `C2P_CLOSE_OK 5`, `EMPTY_CLOSE_OK 5`, `REOPEN_OK 5`, `ERR 0`, `NOS 0`. **Cette Gate B reste NON TESTEE.** Pas de compilation AMOS avant la fin du chantier C2P, ni de promotion sans ordre explicite.

[Contrat approuve](C2P_R78_BLIT_CONTRACT_2026-11-14.md) · [Rapport R77 Close](C2P_R77_CLOSE_WINUAE_GATE_B_2026-11-14.md) · [Regles](../EXTENSION_SOURCE_RULES.md).

## Post-scriptum — preuve WinUAE du 14/11/2026

La Gate B demandée dans le plan ci-dessus est désormais **PASS**, voir [rapport et journal intégral R78](C2P_R78_BLIT_WINUAE_GATE_B_2026-11-14.md). Résultats : cinq profondeurs validées ; tous les compteurs de Blit, pixels et rejets à 5 ; `ERR 0`, `NOS 0` et Chip/Fast delta 0. Le seul ASC R78 et le binaire n'ont pas changé. Prochaine validation : [Gate C Compiler](C2P_R78_COMPILER_GATE_C_PLAN_2026-11-14.md), **NON TESTÉE**.
