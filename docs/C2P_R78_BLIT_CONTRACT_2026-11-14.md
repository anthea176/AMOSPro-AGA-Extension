# C2P-4 / R78 - contrat approuve : Aga C2P Blit

**Decision auteur, 14/11/2026 :** Blit accepte comme suite de R77 Close. La Gate B fonctionnelle R77 Close est confirmee ; R78 est maintenant implémentée en candidate native Gate A PASS, sans nouvelle API implicite. Aucun zoom ni nouvelle API implicite.

## Signature

~~~amos
_OK=Aga C2P Blit(SrcBank,SrcPitch,SrcX,SrcY,W,H,DstX,DstY)
~~~

Fonction entiere a huit parametres; verifier ABI et reconnaissance du token AP20. Source DATA/WORK chunky 8 bits; SrcPitch = octets par ligne (images/sprites de dimensions variables). Destination = banque 320x256 chunky liee a Aga C2P Open.

- Copie **opaque**, index de couleur 0 compris; pas de modification palette.
- Aucun Convert, Swap, redimensionnement ou acces planar implicite.
- Retour **1** si pixels copies; **0** en cas de rejet ou rectangle entierement clippe.

## Validations et bornes obligatoires

- Banque source distincte et non recouvrante en memoire avec la destination; pas de copie overlapping R78.
- Bnk.GetAdr et en-tetes DATA/WORK verifiees a chaque appel, tailles physiques confirmees : aucune adresse stale apres Reserve/Erase/Load.
- SrcPitch > 0; SrcX/SrcY >= 0; 1 <= W <= 320; 1 <= H <= 256; SrcX+W <= SrcPitch. Verification sans overflow de (SrcY+H-1)*SrcPitch + SrcX + W dans les octets de source.
- Ecran AGA et contexte C2P 320x256 actifs, banque destination >=81920 octets.
- Clipping destination a [0,320)x[0,256) sur quatre bords, avec decallage coherent de la source. Aucune ecriture partielle lors du rejet d'une banque ou de parametres.
- Copier au CPU de la chunky en Fast/Chip; pas de DMA Blitter sur la Fast. Couleur 0 est opaque.
- Gate A avec canaries et clipping exact; Gate B WinUAE avec journal RAM et mire. Gate C uniquement en fin d'ensemble C2P.

## Exemple

~~~amos
_OK=Aga C2P Open(12)
_OK=Aga C2P Blit(13,32,0,0,32,32,140,112)
_OK=Aga C2P Convert
_OK=Aga Swap
_OK=Aga C2P Close
~~~

Le zoom nearest-neighbour peut reutiliser cette base mais son contrat reste distinct, non implémente.

[Contrat R77](C2P_R77_CLOSE_CONTRACT_2026-11-14.md)

**Statut 14/11/2026 :** R77 Gates A native et B fonctionnelle PASS ; **R78 implémentée en candidate v0.13.23, Gate A CPU native PASS (46 scenarios)**, Gate B WinUAE fonctionnelle **PASS depuis le journal utilisateur**. L'ASC R77 a ete corrige pour assurer `Amos To Back` avant Echap et eviter les interruptions Ctrl+C dues au focus ; ceci ne modifie pas la library, ni la qualification de la fonction Close. [Rapport R77](C2P_R77_CLOSE_WINUAE_GATE_B_2026-11-14.md).

## Réalisation R78 et tests CPU (14/11/2026)

Nouvelle entrée native append-only, 1358 octets, `Aga C2P Blit` fonction entière 8 paramètres. **68 commandes publiques / 75 AP20** ; taille binaire **55 772 octets**, SHA256 `9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c`. Contrôles CPU M68000/M68020, source et destination DATA/WORK revalidées à chaque appel, overflow, clipping quatre bords, recouvrement physique interdit, index 0 opaque. **Gate A PASS (46 scenarios)** sur la bibliothèque reconstruite ; **Gate B WinUAE PASS** sur le journal utilisateur du 14/11/2026, puis **Gate C Compiler finale non testée**. [Rapport](C2P_R78_BLIT_NATIVE_GATE_A_2026-11-14.md).

## Validation WinUAE reçue et Gate C suivante

La [Gate B R78](C2P_R78_BLIT_WINUAE_GATE_B_2026-11-14.md) est **PASS** sur le journal utilisateur : `RESULT 1`, `PASS_DEPTH 5`, compteurs `BLIT_COPY_OK`, `BLIT_PIXEL_OK`, `BLIT_REJECT_OK`, `BLIT_REOPEN_OK` tous à **5**, `ERR 0`, `NOS 0`, **deltas Chip/Fast 0/0**. Le même binaire R78 reste candidat (55 772 octets ; SHA épinglé ci-dessus). **Gate C AMOS Compiler : non testée** ; [plan pour un seul essai compilé](C2P_R78_COMPILER_GATE_C_PLAN_2026-11-14.md). Aucun Zoom implémenté ni nouvelle API autorisée.
