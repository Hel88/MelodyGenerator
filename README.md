# Melody Generator

Le but de ce projet est de générer des mélodies en explorant différentes méthodes d'apprentissage profond. Nous avons réalisé un VAE et un LSTM. Les données proviennent du dataset [ESAC](https://www.esac-data.org/), composé de mélodies traditionnelles de différentes régions du monde.

Ce projet a été réalisé dans le cadre du cours *8INF887 - Apprentissage profond* de l'UQAC (Université du Québec à Chicoutimi).


## Membres du groupe
* Amandine Lapique--Favre ([Am-lf](https://github.com/Am-lf))
* Héléna Barbillon ([Hel88](https://github.com/Hel88))

## Contenu des dossiers

* **Aleatoire** : Mélodies générées aléatoirement
* **AutoEncodeurs** : Contient 2 modèles de VAE (Variational Auto Encoders), la gen_2 est la plus récente (et efficace)
* **data** : les données du projet
  * *han* : chansons traditionnelles chinoises
  * *france* : chansons traditionnelles françaises
  * *deutsch* : chansons traditionnelles allemandes
* **GAN** : contient des modèles de GAN (generative adversarial network), gan2 contient les modèles les plus complets
* **LSTM** : Contient un modèle de LSTM (Long short term memory encoder), entraîné sur les datasets *han* et *deutsch*.
* **generated_melodies** : Mélodies générées par nos modèles, un résumé est disponible dans le fichier *Listen.ipynb*
* **pdf_files** : Contient les deux rapports de sprint et le diaporama de la présentation finale
