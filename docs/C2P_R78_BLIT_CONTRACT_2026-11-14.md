# C2P-4 / R78 - contrat approuve : Aga C2P Blit

**Decision auteur, 14/11/2026 :** Blit accepte comme suite de R77 Close. R78 ne sera implementee qu'apres qualification de R77 sur WinUAE. Aucun zoom ni nouvelle API implicite.

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
