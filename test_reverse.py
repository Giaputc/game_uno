from model.game_logic import GameLogic
from model.player import Player

p0 = Player("P0")
p1 = Player("P1")
p2 = Player("P2")
p3 = Player("P3")

gl = GameLogic([p0, p1, p2, p3])

# Force hands
p0.hand = []
p1.hand = []
p2.hand = []
p3.hand = []

from model.deck import Card
c_rev = Card("red", "reverse", "red_reverse.png")
c_red1 = Card("red", "1", "")
c_red2 = Card("red", "2", "")
c_red3 = Card("red", "3", "")

# Top card is red 1
gl.discard_pile.append(c_red1)
gl.current_color = "red"

p0.hand.extend([c_rev, c_red1])
p3.hand.append(c_red2)
p2.hand.append(c_red3)

gl.current_turn = 0
print(f"Turn: {gl.current_turn}")
assert gl.current_turn == 0

print("P0 plays Reverse")
res = gl.play_turn(0, 0)
assert res == True
print(f"Turn is now: {gl.current_turn}, exact direction: {gl.direction}")

gl.play_turn(gl.current_turn, 0)
print(f"Turn after next play: {gl.current_turn}")
