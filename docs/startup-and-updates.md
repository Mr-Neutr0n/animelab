# Configuration initiale, thèmes et mises à jour

Au démarrage de l’interface, AnimeLab lit l’état de l’installation et vérifie
les versions disponibles si cette option est activée. Le téléchargement reste
un choix explicite. Une panne réseau n’empêche pas de poursuivre la configuration.

Le parcours reprend la structure des écrans de bienvenue Aniyomi/Anikku :

1. Nouvelle version et notes de version, avec **Télécharger** / **Pas maintenant**.
2. Apparence : système, clair ou sombre ; turquoise, violet, ambre ou AMOLED.
3. Dossier des téléchargements et guide du stockage.
4. Sur Android, permissions d’installation des extensions, de notifications et
   d’activité en arrière-plan. Elles restent facultatives.
5. Ouverture de la bibliothèque.

La fin du parcours est enregistrée dans SQLite, indépendamment du port local
de la WebView Android. Une migration ajoute une table de préférences sans
modifier les bibliothèques, les téléchargements ou les fichiers existants.
Les préférences locales du navigateur conservent la priorité pour l’apparence.

**Paramètres → Général → Application et mises à jour** permet de relancer le
parcours, vérifier une version manuellement, choisir le canal stable/bêta et
désactiver les vérifications au démarrage. Le sélecteur de thèmes reste
disponible dans les paramètres ; le bouton de la barre supérieure commute
entre clair et sombre sans changer de palette.

## Stockage selon la plateforme

- **Android** : véritable sélecteur `ACTION_OPEN_DOCUMENT_TREE`, accès
  lecture/écriture persistant et vérification du dossier. L’annulation ne valide
  pas le choix initial. **Utiliser Downloads/AnimeLab** est une autre sélection
  explicite, sans permission d’accès global aux fichiers. Les vidéos terminées
  et sous-titres sont exportés ; la base et les travaux en cours restent privés.
  Android interdit certaines racines : choisir un sous-dossier dédié.
- **Fenêtre desktop native** : sélecteur de dossier fourni par pywebview,
  exposé uniquement aux pages de l’origine locale AnimeLab. Le dossier choisi
  est ensuite validé par le moteur avant enregistrement.
- **Navigateur sur le même ordinateur** : chemin absolu du dossier du moteur,
  validé en écriture. Le navigateur ne dispose pas d’un sélecteur de dossiers
  natif capable de configurer arbitrairement un chemin côté serveur.
- **Navigateur distant / serveur partagé** : affichage du dossier du serveur,
  sans ouverture de fenêtre native ni changement arbitraire des chemins hôtes.

Changer de dossier ne déplace ni ne supprime les anciens fichiers. Les transferts
actifs doivent être mis en pause. Le choix persiste ; une nouvelle valeur de
`ANIMELAB_DOWNLOAD_DIR` définie par l’opérateur ou le launcher prend la priorité.

Les demandes Android sont déclenchées par leurs boutons. Une permission refusée
ne ferme pas l’assistant et n’empêche pas d’accéder à la bibliothèque. Les statuts
sont actualisés au retour des réglages système. La demande de notifications
automatique dans `MainActivity.onCreate` a été supprimée.

## Source des versions

Le fournisseur initial utilise les métadonnées des releases publiques de
`loeuf237/animelab`. Les notes sont affichées comme du texte : aucun HTML issu
d’une release n’est exécuté. Le canal stable exclut aussi les tags bêta lorsque
GitHub les marque comme releases ordinaires.

La version installée vient de `ANIMELAB_RELEASE_VERSION` lorsqu’elle est fournie,
du `release_tag` embarqué dans `release-metadata/build-info.json` sur desktop,
ou du champ `BuildConfig.RELEASE_VERSION` Android transmis au moteur. Ce dernier
est alimenté par `RELEASE_TAG` pendant les builds GitHub Actions. Ainsi,
`0.1.6-beta.3` est bien comparée à `0.1.6-beta.4`, et non à `0.1.6` stable.
Une exécution depuis les sources sans métadonnées utilise `animelab.__version__`.

La vérification est bornée : délai total serveur de six secondes, métadonnées
limitées à 512 Kio, aucun suivi de redirection HTTP, cache d’une heure par
fournisseur/canal/version et d’une minute sur erreur. Les vérifications
simultanées sont regroupées. Aucun jeton GitHub n’est nécessaire.
Une vérification manuelle peut rafraîchir le cache, au maximum une fois par minute.
`ANIMELAB_UPDATE_CHECK_DISABLED=true` coupe tout accès réseau au fournisseur,
y compris la vérification manuelle ; les probes Android isolés utilisent ce mode.

Le bouton **Télécharger** ouvre le fichier de release dans le navigateur ou le
gestionnaire du système. Il ne remplace pas les fichiers de l’application en
cours et n’installe rien silencieusement. Android conserve la confirmation
d’installation du système ; les archives desktop doivent être extraites selon
le guide de distribution. Une WebApp distante propose les paquets mais ne met
pas à jour son serveur depuis le navigateur.

## Hébergeur alternatif

Configurer côté moteur une URL HTTPS publique, sans identifiants :

```bash
ANIMELAB_UPDATE_FEED_URL=https://downloads.example.org/animelab/releases.json
```

Le flux JSON peut reprendre le format GitHub ou ce format indépendant :

```json
{
  "releases": [
    {
      "version": "0.1.7-beta.1",
      "notes": "# Nouveautés\n- Amélioration de la bibliothèque",
      "url": "https://downloads.example.org/animelab/0.1.7-beta.1",
      "assets": [
        {
          "name": "AnimeLab-Android-arm64.apk",
          "label": "Android ARM64",
          "url": "https://downloads.example.org/animelab/0.1.7-beta.1/AnimeLab.apk",
          "size": 123456
        }
      ]
    }
  ]
}
```

Le flux doit pointer directement vers une réponse JSON, sans redirection. Ses
versions suivent `major.minor.patch`, avec suffixe optionnel `-alpha.N`, `-beta.N`
ou `-rc.N`. Les brouillons, versions invalides et liens non HTTPS sont ignorés.
L’URL du fournisseur est un réglage opérateur, pas une entrée réseau arbitraire
ouverte aux utilisateurs du serveur partagé.

## Validation

Les tests Python utilisent un stockage temporaire et des réponses réseau
simulées. Les scénarios Playwright couvrent le premier lancement, la persistance,
les petits écrans, les canaux, le mode hors ligne, le sélecteur annulé et les
boutons de permissions. Les interactions système Android nécessitent aussi un
build Android et un essai sur appareil ; les simulations navigateur ne prouvent
pas à elles seules le fonctionnement de chaque fournisseur de documents.
