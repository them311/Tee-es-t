# Agent Commercial - Reference Technique

## Configuration HubSpot - Baptiste Thevenot

- **Compte** : Standard (ID: 147714071)
- **Owner ID** : 80842560
- **Email** : bp.thevenot@gmail.com
- **Timezone** : US/Eastern (UTC-4)
- **Devise** : USD
- **UI** : app-eu1.hubspot.com

### Objets CRM Disponibles (Lecture + Ecriture)

| Objet | Lecture | Ecriture | Usage |
|-------|---------|----------|-------|
| CONTACT | OK | OK | Prospects, clients, leads |
| COMPANY | OK | OK | Entreprises des contacts |
| DEAL | OK | OK | Opportunites commerciales |
| TICKET | OK | OK | Support client |
| EMAIL | OK | OK | Historique emails |
| TASK | OK | OK | Taches a faire |
| NOTE | OK | OK | Notes sur les contacts |
| CALL | OK | OK | Appels telephoniques |
| MEETING_EVENT | OK | OK | Reunions |
| LINE_ITEM | OK | OK | Lignes de produit |
| PRODUCT | OK | OK | Catalogue produits |

### Objets en Lecture Seule

| Objet | Usage |
|-------|-------|
| QUOTE | Devis |
| INVOICE | Factures |
| SUBSCRIPTION | Abonnements |
| ORDER | Commandes |
| CART | Paniers |

---

## Bonnes Pratiques Email - Prospection B2C

### Structure d'un Email Efficace

1. **Objet** (< 50 caracteres)
   - Personnalise (prenom)
   - Suscite la curiosite
   - Pas de majuscules excessives
   - Pas de mots spam (gratuit, urgent, offre)

2. **Ouverture** (1 phrase)
   - Contexte personnalise
   - Montrer qu'on connait le destinataire

3. **Corps** (3-5 phrases max)
   - Proposition de valeur claire
   - Benefice concret pour le destinataire
   - Preuve sociale si possible

4. **Call-to-Action** (1 seul)
   - Question ouverte preferee
   - Proposition de creneau specifique
   - Facile a repondre (oui/non)

5. **Signature**
   - Nom complet
   - Titre/role
   - Coordonnees
   - Lien vers site/LinkedIn (optionnel)

### Timing d'Envoi Optimal

| Jour | Meilleur creneau | Taux d'ouverture |
|------|-----------------|------------------|
| Mardi | 10h-11h | Excellent |
| Mercredi | 10h-11h | Excellent |
| Jeudi | 14h-15h | Bon |
| Lundi | 11h-12h | Correct |
| Vendredi | 9h-10h | Correct |

Eviter : samedi, dimanche, lundi matin, vendredi apres-midi

### Frequence de Relance

- **Email 1** : J+0 (premier contact)
- **Email 2** : J+3 (relance douce, valeur ajoutee)
- **Email 3** : J+7 (relance directe, proposition RDV)
- **Email 4** : J+14 (derniere relance, cloture propre)
- **Apres** : Passer en "nurturing" (1 email/mois max)

### Mots-Cles Anti-Spam a Eviter

- Gratuit, free, offre speciale
- Urgent, dernier delai
- Cliquez ici, agissez maintenant
- Garantie, sans engagement
- 100%, satisfaction, meilleur prix

---

## Gestion du Pipeline HubSpot

### Etapes Standard d'un Deal

| Etape | Description | Action Attendue |
|-------|------------|-----------------|
| Prospect identifie | Contact qualifie, interet potentiel | Envoyer email 1 |
| Premier contact | Email envoye ou appel passe | Attendre reponse / relancer |
| Echange en cours | Conversation active | Qualifier le besoin |
| Proposition envoyee | Offre/devis transmis | Suivre, repondre aux objections |
| Negociation | Discussion sur les termes | Ajuster l'offre si necessaire |
| Gagne | Deal conclu | Onboarding, facturation |
| Perdu | Deal abandonne | Logger la raison, nurturing futur |

### Proprietes Essentielles d'un Contact

| Propriete | Obligatoire | Description |
|-----------|------------|-------------|
| firstname | Oui | Prenom |
| lastname | Oui | Nom |
| email | Oui | Email principal |
| phone | Recommande | Telephone |
| company | Recommande | Entreprise |
| lifecyclestage | Oui | subscriber/lead/opportunity/customer |
| hs_lead_status | Recommande | NEW/OPEN/IN_PROGRESS/CONNECTED |
| hubspot_owner_id | Oui | 80842560 (Baptiste) |

### Proprietes Essentielles d'un Deal

| Propriete | Obligatoire | Description |
|-----------|------------|-------------|
| dealname | Oui | Nom du deal |
| dealstage | Oui | Etape du pipeline |
| amount | Recommande | Montant |
| hubspot_owner_id | Oui | 80842560 (Baptiste) |
| closedate | Recommande | Date de cloture prevue |

---

## Traitement des Objections Email

### Objections Courantes et Reponses

**"Ce n'est pas le bon moment"**
> Je comprends parfaitement. Quand serait le moment ideal pour en reparler ? Je peux vous recontacter a la date qui vous convient.

**"Je n'ai pas le budget"**
> C'est tout a fait comprehensible. Puis-je vous presenter les options les plus accessibles ? Souvent, [benefice] permet de [economie/gain] qui compense largement l'investissement initial.

**"J'ai deja un prestataire"**
> Tres bien, c'est rassurant d'etre deja accompagne. Par curiosite, y a-t-il un point sur lequel vous aimeriez voir une amelioration ? Je serais ravi de vous donner un avis complementaire, sans engagement.

**"Envoyez-moi plus d'informations"**
> Avec plaisir ! Pour vous envoyer les informations les plus pertinentes, pourriez-vous me preciser [question qualifiante] ? Comme ca, je vous prepare quelque chose de cible.

**Pas de reponse (silence)**
> Relance a J+3 avec un apport de valeur (article, conseil, etude de cas), pas une simple "relance".

---

## RGPD - Regles de Conformite

### Base Legale pour la Prospection

- **B2C** : Consentement prealable obligatoire (opt-in)
- **B2B** : Interet legitime possible si lien direct avec l'activite du prospect
- **Clients existants** : Communication sur produits/services similaires autorisee

### Obligations

1. **Identification** : Chaque email doit identifier clairement l'expediteur
2. **Desabonnement** : Lien de desinscription obligatoire (ou mention claire)
3. **Donnees minimales** : Ne collecter que les donnees necessaires
4. **Droit d'acces** : Pouvoir fournir les donnees sur demande
5. **Droit a l'effacement** : Supprimer les donnees sur demande
6. **Conservation** : 3 ans max sans interaction pour les prospects

### Dans HubSpot

- Utiliser les proprietes de consentement marketing
- Logger la source de chaque contact
- Respecter les preferences de communication
- Ne jamais re-contacter un contact desabonne
