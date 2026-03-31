# Agent Commercial - Exemples d'Utilisation

## Exemple 1 : Importer une Liste de Contacts

**Commande :** `/commercial-agent importer contacts`

**Utilisateur :** "J'ai rencontre ces personnes au salon Tech Paris : Jean Dupont jean@abc.fr (ABC Corp), Marie Martin marie@xyz.com (XYZ SA), Paul Durand paul@startup.io"

**Agent :**

> J'ai identifie 3 contacts a importer. Voici le recapitulatif :
>
> | # | Prenom | Nom | Email | Entreprise | Source |
> |---|--------|-----|-------|------------|--------|
> | 1 | Jean | Dupont | jean@abc.fr | ABC Corp | Salon Tech Paris 2026 |
> | 2 | Marie | Martin | marie@xyz.com | XYZ SA | Salon Tech Paris 2026 |
> | 3 | Paul | Durand | paul@startup.io | - | Salon Tech Paris 2026 |
>
> **Verification doublons :** Aucun doublon detecte dans HubSpot.
>
> **Proprietes a definir :**
> - lifecyclestage : lead
> - hs_lead_status : NEW
> - hubspot_owner_id : 80842560 (Baptiste)
>
> Dois-je proceder a l'import ?

---

## Exemple 2 : Envoyer un Premier Email de Prospection

**Commande :** `/commercial-agent email prospection Jean Dupont`

**Agent :**

> J'ai recupere le profil de Jean Dupont dans HubSpot :
> - Email : jean@abc.fr
> - Entreprise : ABC Corp
> - Source : Salon Tech Paris 2026
> - Statut : NEW (aucune interaction precedente)
>
> Voici le brouillon que je propose :
>
> ---
> **A :** jean@abc.fr
> **Objet :** Jean, suite a notre echange au Salon Tech Paris
>
> Bonjour Jean,
>
> C'etait un plaisir d'echanger avec vous au Salon Tech Paris la semaine derniere.
>
> Votre reflexion sur [sujet discute] m'a particulierement interpelle, et je pense que nous pourrions explorer ensemble [proposition de valeur].
>
> Seriez-vous disponible pour un appel de 15 minutes cette semaine ? Je suis flexible mardi ou jeudi entre 10h et 12h.
>
> Bien cordialement,
> Baptiste Thevenot
> ---
>
> Dois-je creer ce brouillon dans Gmail ?

---

## Exemple 3 : Repondre a un Email Entrant

**Commande :** `/commercial-agent repondre` (ou detection automatique)

**Utilisateur :** "Marie Martin m'a repondu, peux-tu regarder et preparer une reponse ?"

**Agent :**

> J'ai lu le thread avec Marie Martin. Voici l'analyse :
>
> **Son message :** "Merci pour votre message. Le sujet m'interesse mais je n'ai pas de budget avant septembre. Pouvez-vous me recontacter a ce moment-la ?"
>
> **Analyse :** Objection "pas le bon moment" - interet confirme, report temporel.
>
> **Actions recommandees :**
> 1. Repondre positivement pour maintenir la relation
> 2. Mettre a jour HubSpot : hs_lead_status -> "OPEN", note "Budget disponible sept 2026"
> 3. Creer une tache de rappel pour debut septembre
>
> **Brouillon de reponse :**
>
> ---
> Bonjour Marie,
>
> Merci pour votre retour transparent, c'est tres apprecie.
>
> Je note bien pour septembre. D'ici la, je me permets de vous partager de temps en temps des ressources qui pourraient vous etre utiles sur [sujet].
>
> Je vous recontacterai debut septembre. Bel ete !
>
> Bien cordialement,
> Baptiste Thevenot
> ---
>
> Dois-je :
> - [x] Creer ce brouillon dans Gmail ?
> - [x] Mettre a jour le statut dans HubSpot ?
> - [x] Creer une tache de rappel pour le 1er septembre ?

---

## Exemple 4 : Audit du CRM

**Commande :** `/commercial-agent audit`

**Agent :**

