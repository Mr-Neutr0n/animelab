# Sessions Cloudflare : Aniyomi, Suwayomi et correctifs AnimeLab

Étude et diagnostic du 3 novembre 2026. Périmètre : moteur partagé Linux,
Windows et macOS, WebView Android et extensions APK utilisant sa passerelle HTTP.

## Conclusion

`curl_cffi` reproduit certaines caractéristiques HTTP/TLS d'un navigateur, mais
n'exécute pas le JavaScript d'une page et ne devient pas une WebView. Un refus
n'établit donc pas à lui seul que Cloudflare a « détecté curl ». Il faut distinguer
challenge, interdiction explicite, DNS, délai réseau et restriction géographique.

La correction conserve les requêtes ordinaires dans le moteur et utilise un vrai
navigateur pour la vérification assistée. Elle maintient une identité de session
cohérente, suspend les appels de la source pendant la vérification et reprend
l'opération réelle après fermeture. Le changement de proxy est désormais réservé
aux réponses indiquant explicitement une restriction géographique.

Cela corrige les défauts identifiés d'AnimeLab. Cela ne garantit pas qu'un site
acceptera toujours une application tierce ou qu'un jeton obtenu par navigateur
sera accepté par un autre transport.

## 1. Aniyomi : WebView et client HTTP partagent la session

Révision étudiée : `97414446b8a95994c72dd33c41c971a89d4d25b8`.

