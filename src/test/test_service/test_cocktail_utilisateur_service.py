def service():
    return CocktailService()


def test_ajout_favori(service):
    id_user = 1
    id_cocktail = 101

    assert service.ajouter_cocktail_favori(id_user, id_cocktail)
    assert service.lister_cocktails_favoris(id_user) == [101]

    # doublon refusé
    assert not service.ajouter_cocktail_favori(id_user, id_cocktail)


def test_retrait_favori(service):
    id_user, id_cocktail = 1, 202
    service.ajouter_cocktail_favori(id_user, id_cocktail)

    assert service.retirer_cocktail_favori(id_user, id_cocktail)
    assert service.lister_cocktails_favoris(id_user) == []


def test_ajout_et_retrait_prive(service):
    id_user, id_cocktail = 2, 303
    assert service.ajouter_cocktail_prive(id_user, id_cocktail)
    assert service.lister_cocktails_prives(id_user) == [303]
    assert service.retirer_cocktail_prive(id_user, id_cocktail)
    assert service.lister_cocktails_prives(id_user) == []


def test_ajout_et_retrait_teste(service):
    id_user, id_cocktail = 3, 404
    assert service.ajouter_cocktail_teste(id_user, id_cocktail)
    assert service.lister_cocktails_testes(id_user) == [404]
    assert service.retirer_cocktail_teste(id_user, id_cocktail)
    assert service.lister_cocktails_testes(id_user) == []


def test_listes_independantes(service):
    """Vérifie que chaque type de liste est indépendant."""
    id_user = 10
    fav, prive, teste = 1, 2, 3

    service.ajouter_cocktail_favori(id_user, fav)
    service.ajouter_cocktail_prive(id_user, prive)
    service.ajouter_cocktail_teste(id_user, teste)

    assert service.lister_cocktails_favoris(id_user) == [1]
    assert service.lister_cocktails_prives(id_user) == [2]
    assert service.lister_cocktails_testes(id_user) == [3]