> === AUDIT CRM - 30 Mars 2026 ===
>
> **Contacts**
> - Total : 47 contacts
> - Sans email : 3 (a completer)
> - Sans owner : 5 (a assigner)
> - Doublons potentiels : 2 paires
>
> **Deals**
> - En cours : 8 (valeur totale : 12,500 USD)
> - Sans activite > 30 jours : 3 (risque de perte)
> - Sans montant defini : 2
>
> **Actions Prioritaires :**
> 1. URGENT - Relancer les 3 deals inactifs (noms : ...)
> 2. Completer les 3 contacts sans email
> 3. Assigner les 5 contacts orphelins
> 4. Fusionner les 2 doublons
>
> Voulez-vous que je commence par une action en particulier ?

---

## Exemple 5 : Strategie de Campagne

**Commande :** `/commercial-agent strategie campagne renove`

**Utilisateur :** "Je veux lancer une campagne pour mes services de renovation aupres de particuliers"

**Agent :**

> Voici ma proposition de strategie :
>
> **Segmentation proposee :**
>
> | Segment | Critere | Taille estimee | Priorite |
> |---------|---------|---------------|----------|
> | Prospects chauds | Contact < 30 jours, reponse positive | ? | Haute |
> | Prospects tiedes | Contact < 90 jours, pas de reponse | ? | Moyenne |
> | Prospects froids | Contact > 90 jours ou aucun contact | ? | Basse |
>
> **Sequence Email - Prospects Chauds :**
>
> | Etape | Timing | Objet | Angle |
> |-------|--------|-------|-------|
> | Email 1 | J+0 | "[Prenom], votre projet de renovation" | Personnalise, reference au premier echange |
> | Email 2 | J+3 | "3 erreurs a eviter en renovation" | Valeur ajoutee, conseil expert |
> | Email 3 | J+7 | "Disponible pour un devis gratuit ?" | CTA direct |
> | Email 4 | J+14 | "Derniere question, [Prenom]" | Cloture douce |
>
> **KPIs Cibles :**
> - Taux d'ouverture : > 30%
> - Taux de reponse : > 12%
> - Conversion en RDV : > 5%
>
> Voulez-vous que je commence par segmenter vos contacts HubSpot ?

---

## Exemple 6 : Creer un Pipeline dans Notion

**Commande :** `/commercial-agent creer pipeline notion`

**Utilisateur :** "Je veux un tableau de suivi de mes prospects dans Notion"

**Agent :**

> J'ai cherche dans votre workspace Notion et aucun pipeline prospects n'existe encore.
>
> Voici ce que je propose de creer :
>
> **Base de donnees : Pipeline Prospects L-FDS**
>
> | Propriete | Type | Options |
> |-----------|------|---------|
> | Nom | title | - |
> | Email | email | - |
> | Entreprise | rich_text | - |
> | Statut | select | Nouveau, Contact, Qualifie, Proposition, Gagne, Perdu |
> | Source | select | Salon, Web, Referral, LinkedIn, Autre |
> | Montant | number | EUR |
> | Prochaine relance | date | - |
> | Email envoye | checkbox | - |
> | Notes | rich_text | - |
> | Deal HubSpot | url | Lien vers le deal |
>
> **Vues :**
> - Kanban par Statut (vue par defaut)
> - Table complete
>
> Dois-je creer cette base de donnees dans votre workspace ?

---

## Exemple 7 : Synchroniser HubSpot et Notion

**Commande :** `/commercial-agent sync hubspot notion`

**Utilisateur :** "Mets a jour le pipeline Notion avec les derniers deals HubSpot"

**Agent :**

> J'ai analyse les deux sources :
>
> **HubSpot** : 8 deals actifs
> **Notion Pipeline** : 5 lignes existantes
>
> **Actions a effectuer :**
>
> | Contact | HubSpot | Notion | Action |
> |---------|---------|--------|--------|
> | Jean Dupont | Deal "ABC Corp" - Proposition | Absent | Ajouter dans Notion |
> | Marie Martin | Deal "XYZ" - Negociation | Statut "Contact" | Mettre a jour -> "Proposition" |
> | Paul Durand | Deal "Startup" - Gagne | Statut "Qualifie" | Mettre a jour -> "Gagne" 🎉 |
>
> Dois-je proceder a ces 3 mises a jour ?

