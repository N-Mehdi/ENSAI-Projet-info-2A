-- ================================
-- TABLE cocktail
-- ================================
CREATE TABLE IF NOT EXISTS cocktail (
    id_cocktail SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    categorie VARCHAR(100),
    verre VARCHAR(100),
    alcool BOOLEAN,
    image TEXT
);

-- ================================
-- TABLE ingredient
-- ================================
CREATE TABLE IF NOT EXISTS ingredient (
    id_ingredient SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(100),
    alcool BOOLEAN,
    abv VARCHAR(10)
);

-- ================================
-- TABLE unite
-- ================================
CREATE TABLE IF NOT EXISTS unite (
    id_unite SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    abbreviation VARCHAR(20),
    type_unite VARCHAR(20)     -- liquide, solide, autre
);

-- ================================
-- TABLE utilisateur
-- ================================
CREATE TABLE IF NOT EXISTS utilisateur (
    id_utilisateur INTEGER PRIMARY KEY,
    mail VARCHAR(255),
    mot_de_passe VARCHAR(255),
    pseudo VARCHAR(50),
    date_naissance DATE,
    date_inscription TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ================================
-- TABLE instruction
-- ================================
CREATE TABLE IF NOT EXISTS instruction (
    id_instruction SERIAL,
    id_cocktail INTEGER REFERENCES cocktail(id_cocktail) ON DELETE CASCADE,
    langue VARCHAR(5) NOT NULL,
    texte TEXT,
    PRIMARY KEY (id_instruction, langue)
);

-- ================================
-- TABLE cocktail_ingredient
-- ================================
CREATE TABLE IF NOT EXISTS cocktail_ingredient (
    id_cocktail INTEGER NOT NULL REFERENCES cocktail(id_cocktail) ON DELETE CASCADE,
    id_ingredient INTEGER NOT NULL REFERENCES ingredient(id_ingredient) ON DELETE CASCADE,
    qte NUMERIC(10,3),
    unite VARCHAR(100),
    PRIMARY KEY (id_cocktail, id_ingredient)
);

-- ================================
-- TABLE acces
-- ================================
CREATE TABLE IF NOT EXISTS acces (
    id_utilisateur INTEGER REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    id_cocktail INTEGER REFERENCES cocktail(id_cocktail) ON DELETE CASCADE,
    is_owner BOOLEAN,
    has_access BOOLEAN,
    PRIMARY KEY (id_utilisateur, id_cocktail)
);

-- ================================
-- TABLE stock
-- ================================
CREATE TABLE IF NOT EXISTS stock (
    id_utilisateur INTEGER REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    id_ingredient INTEGER REFERENCES ingredient(id_ingredient) ON DELETE CASCADE,
    quantite NUMERIC(10,3),
    id_unite INTEGER REFERENCES unite(id_unite),
    PRIMARY KEY (id_utilisateur, id_ingredient)
);

-- ================================
-- TABLE liste_course
-- ================================
CREATE TABLE IF NOT EXISTS liste_course (
    id_utilisateur INTEGER REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    id_ingredient INTEGER REFERENCES ingredient(id_ingredient) ON DELETE CASCADE,
    effectue BOOLEAN,
    quantite NUMERIC(10,3),
    id_unite INTEGER REFERENCES unite(id_unite),
    PRIMARY KEY (id_utilisateur, id_ingredient)
);

-- ================================
-- TABLE avis
-- ================================
CREATE TABLE IF NOT EXISTS avis (
    id_utilisateur INTEGER REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    id_cocktail INTEGER REFERENCES cocktail(id_cocktail) ON DELETE CASCADE,
    note INTEGER CHECK (note IS NULL OR (note >= 0 AND note <= 10)),
    commentaire TEXT CHECK (commentaire IS NULL OR LENGTH(commentaire) <= 1000),
    favoris BOOLEAN DEFAULT FALSE NOT NULL,
    date_creation TIMESTAMP(0) DEFAULT NOW() NOT NULL,
    date_modification TIMESTAMP(0) DEFAULT NOW() NOT NULL,
    PRIMARY KEY (id_utilisateur, id_cocktail)
);
