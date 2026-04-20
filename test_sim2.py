from model.game_logic import GameLogic
from model.player import Player
from model.deck import Card

p0 = Player("0_Human")
p1 = Player("1_Bot1")
p2 = Player("2_Bot2")
p3 = Player("3_Bot3")

gl = GameLogic([p0, p1, p2, p3])

gl.discard_pile = [Card("blue", "1", "")]
gl.current_color = "blue"

def print_turn(action):
    print(f"[{action}] Current turn: {gl.current_turn}. Direction: {gl.direction}")

gl.current_turn = 0
print_turn("Start")

# P0 plays Reverse
c_r = Card("blue", "reverse", "")
p0.hand = [c_r, c_r]
gl.play_turn(0, 0)
print_turn("After P0 played Reverse")

# Now turn is 3. P3 plays +2
c_2 = Card("blue", "+2", "")
p3.hand = [c_2, c_2]
gl.play_turn(3, 0)
print_turn("After P3 played +2")

# Now turn is 1. P1 plays skip
c_s = Card("blue", "skip", "")
p1.hand = [c_s, c_s]
gl.play_turn(1, 0)
print_turn("After P1 played Skip")