Le [CloudflareInterceptor](https://github.com/aniyomiorg/aniyomi/blob/97414446b8a95994c72dd33c41c971a89d4d25b8/core/common/src/main/java/eu/kanade/tachiyomi/network/interceptor/CloudflareInterceptor.kt)
reconnaît certains refus, ferme la réponse et supprime l'ancien `cf_clearance`.
Il exécute ensuite une vraie WebView, attend le chargement ou un renouvellement
du cookie, détruit cette WebView et rejoue la requête initiale. L'attente est bornée.
Ce n'est pas un mécanisme de rotation d'adresses IP.

[AndroidCookieJar](https://github.com/aniyomiorg/aniyomi/blob/97414446b8a95994c72dd33c41c971a89d4d25b8/core/common/src/main/java/eu/kanade/tachiyomi/network/AndroidCookieJar.kt)
utilise Android CookieManager pour les lectures et écritures du client HTTP.
Le [WebViewInterceptor](https://github.com/aniyomiorg/aniyomi/blob/97414446b8a95994c72dd33c41c971a89d4d25b8/core/common/src/main/java/eu/kanade/tachiyomi/network/interceptor/WebViewInterceptor.kt)
active JavaScript et le stockage DOM et utilise l'agent utilisateur de la
requête ou son fournisseur par défaut.
Le [UserAgentInterceptor](https://github.com/aniyomiorg/aniyomi/blob/97414446b8a95994c72dd33c41c971a89d4d25b8/core/common/src/main/java/eu/kanade/tachiyomi/network/interceptor/UserAgentInterceptor.kt)
respecte un agent utilisateur explicitement fourni par l'extension.

Conséquence pour AnimeLab : partager les cookies pertinents et conserver
l'identité utilisée pour la vérification, au lieu de fabriquer une nouvelle
identité à chaque appel. La politique AnimeLab force l'identité apprise pour
le domaine vérifié afin de préserver cette session ; avant vérification, un
agent utilisateur explicitement fourni par une extension reste respecté.

## 2. Suwayomi : session du navigateur et réponse de secours optionnelle

Révision étudiée : `7b061be09c9b62a89a63addd11ac91c40fc2510f`.

Le [CloudflareInterceptor de Suwayomi](https://github.com/Suwayomi/Suwayomi-Server/blob/7b061be09c9b62a89a63addd11ac91c40fc2510f/server/src/main/kotlin/eu/kanade/tachiyomi/network/interceptor/CloudflareInterceptor.kt)
coordonne les résolutions simultanées par hôte. Avec FlareSolverr configuré,
il réutilise les cookies et **l'agent utilisateur retourné par le navigateur**,
puis réessaie la requête. La session du service a une durée de vie et des délais
bornés. La configuration peut transmettre un proxy au navigateur ; cela n'impose
pas de rotation pour chaque challenge.

Une option `flareSolverrAsResponseFallback` permet, si la reprise HTTP échoue,
de retourner la réponse réussie du navigateur pour les cas pris en charge.
Elle montre une limite importante : importer un cookie ne prouve pas que la
requête suivante, envoyée avec un autre transport, sera acceptée.

[KcefWebView](https://github.com/Suwayomi/Suwayomi-Server/blob/7b061be09c9b62a89a63addd11ac91c40fc2510f/server/src/main/kotlin/suwayomi/tachidesk/global/impl/KcefWebView.kt)
est un véritable moteur Chromium/CEF, avec échange des cookies persistants du
serveur. Il ne s'agit pas de modifier seulement des en-têtes curl.

AnimeLab ne déploie pas FlareSolverr et ne transforme pas du DOM capturé en
réponse HTTP supposée équivalente. Le transfert des réponses complètes est une
fonctionnalité distincte, non implémentée dans ce correctif. Une extraction
incorrecte perdrait notamment statuts, en-têtes, redirections ou données POST.

## 3. Défauts identifiés et changements

| Défaut | Correction |
| --- | --- |
| Agent Windows/Chrome imposé à Chromium, à la WebView et aux requêtes | Chromium fournit son UA via CDP ; Android fournit celui du WebView installé ; la WebView desktop conserve celui de son moteur. |
| En-têtes de navigateur ajoutés implicitement par curl | Désactivation des en-têtes automatiques ; suppression des client hints `sec-ch-ua*` incompatibles lorsque l'identité du domaine a été apprise. |
| Ancienne option « Random (Rotator) » changeant l'UA des appels natifs | Cette préférence historique utilise désormais le fournisseur stable par défaut. |
| UA du navigateur perdu au redémarrage | Persistance par domaine avec les cookies, liée à la même route ; suppression lors d'un changement de route. |
| Cookies de clearance associés à l'ancienne identité | Suppression de `cf_clearance` et `__cf_bm` lors d'un changement d'UA appris ; conservation des autres cookies de connexion. |
| Appels HTTP concurrents pendant la vérification Chromium | Même verrou de session que pour WebView : drain des connexions existantes, refus des nouvelles requêtes et flux. |
| Sonde HTTP exécutée alors que Chromium est ouvert | Suppression de la sonde ; import, fermeture, libération de la source, puis reprise de l'opération. |
| Reprise déclenchée au simple changement d'un cookie | Synchronisation seule pendant l'ouverture ; reprise à la confirmation ou à la fermeture observée. |
| Rotation sur CAPTCHA, 403, 451 ou coupure réseau | Rotation uniquement après indice géographique explicite ; un 403/451 seul ne suffit pas. |
| Rotation après réception partielle d'une vidéo | Suppression ; reprise Range/HLS sur la même route en conservant les données reçues. |
| Proposition « changer de proxy » sur un challenge | Retirée du panneau de vérification ; autres boutons conditionnés au diagnostic géographique du serveur. |
| Actualisation du pool public avant contrôle de la cause | Refus côté API avant toute actualisation si aucun blocage géographique n'est identifié. |

Un challenge explicite `cf-mitigated: challenge` garde priorité sur un texte
mentionnant un pays. Les restrictions géographiques reconnues comprennent des
messages explicites de pays/région et l'erreur Cloudflare 1009. Les mécanismes de
limitation existants continuent de respecter les attentes et ne provoquent pas
une rotation d'IP. Les transferts actifs interdisent toujours la rotation.

## 4. Diagnostic des sources signalées

Les adresses ci-dessous proviennent des extensions présentes dans la base locale,
consultée en lecture seule. Les essais n'ont modifié ni cette base ni les cookies
personnels. Ils ont utilisé une session isolée, sans proxy, sans lecture vidéo,
avec au plus 64 Kio de corps inspecté dans le diagnostic final.

| Source / adresse configurée | Résultat depuis cette connexion le 3 novembre | Interprétation |
| --- | --- | --- |
| Anime-Sama, `https://anime-sama.to/` | HTTP 200, serveur Cloudflare, échantillon de 65 536 octets | Cloudflare n'interdit pas systématiquement ce transport sur la page d'accueil. Recherche, lecteur et hébergeur restent des étapes différentes. |
| OtakuFR, `https://otakufr.cc/` | Erreur de transport à l'ouverture, sans réponse HTTP exploitable | Aucun challenge ni blocage géographique démontré. Ne pas changer de proxy automatiquement. |
| AniSama, `https://v1.animesz.xyz/` | Échec de résolution DNS locale (`getaddrinfo`) | Pas de réponse Cloudflare à diagnostiquer ; vérifier l'adresse actuelle de l'extension. |

`https://www.otakufr.org/` répondait aussi en HTTP 200 lors d'un premier contrôle,
mais ce n'est **pas l'adresse configurée dans l'extension installée**. Ce résultat
ne valide donc pas OtakuFR dans AnimeLab et ne justifie pas de changer son domaine
sans vérifier la compatibilité de l'extension.

Ces mesures portent sur cette machine et ce moment. Elles ne constituent ni
une validation complète des trois extensions ni un essai sur téléphone.

## 5. Validation et limites

Les régressions couvrent la persistance et la portée de l'UA, les cookies de
connexion conservés, les redirections, les flux, l'absence de rotation sur
challenge/refus ordinaire, les restrictions géographiques, et les reprises exactes
Range/HLS après interruption. Des tests avec le **Chrome réellement installé**
exercent les échanges CDP et imposent la fermeture avant reprise ; un serveur
local exige à la fois le cookie reçu et le véritable UA du navigateur.

Résultats locaux : **1 080 tests Python réussis, 5 ignorés**, contrôles Ruff et
Mypy réussis, **37 tests frontend réussis**, compilation Vue réussie et **5 essais
Playwright ciblés réussis** dans le Chrome installé (mobile/desktop, français et
anglais, reprise et politique des proxys). Aucun appareil n'était connecté à ADB
pendant ce diagnostic.

Les essais d'interface vérifient la reprise et l'absence de promesse « accès
vérifié ». L'instrumentation Android compare également l'UA exposé aux extensions
à celui du WebView installé. Une compilation ne remplace pas l'exécution de cette
instrumentation ni un essai des sites sur le téléphone de l'utilisateur.

Cloudflare documente des échecs liés à l'UA, aux IP différentes, aux WebView et
aux navigateurs automatisés. Si un site exige le navigateur pour chaque requête,
le partage de cookies seul peut rester insuffisant. AnimeLab conserve alors un
état de vérification explicite ; aucune boucle de rotation de proxy n'est lancée.

Références officielles :

- [Aniyomi : diagnostic](https://aniyomi.org/docs/guides/troubleshooting/diagnosis).
- [Cloudflare : échecs de résolution](https://developers.cloudflare.com/cloudflare-challenges/troubleshooting/challenge-solve-issues/).
- [Cloudflare : navigateurs pris en charge](https://developers.cloudflare.com/cloudflare-challenges/reference/supported-browsers/).
- [Cloudflare : fonctionnement des challenges](https://developers.cloudflare.com/cloudflare-challenges/concepts/how-challenges-work/).
- [Cloudflare : portée de la clearance](https://developers.cloudflare.com/cloudflare-challenges/concepts/clearance/).
