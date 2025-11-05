/*

CREATE TABLE IF NOT EXISTS cocktail (
    id_cocktail SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    categorie VARCHAR(100),
    verre VARCHAR(100),
    alcool BOOLEAN,
    image TEXT
    );

CREATE TABLE IF NOT EXISTS ingredient (
    id_ingredient SERIAL PRIMARY KEY, 
    nom VARCHAR(255) NOT NULL,             
    description TEXT,                  
    type VARCHAR(100),                    
    alcool BOOLEAN,                        
    abv VARCHAR(10)                          
);

CREATE TABLE IF NOT EXISTS instruction (
    id_instruction SERIAL,
    id_cocktail INTEGER UNIQUE REFERENCES cocktail(id_cocktail) ON DELETE CASCADE,
    langue VARCHAR(5) NOT NULL,
    texte TEXT,
    PRIMARY KEY (id_instruction, langue)
);

CREATE TABLE IF NOT EXISTS cocktail_ingredient (
    id_cocktail INT NOT NULL,
    id_ingredient INT NOT NULL,
    quantite VARCHAR(50),
    id_unite VARCHAR(50),
    PRIMARY KEY (id_cocktail, id_ingredient),
    FOREIGN KEY (id_cocktail) REFERENCES cocktail(id_cocktail) ON DELETE CASCADE,
    FOREIGN KEY (id_ingredient) REFERENCES ingredient(id_ingredient) ON DELETE CASCADE
);

/* UPDATE ingredient
SET nom = INITCAP(nom);
*/

CREATE TABLE IF NOT EXISTS unite (
    id_unite SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    abbreviation VARCHAR(20),
    type_unite VARCHAR(20)   -- 'liquide', 'solide', 'autre'
);

CREATE TABLE IF NOT EXISTS utilisateur (
    id_utilisateur INTEGER PRIMARY KEY,
    mail VARCHAR(255),
    mot_de_passe VARCHAR(255),
    pseudo VARCHAR(50),
    date_naissance DATE,
    date_inscription DATE
);


CREATE TABLE IF NOT EXISTS avis (
    id_utilisateur INTEGER,
    id_cocktail INTEGER,
    note NUMERIC,
    commentaire TEXT,
    favoris BOOLEAN,
    PRIMARY KEY (id_utilisateur, id_cocktail)
);

CREATE TABLE IF NOT EXISTS acces (
    id_utilisateur INTEGER,
    id_cocktail INTEGER,
    is_owner BOOLEAN,
    can_access BOOLEAN,
    PRIMARY KEY (id_utilisateur, id_cocktail)
);

CREATE TABLE IF NOT EXISTS stock (
    id_utilisateur INTEGER,
    id_ingredient INTEGER,
    quantite NUMERIC(10,3),
    id_unite INTEGER,
    PRIMARY KEY (id_utilisateur, id_ingredient)
);

CREATE TABLE IF NOT EXISTS liste_course (
    id_utilisateur INTEGER,
    id_ingredient INTEGER,
    effectue BOOLEAN,
    quantite NUMERIC(10,3),
    id_unite INTEGER,
    PRIMARY KEY (id_utilisateur, id_ingredient)
);

*/

-- INSERT INTO utilisateur (mail, mot_de_passe, pseudo, date_naissance)
-- VALUES ('monmail@example.com', 'monMotDePasse', 'monPseudo', '1990-01-01');

/* 

ALTER TABLE acces
ADD CONSTRAINT fk_utilisateur_acces
FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur);
 
ALTER TABLE acces
ADD CONSTRAINT fk_cocktail_acces
FOREIGN KEY (id_cocktail) REFERENCES cocktail(id_cocktail);


ALTER TABLE avis
ADD CONSTRAINT fk_utilisateur_avis
FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur);

ALTER TABLE avis
ADD CONSTRAINT fk_cocktail_avis
FOREIGN KEY (id_cocktail) REFERENCES cocktail(id_cocktail);


ALTER TABLE liste_course
ADD CONSTRAINT fk_utilisateur_course
FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur);

ALTER TABLE liste_course
ADD CONSTRAINT fk_ingredient_course
FOREIGN KEY (id_ingredient) REFERENCES ingredient(id_ingredient);

ALTER TABLE liste_course
ADD CONSTRAINT fk_unite_course
FOREIGN KEY (id_unite) REFERENCES unite(id_unite);


ALTER TABLE instruction
ADD CONSTRAINT fk_cocktail_instruction
FOREIGN KEY (id_cocktail) REFERENCES cocktail(id_cocktail);


ALTER TABLE stock
ADD CONSTRAINT fk_unite_stock
FOREIGN KEY (id_unite) REFERENCES unite(id_unite);

ALTER TABLE stock
ADD CONSTRAINT fk_utilisateur_stock
FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur);

ALTER TABLE stock
ADD CONSTRAINT fk_ingredient_stock
FOREIGN KEY (id_ingredient) REFERENCES ingredient(id_ingredient);


ALTER TABLE cocktail_ingredient
ALTER COLUMN id_unite TYPE INTEGER USING id_unite::INTEGER;

ALTER TABLE cocktail_ingredient
ADD CONSTRAINT fk_unite_cocktail_ingredient
FOREIGN KEY (id_unite) REFERENCES unite(id_unite);

*/

/*

ALTER TABLE utilisateur
DROP COLUMN date_inscription;

ALTER TABLE utilisateur
ADD COLUMN date_inscription timestamptz NOT NULL DEFAULT now();

*/

-- Vider en cascade (vide aussi les tables dépendantes)
TRUNCATE TABLE utilisateur RESTART IDENTITY CASCADE;
