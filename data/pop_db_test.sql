-- ================================================
-- Script de peuplement de la base de données de test
-- ================================================

-- Nettoyer les tables existantes (dans l'ordre des dépendances)
TRUNCATE TABLE 
    avis,
    liste_course,
    stock,
    acces,
    instruction,
    cocktail_ingredient,
    cocktail,
    ingredient,
    unite,
    utilisateur
CASCADE;

-- Réinitialiser les séquences
ALTER SEQUENCE cocktail_id_cocktail_seq RESTART WITH 1;
ALTER SEQUENCE ingredient_id_ingredient_seq RESTART WITH 1;
ALTER SEQUENCE unite_id_unite_seq RESTART WITH 1;
ALTER SEQUENCE instruction_id_instruction_seq RESTART WITH 1;

-- ================================
-- TABLE unite
-- ================================
INSERT INTO unite (nom, abbreviation, type_unite) VALUES
    ('millilitre', 'ml', 'liquide'),
    ('centilitre', 'cl', 'liquide'),
    ('litre', 'l', 'liquide'),
    ('once', 'oz', 'liquide'),
    ('gramme', 'g', 'solide'),
    ('cuillère à café', 'tsp', 'autre'),
    ('cuillère à soupe', 'tbsp', 'autre'),
    ('trait', 'dash', 'autre'),
    ('pièce', 'pcs', 'autre');

-- ================================
-- TABLE ingredient
-- ================================
INSERT INTO ingredient (nom, description, type, alcool, abv) VALUES
    -- Spiritueux
    ('Vodka', 'Alcool neutre distillé', 'Spirit', TRUE, '40%'),
    ('Rhum blanc', 'Rhum léger non vieilli', 'Spirit', TRUE, '40%'),
    ('Gin', 'Alcool aromatisé au genièvre', 'Spirit', TRUE, '40%'),
    ('Tequila', 'Spiritueux mexicain à base d''agave', 'Spirit', TRUE, '40%'),
    ('Triple sec', 'Liqueur d''orange', 'Liqueur', TRUE, '40%'),
    ('Rhum brun', 'Rhum vieilli en fût', 'Spirit', TRUE, '40%'),
    
    -- Jus et sodas
    ('Jus de citron vert', 'Jus de lime fraîchement pressé', 'Juice', FALSE, NULL),
    ('Jus de citron', 'Jus de citron fraîchement pressé', 'Juice', FALSE, NULL),
    ('Jus d''orange', 'Jus d''orange frais', 'Juice', FALSE, NULL),
    ('Jus de cranberry', 'Jus de canneberge', 'Juice', FALSE, NULL),
    ('Coca-Cola', 'Soda au cola', 'Soft drink', FALSE, NULL),
    ('Club Soda', 'Eau gazeuse', 'Soft drink', FALSE, NULL),
    
    -- Autres ingrédients
    ('Sucre', 'Sucre blanc granulé', 'Sweetener', FALSE, NULL),
    ('Sirop de sucre', 'Sirop simple', 'Sweetener', FALSE, NULL),
    ('Feuilles de menthe', 'Menthe fraîche', 'Herb', FALSE, NULL),
    ('Glaçons', 'Glace pilée ou en cubes', 'Ice', FALSE, NULL);

-- ================================
-- TABLE cocktail
-- ================================
INSERT INTO cocktail (nom, categorie, verre, alcool, image) VALUES
    ('Mojito', 'Cocktail', 'Highball glass', TRUE, 'https://www.thecocktaildb.com/images/media/drink/3z6xdi1589574603.jpg'),
    ('Margarita', 'Ordinary Drink', 'Cocktail glass', TRUE, 'https://www.thecocktaildb.com/images/media/drink/5nknm91582474838.jpg'),
    ('Cosmopolitan', 'Cocktail', 'Cocktail glass', TRUE, 'https://www.thecocktaildb.com/images/media/drink/kpsajh1504368362.jpg'),
    ('Cuba Libre', 'Ordinary Drink', 'Highball glass', TRUE, 'https://www.thecocktaildb.com/images/media/drink/psf9z51504366002.jpg'),
    ('Daiquiri', 'Ordinary Drink', 'Cocktail glass', TRUE, 'https://www.thecocktaildb.com/images/media/drink/mrz9091589574515.jpg');

-- ================================
-- TABLE cocktail_ingredient
-- ================================

-- Mojito (id_cocktail = 1)
INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, qte, unite) VALUES
    (1, 2, 60, 'ml'),      -- Rhum blanc
    (1, 7, 30, 'ml'),      -- Jus de citron vert
    (1, 13, 2, 'tsp'),     -- Sucre
    (1, 12, 60, 'ml'),     -- Club Soda
    (1, 15, 10, 'pcs'),    -- Feuilles de menthe
    (1, 16, 1, 'pcs');     -- Glaçons

