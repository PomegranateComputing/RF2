# Passe sur les portes du 02/10 : éléments inspectés en jeu

Vues prises dans le moteur à hauteur du joueur (caméra posée sur le sol de la pièce d'où la face est vue), sur le
build de développement du commit `8a4b463` (mêmes sources que le build de revue). Une vue n'est gardée que si
l'image montre bien le tic de sa prise (bande de tic en haut à gauche) ; les vues non obtenues sont listées.

| Carte | Faces de porte au relevé | Vues de face | Vues de biais | Vues porte ouverte | Portes vues en mouvement (4 états) | Fins de façade vues (avant défaut) | Vues non obtenues |
|---|---|---|---|---|---|---|---|
| RF01 | 52 | 51 | 52 | 51 | 26 / 26 | 5 | 0 |
| RF02 | 9 | 8 | 6 | 3 | 2 / 2 | 69 | 3 |
| RF03 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF04 | 26 | 26 | 24 | 12 | 6 / 6 | 34 | 0 |
| RF05 | 16 | 15 | 14 | 2 | 1 / 1 | 35 | 1 |
| RF06 | 17 | 17 | 17 | 0 | 0 / 0 | 0 | 0 |
| RF08 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF09 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF10 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF11 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF12 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF13 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF14 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF15 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF16 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF17 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF18 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF19 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF20 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF21 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF22 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| RF23 | 7 | 7 | 7 | 6 | 3 / 3 | 0 | 0 |
| **Total** | 239 | 236 | 232 | 170 | 86 / 86 | 143 | 4 |

RF07 n'a ni porte ni image de porte (ses ouvertures sont des baies sans vantail).

## Vues non obtenues

- RF02 : `s46_l157_m_RDFB80DC_16x168_face`
- RF02 : `s46_l157_m_RDFB80DC_16x168_biais`
- RF02 : `f0_l0_m_RF2_FAC1_704x448_face`
- RF05 : `s57_l226b_b_RF4_PORT_1280x256_face`

## Portes vues en mouvement

Chaque porte est levée par le moteur (`Door_Raise` sur son étiquette, vitesse 16) et photographiée fermée, en course,
ouverte, en fermeture ; l'ouverture du vantail (plafond moins sol du secteur de la porte) est lue dans le moteur à
chaque image.

| Carte | Porte (secteur, étiquette, image, face) | Ouverture aux quatre images (u) |
|---|---|---|
| RF01 | `porte_s19_tag51_RFSLIMEA_64x128` | 0, 46, 92, 46 |
| RF01 | `porte_s192_tag43_RFPTILEA_64x96` | 0, 46, 92, 46 |
| RF01 | `porte_s15_tag21_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s29_tag31_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s32_tag24_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s47_tag23_RDDC12FF_48x104` | 0, 50, 100, 50 |
| RF01 | `porte_s51_tag25_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s52_tag49_RFDDBLA_128x128` | 0, 62, 124, 62 |
| RF01 | `porte_s61_tag35_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s63_tag48_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s73_tag46_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s76_tag26_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s85_tag32_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s87_tag22_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s102_tag20_RD8C77A1_64x128` | 0, 62, 124, 62 |
| RF01 | `porte_s103_tag30_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s113_tag50_RD94CC3A_96x160` | 0, 78, 156, 78 |
| RF01 | `porte_s116_tag10_RDD0EC2F_96x128` | 0, 62, 124, 62 |
| RF01 | `porte_s120_tag45_RD3E5137_64x160` | 0, 78, 156, 78 |
| RF01 | `porte_s126_tag36_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s131_tag38_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s138_tag40_RD1405A1_96x112` | 0, 54, 108, 54 |
| RF01 | `porte_s151_tag41_RD4BA84C_64x112` | 0, 54, 108, 54 |
| RF01 | `porte_s164_tag44_RD008D49_64x104` | 0, 50, 100, 50 |
| RF01 | `porte_s188_tag47_RD008D49_64x104` | 0, 50, 100, 50 |
| RF01 | `porte_s190_tag42_RD008D49_64x104` | 0, 50, 100, 50 |
| RF02 | `porte_s8_tag70_RD1DDE15_160x168` | 0, 82, 164, 82 |
| RF02 | `porte_s84_tag60_RD245ADD_48x104` | 0, 50, 100, 50 |
| RF03 | `porte_s12_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF03 | `porte_s65_tag201_RFBRICK_64x384` | 0, 94, 188, 94 |
| RF03 | `porte_s66_tag200_RFBRICK_64x384` | 0, 94, 188, 94 |
| RF04 | `porte_s189_tag43_RFW_PANL_48x168` | 0, 46, 92, 46 |
| RF04 | `porte_s303_tag42_RF4_CABL_32x104` | 0, 50, 100, 50 |
| RF04 | `porte_s305_tag41_RF4_CABL_48x104` | 0, 50, 100, 50 |
| RF04 | `porte_s142_tag44_RFD_OAKS_64x128` | 0, 62, 124, 62 |
| RF04 | `porte_s203_tag46_RD35F910_48x96` | 0, 46, 92, 46 |
| RF04 | `porte_s284_tag45_RF4_PSST_64x96` | 0, 46, 92, 46 |
| RF05 | `porte_s207_tag46_RD35F910_48x96` | 0, 46, 92, 46 |
| RF08 | `porte_s4_tag200_RFPLAST_64x192` | 0, 94, 188, 94 |
| RF08 | `porte_s5_tag201_RFPLAST_64x192` | 0, 94, 188, 94 |
| RF08 | `porte_s33_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF09 | `porte_s4_tag200_RFSTONE_64x192` | 0, 94, 188, 94 |
| RF09 | `porte_s5_tag201_RFSTONE_64x192` | 0, 94, 188, 94 |
| RF09 | `porte_s43_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF10 | `porte_s9_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF10 | `porte_s63_tag200_RFTILEW_64x192` | 0, 94, 188, 94 |
| RF10 | `porte_s64_tag201_RFTILEW_64x192` | 0, 94, 188, 94 |
| RF11 | `porte_s14_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF11 | `porte_s61_tag200_RFPOM_64x192` | 0, 94, 188, 94 |
| RF11 | `porte_s62_tag201_RFPOM_64x192` | 0, 94, 188, 94 |
| RF12 | `porte_s58_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF12 | `porte_s63_tag200_RFCONC_64x384` | 0, 94, 188, 94 |
| RF12 | `porte_s64_tag201_RFCONC_64x192` | 0, 94, 188, 94 |
| RF13 | `porte_s12_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF13 | `porte_s63_tag201_RFPLAST_64x384` | 0, 94, 188, 94 |
| RF13 | `porte_s64_tag200_RFPLAST_64x384` | 0, 94, 188, 94 |
| RF14 | `porte_s4_tag200_RFCORR_64x192` | 0, 94, 188, 94 |
| RF14 | `porte_s5_tag201_RFCORR_64x192` | 0, 94, 188, 94 |
| RF14 | `porte_s34_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF15 | `porte_s4_tag200_RFFREEZ_64x192` | 0, 94, 188, 94 |
| RF15 | `porte_s5_tag201_RFFREEZ_64x192` | 0, 94, 188, 94 |
| RF15 | `porte_s62_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF16 | `porte_s39_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF16 | `porte_s58_tag201_RFPANEL_64x192` | 0, 94, 188, 94 |
| RF16 | `porte_s59_tag200_RFPANEL_64x256` | 0, 94, 188, 94 |
| RF17 | `porte_s22_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF17 | `porte_s61_tag200_RFPLAST_64x192` | 0, 94, 188, 94 |
| RF17 | `porte_s63_tag201_RFPLAST_64x192` | 0, 94, 188, 94 |
| RF18 | `porte_s4_tag200_RFCORR_64x192` | 0, 94, 188, 94 |
| RF18 | `porte_s5_tag201_RFCORR_64x192` | 0, 94, 188, 94 |
| RF18 | `porte_s33_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF19 | `porte_s33_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF19 | `porte_s65_tag200_RFFREEZ_64x192` | 0, 94, 188, 94 |
| RF19 | `porte_s68_tag201_RFFREEZ_64x384` | 0, 94, 188, 94 |
| RF20 | `porte_s14_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF20 | `porte_s68_tag200_RFMETAL_64x192` | 0, 94, 188, 94 |
| RF20 | `porte_s70_tag201_RFMETAL_64x192` | 0, 94, 188, 94 |
| RF21 | `porte_s4_tag200_RFPLAST_64x192` | 0, 94, 188, 94 |
| RF21 | `porte_s5_tag201_RFPLAST_64x192` | 0, 94, 188, 94 |
| RF21 | `porte_s51_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF22 | `porte_s64_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
| RF22 | `porte_s68_tag200_RFPOM_64x192` | 0, 94, 188, 94 |
| RF22 | `porte_s69_tag201_RFPOM_64x192` | 0, 94, 188, 94 |
| RF23 | `porte_s4_tag201_RFPLAST_64x192` | 0, 94, 188, 94 |
| RF23 | `porte_s5_tag200_RFPLAST_64x192` | 0, 94, 188, 94 |
| RF23 | `porte_s34_tag100_RD8040AF_192x192` | 0, 94, 188, 94 |
