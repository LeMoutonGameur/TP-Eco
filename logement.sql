-- SQL Pour detruire les tables existantes 

-- Attention a respecter l'ordre de suppression pour ne pas créer de probleme avec les cles etrangeres (ex: ne pas supp logement avant piece)

-- Suppression de la table Mesure
DROP TABLE IF EXISTS Mesure;
-- Suppression de la table CapteurActionneur
DROP TABLE IF EXISTS CapteurActionneur;
-- Suppression de la table TypeCapteurActionneur
DROP TABLE IF EXISTS TypeCapteurActionneur;
-- Suppression de la table Facture
DROP TABLE IF EXISTS Facture;
-- Suppression de la table Piece
DROP TABLE IF EXISTS Piece;
-- Suppression de la table Logement
DROP TABLE IF EXISTS Logement;


-- CREATION DES TABLES

-- Création de la table Logement
CREATE TABLE Logement (
    id_logement INTEGER PRIMARY KEY AUTOINCREMENT,
    adresse TEXT NOT NULL,
    ville TEXT NOT NULL,
    numero_telephone TEXT NOT NULL,
    adresse_ip TEXT NOT NULL,
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Création de la table Piece
CREATE TABLE Piece (
    id_piece INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    coordonnees TEXT NOT NULL,
    id_logement INTEGER,
    FOREIGN KEY (id_logement) REFERENCES Logement(id_logement)
);

-- Création de la table TypeCapteurActionneur
CREATE TABLE TypeCapteurActionneur (
    id_type INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_type TEXT NOT NULL,
    unite_mesure TEXT
);

-- Création de la table CapteurActionneur
CREATE TABLE CapteurActionneur (
    id_capteur_actionneur INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_commerciale TEXT NOT NULL,
    id_piece INTEGER,
    id_type INTEGER,
    topic TEXT,
    port_communication TEXT NOT NULL,
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_piece) REFERENCES Piece(id_piece),
    FOREIGN KEY (id_type) REFERENCES TypeCapteurActionneur(id_type)
);

-- Création de la table Mesure
CREATE TABLE Mesure (
    id_mesure INTEGER PRIMARY KEY AUTOINCREMENT,
    id_capteur_actionneur INTEGER,
    valeur REAL NOT NULL,
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_capteur_actionneur) REFERENCES CapteurActionneur(id_capteur_actionneur)
);


-- Création de la table Facture
CREATE TABLE Facture (
    id_facture INTEGER PRIMARY KEY AUTOINCREMENT,
    id_logement INTEGER,
    type_facture TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    montant REAL NOT NULL,
    valeur_consomme REAL,
    FOREIGN KEY (id_logement) REFERENCES Logement(id_logement)
);  


-- Implementation de la base de donnees

-- Insertion d'un logement
INSERT INTO Logement (adresse, ville, numero_telephone, adresse_ip)
VALUES ('1 Rue de Jussieu', "Paris", '0123456789', '1.2.3.3');


-- Insertion de 4 pièces pour ce logement
INSERT INTO Piece (nom, coordonnees, id_logement)
VALUES ('Salon', '1,1,0', 1);

INSERT INTO Piece (nom, coordonnees, id_logement)
VALUES ('Cuisine', '1,2,0', 1);

INSERT INTO Piece (nom, coordonnees, id_logement)
VALUES ('Chambre', '2,1,0', 1);

INSERT INTO Piece (nom, coordonnees, id_logement)
VALUES ('Salle de bain', '2,2,0', 1);


-- Insertion de types de capteurs/actionneurs
INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure)
VALUES ('Temperature', '°C');

INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure)
VALUES ('Luminosite', 'lux');

INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure)
VALUES ('Humidite', '%');

INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure)
VALUES ('Consommation', 'kWh');

INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure)
VALUES ('Actionneur', 'On/Off');


-- Insertion de capteurs/actionneurs
INSERT INTO CapteurActionneur (ref_commerciale, id_piece, id_type, port_communication, topic)
VALUES ('Temp_Piece1', 1, 1, 'COM1', '1_1'); --id piece1 = 1 / id type = temperature = 1 topic = 1_1

INSERT INTO CapteurActionneur (ref_commerciale, id_piece, id_type, port_communication, topic)
VALUES ('Humi_Piece2', 2, 3, 'COM2', '2_2'); --id piece2 = 2 / id type = luminosite = 2 topic = 2_2


-- Mesures pour le capteur de temperature dans piece 1 logement 1 = capteur 1
INSERT INTO Mesure (id_capteur_actionneur, valeur)
VALUES (1, 22.5);

INSERT INTO Mesure (id_capteur_actionneur, valeur)
VALUES (1, 23.1);


-- Mesures pour le capteur de luminosite dans piece 2 logement 1 = capteur 2
INSERT INTO Mesure (id_capteur_actionneur, valeur)
VALUES (2,35);

INSERT INTO Mesure (id_capteur_actionneur, valeur)
VALUES (2, 40);


-- Insertion d'une facture d'eau pour le logement
INSERT INTO Facture (id_logement, type_facture, date, montant, valeur_consomme)
VALUES (1, 'Eau', '2024-11-10', 30.5, 15.3);

INSERT INTO Facture (id_logement, type_facture, date, montant, valeur_consomme)
VALUES 
    (1, 'Eau', '2024-09-05', 25.0, 12.5),
    (1, 'Eau', '2024-10-05', 30.0, 14.5),
    (1, 'Eau', '2024-11-05', 35.5, 16.0),
    (1, 'Eau', '2024-12-05', 40.0, 18.5);

    
-- Insertion d'une facture d'électricité pour le logement
INSERT INTO Facture (id_logement, type_facture, date, montant, valeur_consomme)
VALUES (1, 'Électricité', '2024-11-01', 45.0, 100.0);

INSERT INTO Facture (id_logement, type_facture, date, montant, valeur_consomme)
VALUES 
    (1, 'Électricité', '2024-09-01', 50.0, 120.0),
    (1, 'Électricité', '2024-10-01', 55.0, 125.0),
    (1, 'Électricité', '2024-11-01', 45.0, 100.0),
    (1, 'Électricité', '2024-12-01', 60.0, 140.0);


-- Insertion d'une facture de déchets pour le logement
INSERT INTO Facture (id_logement, type_facture, date, montant, valeur_consomme)
VALUES (1, 'Déchets', '2024-10-25', 20.0, 10.5);

INSERT INTO Facture (id_logement, type_facture, date, montant, valeur_consomme)
VALUES 
    (1, 'Déchets', '2024-09-10', 15.0, NULL),
    (1, 'Déchets', '2024-10-10', 20.0, NULL),
    (1, 'Déchets', '2024-11-10', 25.0, NULL),
    (1, 'Déchets', '2024-12-10', 30.0, NULL);


-- Insertion d'une facture de chauffage pour le logement
INSERT INTO Facture (id_logement, type_facture, date, montant, valeur_consomme)
VALUES (1, 'Chauffage', '2024-10-30', 60.0, 50.0);

INSERT INTO Facture (id_logement, type_facture, date, montant, valeur_consomme)
VALUES 
    (1, 'Chauffage', '2024-09-15', 75.0, 50.0),
    (1, 'Chauffage', '2024-10-15', 80.0, 55.0),
    (1, 'Chauffage', '2024-11-15', 85.0, 60.0),
    (1, 'Chauffage', '2024-12-15', 90.0, 65.0);
