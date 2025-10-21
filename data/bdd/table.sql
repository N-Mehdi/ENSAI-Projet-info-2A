/*
CREATE TABLE IF NOT EXISTS cocktail (
    id_cocktail SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    categorie VARCHAR(100),
    verre VARCHAR(100),
    alcool BOOLEAN,
    image TEXT
    );
*/

-- DELETE FROM cocktail;

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