---

## Exemple 8 : Suivi Technique via GitHub

**Commande :** `/commercial-agent suivi technique`

**Utilisateur :** "Ou en est le developpement du site ? Y a-t-il des bugs ouverts ?"

**Agent :**

> J'ai consulte le repository them311/Tee-es-t :
>
> **Resume :**
> - Branche principale : main
> - Derniers commits : 4 commits cette semaine
> - Issues ouvertes : 2
> - PRs en attente : 1
>
> **Issues ouvertes :**
>
> | # | Titre | Labels | Cree le |
> |---|-------|--------|---------|
> | #5 | Formulaire contact ne fonctionne pas sur mobile | bug-prod | 28 mars |
> | #3 | Ajouter page temoignages | feature-request | 25 mars |
>
> **Pull Requests :**
>
> | # | Titre | Auteur | Statut |
> |---|-------|--------|--------|
> | #6 | Fix responsive form | them311 | En review |
>
> **Impact commercial :**
> - ⚠️ Issue #5 (formulaire mobile) pourrait bloquer la conversion de prospects mobiles
> - 💡 Issue #3 (temoignages) peut booster la confiance des prospects
>
> **Recommandations :**
> 1. Priorite haute sur #5 — 60% du trafic web est mobile
> 2. Creer une issue pour la landing page de la campagne renovation
>
> Voulez-vous que je cree une issue pour la landing page ?

---

## Exemple 9 : Workflow Complet Cross-Plateforme

**Commande :** `/commercial-agent workflow complet`

**Utilisateur :** "J'ai eu un RDV avec Sophie Lemaire de Deco Plus, elle est interessee par nos services. Gere tout."

**Agent :**

> J'ai lance le workflow complet. Voici ce que j'ai fait et ce que je propose :
>
> **1. HubSpot CRM** ✅
> - Recherche : Sophie Lemaire n'existe pas encore dans le CRM
> - Creation du contact : sophie.lemaire@decoplus.fr, Deco Plus, Source: RDV Direct
> - Creation du deal : "Deco Plus - Services Renovation", Montant: a definir, Etape: "Echange en cours"
> - Note ajoutee : "RDV du 31/03 - Interessee par nos services, a rappeler"
> - Tache creee : "Envoyer proposition Deco Plus" (echeance: 03/04)
>
> **2. Notion** 📝
> - Ajout dans Pipeline Prospects : Sophie Lemaire, Statut "Qualifie"
> - Page Compte-Rendu RDV creee :
>   - Date : 31/03/2026
>   - Contact : Sophie Lemaire - Deco Plus
>   - (A completer : vos notes du RDV)
>
> **3. Gmail** ✉️
> - Brouillon de remerciement cree :
>
> > **A :** sophie.lemaire@decoplus.fr
> > **Objet :** Sophie, merci pour notre echange !
> >
> > Bonjour Sophie,
> >
> > Merci pour le temps que vous m'avez accorde aujourd'hui. Notre echange sur vos projets de renovation chez Deco Plus etait tres enrichissant.
> >
> > Comme convenu, je vous prepare une proposition detaillee que je vous enverrai d'ici jeudi.
> >
> > N'hesitez pas si vous avez des questions entre-temps.
> >
> > Bien cordialement,
> > Baptiste Thevenot
>
> **4. GitHub** 🔧
> - Verifie : aucune issue en cours liee a Deco Plus
> - (Si besoin technique specifique, je pourrai creer une issue)
>
> **Prochaines etapes :**
> - [ ] Valider le brouillon email de remerciement
> - [ ] Completer les notes du RDV dans Notion
> - [ ] Preparer la proposition pour jeudi
>
> Voulez-vous modifier quelque chose ?
