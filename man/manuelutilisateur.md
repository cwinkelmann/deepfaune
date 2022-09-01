# MANUEL D’UTILISATION DU LOGICIEL DEEPFAUNE (v0.2)

---
## PRESENTATION GENERALE
---
Ce document décrit le logiciel DeepFaune qui est une **interface graphique permettant d’utiliser simplement le modèle de classification développé par notre équipe pour trier automatiquement des images de pièges photographiques.** Les étapes d’installation ainsi que la prise en main du logiciel et un exemple d’utilisation y sont abordés. Le logiciel DeepFaune peut être utilisé sur un ordinateur personnel (PC) standard avec les systèmes d’exploitation Windows ou Linux (Mac OS non testé). 

Ce logiciel fait partie d’un projet de recherche vivant et peut donc évoluer régulièrement. Les mises à jour du logiciel et de son manuel seront disponibles ici [https://www.deepfaune.cnrs.fr/].

---
## VUE D’ENSEMBLE DU LOGICIEL
---
### Fonctionnalités
Le logiciel DeepFaune offre une interface ergonomique pour faciliter le tri et la classification d’**images stockées localement**. Il suffit de sélectionner le dossier contenant les images à trier et de lancer le programme.  Le modèle de classification prédit alors, pour chaque image, **si l'image est vide ou contient un taxon** détecté avec le plus haut score de confiance (ex : une image peut être prédite comme contenant un « chamois » avec 92% de confiance). 

Les **résultats sont disponibles sous forme de tableau** (disponibles aux formats `.csv` ou `.xlsx`) associant à chaque image la classe prédite et le score de confiance. Les images classées peuvent être stockées dans des **sous-dossiers spécifiques aux taxons**, permettant d’organiser directement toutes les images d’un taxon spécifique dans un même sous-dossier. 

Un seuil de confiance minimal et un délai maximal par séquence d’images sont des paramètres à fixer pour effectuer une prédiction et sont explicitées ci-dessous.

Le **seuil de confiance** détermine le seuil minimal pour lequel une prédiction est retenue (ex. avec un seuil de 50%, toute image étant prédite avec un score inférieur à 50% se verra attribuer la mention « indéfini »). Un seuil élevé permet de classer rapidement et avec peu d’erreur les images facilement reconnues par le modèle, mais laisse à l’utilisateur.rice plus d'images à trier manuellement (classées alors comme « indéfini »). Inversement, un seuil bas laissera peu d’images « indéfini » mais la qualité de la prédiction pourra être moins bonne. La valeur la plus pertinente pour ce seuil dépend donc de nombreux facteurs tels que les objectifs de l’étude, les espèces étudiées, la capacité à inspecter visuellement les images classées comme « indéfini » etc. Ce choix est donc laissé à l’utilisateur.rice.

Certains pièges photographiques sont programmés pour prendre une suite d’images à chaque déclenchement de l’appareil (ex : piège programmé en mode « rafale », prenant trois photos consécutives quand un mouvement est détecté). On considère alors que ces images consécutives font partie de la même « séquence » et représentent un unique évènement de détection. Le **délai de temps maximal** par séquence permet alors d’identifier les images appartenant à un même évènement de piège photographique grâce à la date présente dans l'exif. Ce délai indique le temps maximal pour que des images consécutives soient traitées en une même « séquence » (ex : avec un délai de 2 secondes, toutes les images consécutives espacées de moins de 2 secondes se voient attribuées la même classification). 
ATTENTION : L’information du « site » dans lequel les images ont été prises n’existe pas. Il faut donc veiller à ce que les images de différents sites soient stockées dans des dossiers séparés. Si les images de sites différents sont contenues dans un même dossier, l’information de « séquence » sera faussée.

### Organisation de l’interface
L’interface est composée d’une fenêtre principale organisée avec plusieurs onglets :

- les commandes permettant de sélectionner le dossier d’images à classer, définir les paramètres de classification et la liste des commandes effectuées en temps réel par le programme

-  les commandes permettant de choisir les modalités de sortie pour les résultats et une fenêtre de prévisualisation des résultats sous forme de tableau.

Une seconde fenêtre permet de visualiser les images et les prédictions.

---
## INSTALLATION
---
Le logiciel `deepfaune` peut tourner sur tout ordinateur classique.

#### Pour utilisateur.rices sous Windows
**Aucun prérequis technique, aucune installation tiers préalable.**

- Télécharger l’archive `.zip` correspondant à la dernière version sur [https://pbil.univ-lyon1.fr/software/download/deepfaune/](https://pbil.univ-lyon1.fr/software/download/deepfaune/)
- Extraire les fichiers contenus dans le `.zip` téléchargé dans le dossier de votre choix.
- Cliquer sur `deepfauneGUI.exe` (attention, le lancement peut prendre plusieurs dizaines de secondes).


#### Pour utilisateur.rices sous Linux, Mac (ou Windows habitué.es à Python)
Se référer aux instructions indiquées sur [https://plmlab.math.cnrs.fr/deepfaune/software](https://plmlab.math.cnrs.fr/deepfaune/software)


---
## UTILISATION
---

#### ETAPE 1 : Lancement du logiciel
Windows : Double-cliquer sur `deepfauneGUI.exe`

Linux : Dans un terminal, lancer `python deepfauneGUI.py`

#### ETAPE 2 : Choix de la langue
La première fenêtre à apparaître permet de sélectionner la langue du logiciel ; cocher Français ou English.

#### ETAPE 3 : Chargement des paramètres
Le programme charge les paramètres du modèle de classification associé. Cette étape peut prendre quelques secondes.

#### ETAPE 4 : Sélection le dossier contenant les images à trier
Sélectionner le dossier à trier en cliquant sur le bouton « Choisir » en haut à gauche dans la section Dossier d’images. Les images à trier doivent être contenues dans un même dossier parent. 

#### ETAPE 5 : Définition du seuil de confiance
Le seuil de confiance détermine le seuil minimal pour lequel une prédiction est retenue (ex. avec un seuil de 50%, toute image étant prédite avec un score inférieur à 50% sera attribué à la classe « indéfini »).
Sélectionner le seuil de confiance choisi dans la section « Seuil de confiance » en faisant augmenter/diminuer le chiffre avec les flèches haut/bas situées à droite. 

#### ETAPE 6 : Définition du délai de temps maximal par séquence
Le délai de temps maximal par séquence indique le temps maximal (en secondes) pour que des images consécutives soient traitées en une même « séquence » (ex : avec un délai de 2 secondes, toutes les images consécutives espacées de moins de 2 secondes se voient attribuées la même classification)
Sélectionner le délai de temps maximal par séquence en secondes dans la section « Délai max / séquence » en faisant augmenter/diminuer le chiffre avec les flèches haut/bas situées à droite.

#### ETAPE 7 : Lancement de la prédiction
Une fois que les valeurs des paramètres sont définies, lancer la prédiction en cliquant sur le bouton « Lancer » en bas de la fenêtre.
La barre d’état en bas à gauche se remplit en fonction de l’avancée des calculs. Elle est totalement remplie quand le programme a fini de tourner.

Une série de commandes vont s’afficher. Les lignes qui apparaissent retracent l’ensemble des commandes effectuées par le programme. Ces lignes indiquent le dossier sélectionné, le nombre d’images contenues dans ce fichier, l’état d’avancement du calcul (en batchs = groupes d’images traitées en même temps) et les étapes d’autocorrection grâce au paramètre de séquence pré-établi.

#### ETAPE 8 : Visualisation des résultats dans le tableau
Les prédictions faites apparaissent dans le deuxième onglet sous forme d’un tableau contenant le nom du fichier, la prédiction et le score de confiance associé à cette prédiction par ligne.

#### ETAPE 9 : Visualisation des résultats sous forme de diaporama
Les images classées peuvent être visualisées une à une dans une fenêtre séparée en cliquant sur le bouton « Afficher les images ». Ceci affiche toutes les images pour lesquelles des prédictions ont été faites. 
Pour visualiser une seule image, il faut impérativement sélectionner l’image dans la section tableau de l’interface en cliquant dessus (elle devient alors surlignée) puis cliquer sur le bouton « Afficher l’image sélectionnée ». 

Une fois que les prédictions sont faites, **une nouvelle fenêtre de visualisation des résultats sous forme de diaporama est disponible** en cliquant sur le bouton « Afficher les images ». Cette nouvelle fenêtre permet :

- de vérifier manuellement les prédictions faites par le modèle pour chaque image du jeu de données
- de modifier la prédiction faite par le modèle si cette dernière est jugée incorrecte.

La fenêtre de visualisation se compose d’un panneau affichant l’image sélectionnée, la prédiction associée (« Prédiction ») et des boutons permettant d’effectuer plusieurs commandes explicitées ci-dessous. 

Pour naviguer entre les images, cliquer sur les boutons « Suivant » et « Précédent ». 
Pour ne sélectionner que certaines images, choisir la catégorie « Toutes images », « Images indéfinies », « Images vides » ou « Images non vides ».

Pour sortir de la fenêtre de visualisation diaporama, cliquer sur le bouton « Close ». 

#### ETAPE 10 : Correction des résultats dans le diaporama
Pour modifier la prédiction du modèle, taper au clavier dans la section « Prediction » le nom de la classe à attribuer ou la sélectionner parmi les classes disponibles grâce au menu déroulant (cliquer sur la petite flèche à droite). 

Pour sortir de la fenêtre de visualisation diaporama, cliquer sur le bouton « Close ». 

#### ETAPE 11 : Sauvegarde des résultats dans un fichier CSV ou XSLX
Les résultats sont disponibles sous forme de tableau aux formats `.csv` et `.xlsx`.  Pour enregistrer les résultats sous forme de tableau, cliquer sur les boutons « Enregistrer en CSV » ou « Enregistrer en XSLX » selon le format choisi.

#### ETAPE 11 bis : Sauvegarde des résultats dans des sous-dossiers d'images
Les résultats sont sauvegardés dans le dossier parent (contenant les images à annoter) sous forme d’un sous-dossier nommé : « deepdaune_{DATE}_{HEURE} ». La date et l’heure contenues dans le nom de dossier sont la date et l’heure associée au lancement du programme sur un ensemble d’images. 
En sortie, les images triées sont organisées par taxon en regroupant toutes les images d’un même taxon dans un sous-dossier spécifique. **Chaque sous-dossier est identifié par le nom du taxon** et est sauvegardé le dossier de résultats « deepfaune_{DATE}_{HEURE} ». 

Remarque : Ces images peuvent être organisées selon deux modalités, selon que l'on coche « Copier les fichiers » ou « Déplacer les fichiers » AVANT de créer les sous-dossiers :

- en copiant les fichiers d’images du dossier parent dans les nouveaux sous-dossiers par taxon
- en déplaçant les fichiers d’images du dossier parent aux sous-dossiers triés. 

---
## LICENSE
---
DeepFaune est développé sous la licence CeCILL, compatible avec GNU GPL. L’utilisation d’une partie ou de la totalité du logiciel DeepFaune à des fins commerciales est strictement interdite.

---
## CONTACT
---
Pour toute question ou remarque, contacter Simon et Vincent aux adresses suivantes:

simon.chamaille@cefe.cnrs.fr / vincent.miele@univ-lyon1.fr
