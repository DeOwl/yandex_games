from data.db_session import create_session, global_init
from data.games import Game
import random
global_init('db/db.sqlite')
session = create_session()
game = Game()
id = random.randint(1000000, 10000000)
while session.query(Game).get(id):
    id = random.randint(1000000, 10000000)
game.id = id
game.name = input("название: ")
game.cost = int(input("цена: "))
game.description = input("описание: ")
session.add(game)
session.commit()

