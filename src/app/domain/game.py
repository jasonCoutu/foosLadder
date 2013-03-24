from app.models import GameModel


def get_entities(query=None):
    """ Get all PlayerModels by a query, or get all of them """
    if query:
        return GameModel.query(query)
    else:
        return GameModel.query()


def new_game():
    return GameModel()
