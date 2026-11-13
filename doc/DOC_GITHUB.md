# Méthode d'utilisation du GitHub

A faire **SYSTEMATIQUEMENT**:

 - Avant de commencer à coder, importer la dernière version en local avec **git pull**
 - Changer de branche pour se mettre dans sa branche de dev avec **git switch**
 - Ajouter dans les commits **UNIQUEMENT** les fichiers que l'on doit modifier (s'assurer que personne d'autre ne les modifie   en même temps)
 - Faire des commits réguliers dans la branche dev **git commit**
 - A la fin, rassembler la branche dev avec la main **git merge**
 - Ne pas oublier de mettre ses modifications sur le serveur en ligne **git push origin main**


# Commandes pratiques

##  Faire un commit

> git add NOM_DU_FICHIER

Cela permet de spécifier le fichier qui va être commit

> git commit -m "MESSAGE"

Le texte MESSAGE est a remplacer par un message conpréhensible de tous pour comprendre la modification

## Uploader son code sur le server

> git push origin main

## Récuperer la version sur le serveur

> git pull 

A faire à chaque fois avant de commencer à travailler

## Changer de branche

> git switch -c NOM_BRANCHE

A utiliser systématiquement en développant 

## Fusionner une branche (dev par exemple) avec la main

> git merge dev

Il faut se placer dans la branche main avant d'executer la commande


