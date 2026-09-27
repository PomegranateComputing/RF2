# RF2-UI-01 — menus artistiques (Opus → Astra)

Préparé le 27/09/2026 par Opus. Opus possède les fonctions, la navigation et le rendu du texte ; Astra livre les
ressources. La structure est déjà en place et jouable (candidate `JOUER_RF2_UI-01.cmd`) : chaque ressource livrée
remplace une ressource provisoire **sous le même nom**, sans toucher au code.

## 1. Ce qui existe (base de ton travail)

| Écran | Classe / fichier | Fonction réelle |
|---|---|---|
| Titre + menu principal | `RFMainMenu` (`src/zscript/rf/menu.zs`) | Continuer (sauvegarde la plus récente, grisé s'il n'y en a pas), Nouvelle partie, Charger, Options, Crédits, Quitter |
| Pause | même classe en jeu | Reprendre, Sauvegarder, Charger, Options, Menu principal, Quitter ; chapitre et objectif courant |
| Difficulté | `RFSkillMenu` | trois difficultés de `MAPINFO`, ligne d'explication |
| Charger / Sauvegarder | `RFLoadMenu`, `RFSaveMenu` | listes du moteur (sélection, Suppr, saisie du nom, image de la sauvegarde) |
| Options | `RFOptionMenu` | page RF + pages natives complètes (police du moteur, non remplaçable par un mod) |
| Confirmation | `RFMessageBox` (`MessageBoxClass`) | quitter, abandonner la partie, effacer, écraser : Oui / Non |
| Mort / reprise | `RFStatusBar.DrawDeath` (`hud.zs`) | « Viktor est tombé. », [Utiliser] reprendre, [Échap] menu |
| Crédits | `RFCreditsMenu` | texte LANGUAGE |

Grille de mise en page : cadre de référence 1920 × 1080, mis à l'échelle uniformément et centré (16:9, 16:10, 21:9,
4:3). Colonne de menu à gauche : x = 190, titres à y ≈ 150–270, entrées à partir de y = 470 (pas de 64), aide en
bas à y = 992. La moitié droite reste à l'image.

Palette en usage (proposition de la directive, gardée) : charbon `#0E0C0E`, papier `#E8E4DA` / `#C9C4B8`, acier
`#9A9A95` / `#6B6B68`, bordeaux `#7A1F2B` (règle, focus `#A3303E`). États : normal (papier atténué), focus (papier,
bande charbon, barre bordeaux à gauche, déplacement adouci), pressé (barre papier 6 tics), indisponible (acier 70 %,
avec sa raison), confirmation (carte charbon, filet bordeaux).

## 2. Ressources attendues (remplacements, mêmes noms)

| Ressource | Cible | Format | Provisoire actuel |
|---|---|---|---|
| Composition de titre | `src/graphics/ui/RFMENUBG.png` **et** `src/graphics/TITLEPIC.png` | 1920 × 1080 (ou 2560 × 1440), PNG RGB, sans texte ; sujet dans les 45 % droits, gauche calme et sombre ; lisible recadrée en 4:3 (centre) et en 21:9 | capture du couloir du pavillon ouest (RF01) étalonnée, `scripts/ui/title_compose.py` |
| Sons de menu | `src/sounds/ui/{cursor,choose,change,backup,clear,invalid,prompt,dismiss}.wav` | mono 48 kHz PCM16, 60–250 ms, crête −20 à −27 dBFS, sans réverbération ni musique | découpes CC0 Kenney, `scripts/ui/ui_sounds.py` |
| Police de titre (facultatif) | dossier de glyphes `src/fonts/rflogo/` ou fichier source + licence | police libre (OFL ou équivalent) ; Opus la rastérise par `scripts/mapkit/fonts.py` | Inter ExtraBold (OFL) |
| Matière discrète (facultatif) | `src/graphics/ui/RFPAPER.png` | 512 × 512 répétable, très bas contraste, pour les cartes et bandeaux | aucune (aplats) |

Interdits : texte peint dans une image, crânes/grunge, cartes arrondies de tableau de bord, noms de fichier
`RFTITLE*` (ce nom masquerait la police `RFTitle` : tous les titres du jeu disparaissaient — constaté le 27/09).

## 3. Livraison

`incoming/astra/RF2_UI_01/` dans ton worktree : `manifest.json` (cible, SHA-256, dimensions/format, source,
licence), `runtime/`, `source/`, `evidence/` (captures dans le moteur avec la candidate UI si possible). Opus importe,
reconstruit, recapture tous les écrans (1080p, 1440p, 4K) et teste la navigation.