-- Margarita (id_cocktail = 2)
INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, qte, unite) VALUES
    (2, 4, 50, 'ml'),      -- Tequila
    (2, 5, 20, 'ml'),      -- Triple sec
    (2, 7, 25, 'ml'),      -- Jus de citron vert
    (2, 16, 1, 'pcs');     -- Glaçons

-- Cosmopolitan (id_cocktail = 3)
INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, qte, unite) VALUES
    (3, 1, 40, 'ml'),      -- Vodka
    (3, 5, 15, 'ml'),      -- Triple sec
    (3, 8, 15, 'ml'),      -- Jus de citron
    (3, 10, 30, 'ml'),     -- Jus de cranberry
    (3, 16, 1, 'pcs');     -- Glaçons

-- Cuba Libre (id_cocktail = 4)
INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, qte, unite) VALUES
    (4, 2, 50, 'ml'),      -- Rhum blanc
    (4, 7, 10, 'ml'),      -- Jus de citron vert
    (4, 11, 120, 'ml'),    -- Coca-Cola
    (4, 16, 1, 'pcs');     -- Glaçons

-- Daiquiri (id_cocktail = 5)
INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, qte, unite) VALUES
    (5, 2, 60, 'ml'),      -- Rhum blanc
    (5, 7, 30, 'ml'),      -- Jus de citron vert
    (5, 14, 15, 'ml'),     -- Sirop de sucre
    (5, 16, 1, 'pcs');     -- Glaçons

-- ================================
-- TABLE instruction
-- ================================

-- Mojito (id_cocktail = 1)
INSERT INTO instruction (id_cocktail, langue, texte) VALUES
    (1, 'EN', 'Muddle mint leaves with sugar and lime juice in a highball glass. Fill the glass with crushed ice. Add rum and top with club soda. Stir gently and garnish with mint leaves and a lime wedge.');

-- Margarita (id_cocktail = 2)
INSERT INTO instruction (id_cocktail, langue, texte) VALUES
    (2, 'EN', 'Rub the rim of a cocktail glass with lime and dip it in salt. Pour tequila, triple sec, and lime juice into a shaker filled with ice. Shake vigorously and strain into the prepared glass. Garnish with a lime wedge.');

-- Cosmopolitan (id_cocktail = 3)
INSERT INTO instruction (id_cocktail, langue, texte) VALUES
    (3, 'EN', 'Pour all ingredients into a shaker filled with ice. Shake well and strain into a chilled cocktail glass. Garnish with a flamed orange peel.');

-- Cuba Libre (id_cocktail = 4)
INSERT INTO instruction (id_cocktail, langue, texte) VALUES
    (4, 'EN', 'Fill a highball glass with ice. Add rum and lime juice. Top with Coca-Cola and stir gently. Garnish with a lime wedge.');

-- Daiquiri (id_cocktail = 5)
INSERT INTO instruction (id_cocktail, langue, texte) VALUES
    (5, 'EN', 'Pour rum, lime juice, and simple syrup into a shaker filled with ice. Shake vigorously until the shaker is very cold. Strain into a chilled cocktail glass. Garnish with a lime wheel.');

-- ================================
-- Vérifications
-- ================================
SELECT 'Données insérées avec succès !' AS message;

SELECT 
    'Cocktails' AS table_name, 
    COUNT(*) AS count 
FROM cocktail
UNION ALL
SELECT 'Ingrédients', COUNT(*) FROM ingredient
UNION ALL
SELECT 'Unités', COUNT(*) FROM unite
UNION ALL
SELECT 'Cocktail_Ingredient', COUNT(*) FROM cocktail_ingredient
UNION ALL
SELECT 'Instructions', COUNT(*) FROM instruction;