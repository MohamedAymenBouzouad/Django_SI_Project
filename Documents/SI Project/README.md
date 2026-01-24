# Système d'Information de Gestion Logistique

Un système complet de gestion logistique pour une société de transport et de livraison de colis, développé avec Django.

## Architecture du Système

### Structure des Modèles

#### 1. Modèles Communs (`common/models.py`)
- **CustomUser**: Utilisateur personnalisé avec rôles (admin, agent, client, chauffeur)
- **Client**: Informations clients avec gestion des soldes
- **Driver**: Gestion des chauffeurs et leurs informations professionnelles
- **Vehicle**: Flotte de véhicules avec capacités et maintenance
- **Destination**: Destinations de livraison avec tarifs de base
- **ServiceType**: Types de services (standard, express, international)
- **Pricing**: Tarification combinant service et destination

#### 2. Gestion des Expéditions (`common/models.py`)
- **Shipment**: Colis avec tracking et états
- **ShipmentTracking**: Historique de suivi détaillé
- **Tour**: Tournées de livraison regroupant plusieurs expéditions

#### 3. Facturation et Paiements (`common/models.py`)
- **Invoice**: Factures regroupant plusieurs expéditions
- **Payment**: Paiements clients avec méthodes multiples
- **InvoiceShipment**: Relation many-to-many factures-expéditions

#### 4. Gestion des Incidents (`common/models.py`)
- **IncidentType**: Types d'incidents classés par sévérité
- **Incident**: Incidents avec suivi et résolution

#### 5. Gestion des Réclamations (`common/models.py`)
- **Claim**: Réclamations clients avec priorités
- **ClaimAttachment**: Pièces jointes aux réclamations
- **ClaimNote**: Notes internes de suivi

#### 6. Analyses et Tableaux de Bord (`common/models.py`)
- **Dashboard**: Configurations de tableaux de bord personnalisés
- **DashboardWidget**: Widgets individuels (charts, tables, métriques)
- **Report**: Rapports programmés et personnalisés
- **ReportExecution**: Historique d'exécution des rapports
- **AnalyticsSnapshot**: Données d'analyses pré-calculées

## Fonctionnalités Implémentées

### Section 0: Favoris
- Système de favoris personnalisables par utilisateur
- Accès rapide aux fonctionnalités fréquemment utilisées

### Section 1: Tables Principales
- Gestion complète des entités de base (CRUD)
- Recherche, filtrage et export des données
- Validation des données et contraintes d'intégrité

### Section 2: Gestion et Suivi des Expéditions
- Création d'expéditions avec calcul automatique des montants
- Suivi en temps réel avec historique détaillé
- Gestion des tournées et affectation chauffeur/véhicule
- Statuts automatiques selon l'avancement

### Section 3: Facturation et Paiements
- Génération automatique de factures
- Calcul TVA (19%) et montants TTC
- Suivi des paiements et soldes clients
- Génération de reçus et relances

### Section 4: Gestion des Incidents
- Saisie et classification des incidents
- Mise à jour automatique des statuts d'expédition
- Escalade et résolution des problèmes
- Analyse des causes et prévention

### Section 5: Gestion des Réclamations
- Centralisation des réclamations clients
- Suivi des délais de traitement par priorité
- Gestion des tâches et attribution aux agents
- Mesure de la satisfaction client

### Section 6: Analyses et Tableaux de Bord
- Métriques commerciales (CA, évolution, top clients)
- Analyses opérationnelles (performance livraison, chauffeurs)
- Tableaux de bord personnalisables
- Rapports automatisés et exports

## Sécurité et Authentification

- Authentification par rôle avec permissions granulares
- Journalisation des actions sensibles
- Chiffrement des données sensibles
- Contrôle d'accès basé sur les rôles

## Architecture Technique

### Base de Données
- PostgreSQL/MySQL recommandé pour production
- Indexes optimisés pour les requêtes fréquentes
- Contraintes d'intégrité referential

### API et Interfaces
- REST API pour intégrations tierces
- Portail client pour suivi des expéditions
- Application mobile chauffeur
- Interface d'administration

### Performance
- Calculs pré-calculés pour les analyses
- Cache pour les données fréquemment consultées
- Optimisation des requêtes avec select_related/prefetch_related

## Installation et Configuration

1. Installer les dépendances Python
2. Configurer la base de données
3. Exécuter les migrations
4. Créer un superutilisateur
5. Configurer les paramètres système

## Utilisation

### Pour les Agents
- Création et gestion des expéditions
- Organisation des tournées
- Gestion des incidents et réclamations
- Consultation des analyses

### Pour les Clients
- Suivi des expéditions en temps réel
- Consultation des factures
- Soumission de réclamations
- Accès à l'historique

### Pour les Chauffeurs
- Consultation des tournées assignées
- Mise à jour des statuts de livraison
- Signalement d'incidents
- Tracking GPS

## Évolutivité

L'architecture modulaire permet l'ajout facile de :
- Nouveaux types de services
- Intégrations avec des transporteurs externes
- Nouvelles méthodes de paiement
- Fonctionnalités de géolocalisation avancées

## Conformité

Le système respecte les standards de :
- Sécurité des données (RGPD)
- Traçabilité des opérations
- Conformité fiscale
- Standards UI/UX