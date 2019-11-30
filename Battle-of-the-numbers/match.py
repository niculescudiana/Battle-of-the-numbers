import pygame, sys
import time
from random import *
import copy
import math
from pygame.locals import *

pygame.init()

display_width = 1500
display_height = 700

# colours
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 200, 0)
bright_red = (255, 0, 0)
bright_green = (0, 255, 0)
mmm_orange = (255, 136, 17)
mmm_orange_lite = (255, 157, 60)
mmm_yellow = (244, 208, 111)
mmm_blue = (157, 217, 210)
mmm_cream = (255, 248, 240)
mmm_purple = (57, 47, 90)
mmm_purple_lite = (93, 84, 120)

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('The Battle of the numbers')
clock = pygame.time.Clock()

img_width = 80
img_height = 120

start_screen = True


def text_objects(text, font, colour):
    text_surface = font.render(text, True, colour)
    return text_surface, text_surface.get_rect()


def draw_start_screen(mode_choice: int):
    background_image = pygame.image.load("./min/background.jpeg").convert()
    background_image = pygame.transform.scale(background_image, (1500, 620))

    gameDisplay.blit(background_image, [0, 0])

    draw_text(mmm_cream, "fonts/ARCADE.TTF", 100, "The Battle of the Numbers", (display_width / 2), 120)
    draw_text(black, "fonts/ARCADE.TTF", 35, "Mode 1", (display_width / 2) - 20, 285)
    draw_text(black, "fonts/ARCADE.TTF", 35, "Mode 2", (display_width / 2) - 20, 320)

    start = draw_interactive_button(300, 50, 485, mmm_orange, mmm_orange_lite, "START", False)
    exit_game = draw_interactive_button(300, 50, 570, red, red, "EXIT GAME", False)
    if mode_choice == 1:
        pygame.draw.circle(gameDisplay, black, (int(display_width / 2) - 100, 277), 9, 3)
    else:
        pygame.draw.circle(gameDisplay, black, (int(display_width / 2) - 100, 315), 9, 3)


def draw_text(colour, font, size, content, center_x, center_y):
    text = pygame.font.Font(font, size)
    text_surf, text_rect = text_objects(content, text, colour)
    text_rect.center = (int(center_x), center_y)
    gameDisplay.blit(text_surf, text_rect)


def draw_interactive_button(w, h, y, colour, secondary_colour, text, restart):
    stay_on_start_screen = True
    x = display_width / 2 - w / 2
    click = pygame.mouse.get_pressed()
    pygame.draw.rect(gameDisplay, secondary_colour, (int(x), y, w, h))
    draw_text(mmm_cream, "fonts/ARCADE.TTF", 50, text, display_width / 2, y + 32)
    return stay_on_start_screen


def load_card(face_up: list, face_down: list, hand_of_player1: list, hand_of_player2: list, end_game: int = 0,
              winner: int = 0):
    for i in range(len(face_up)):
        card = "./min/%s.jpeg" % face_up[i]
        img = pygame.image.load(card)
        # image_width = img.convert().get_width()
        # gameDisplay.blit(img, (0 + i * 10 * img_width//2, 70))
        gameDisplay.blit(img, (0 + i * 100, 70))

    for i in range(len(face_down)):
        card = "./min/back.jpeg"
        img = pygame.image.load(card)
        # image_width = img.convert().get_width()
        gameDisplay.blit(img, (750 + i * 50, 70))

    draw_text(mmm_cream, "fonts/ARCADE.TTF", 70, "Player 1:", 250, 420)

    for i in range(len(hand_of_player1)):
        card = "./min/%s.jpeg" % hand_of_player1[i]
        img = pygame.image.load(card)
        gameDisplay.blit(img, (20 + i * 100, 460))

    draw_text(mmm_cream, "fonts/ARCADE.TTF", 70, "Player 2:", 900, 420)

    if end_game == 0:
        for i in range(len(hand_of_player2)):
            card = "./min/back.jpeg"
            img = pygame.image.load(card)
            gameDisplay.blit(img, (700 + i * 100, 460))

        pygame.draw.rect(gameDisplay, mmm_purple_lite, (580, 625, 200, 50))
        draw_text(white, "fonts/ARCADE.TTF", 30, "ENG GAME", 670, 650)
    else:
        for i in range(len(hand_of_player2)):
            card = "./min/%s.jpeg" % hand_of_player2[i]
            img = pygame.image.load(card)
            gameDisplay.blit(img, (700 + i * 100, 460))
        if winner == 0:
            draw_text(red, "fonts/ARCADE.TTF", 80, "Player 1 WON", 670, 330)
        else:
            draw_text(red, "fonts/ARCADE.TTF", 80, "Player 2 WON", 670, 330)
        pygame.draw.rect(gameDisplay, mmm_purple_lite, (580, 625, 200, 50))
        draw_text(white, "fonts/ARCADE.TTF", 30, "PLAY AGAIN", 670, 650)

        pygame.draw.rect(gameDisplay, red, (1300, 100, 150, 50))
        draw_text(white, "fonts/ARCADE.TTF", 30, "EXIT", 1370, 125)


class Action:
    def __init__(self, option: str, card_choice: int = 0):
        if option not in ["draw", "play", "discard", "end game"]:
            raise ValueError('Invalid action: must be of type [ "draw", "play",  "discard", "end game" ]')
        self.option = option
        self.card_choice = card_choice

    def __str__(self):
        return f"{self.option} {self.card_choice}"

    def __eq__(self, other):
        return self.option == other.option and self.card_choice == other.card_choice


class State:
    def __init__(self, face_up: list, face_down: list, hand_of_player_one: list, hand_of_player_two: list,
                 mode: int = 0):
        self.face_up = face_up
        self.face_down = face_down
        self.hands_of_players = [hand_of_player_one, hand_of_player_two]
        self.winner = None
        self.mode = mode

    def __str__(self):
        return f"{self.face_up}\n{self.hands_of_players}\n" + (
            f"And the Winner is... Player {self.winner + 1}!" if self.winner is not None else " still going")

    def apply(self, player_id: int, action: Action):
        hand_of_current_player = self.hands_of_players[player_id]
        hand_of_other_player = self.hands_of_players[(player_id + 1) % 2]
        if action.card_choice not in range(len(hand_of_current_player)):
            raise ValueError('Invalid action: player does not have enough cards')
        if action.option == "draw":
            if self.face_up:
                card = self.face_up.pop(-1)
                hand_of_current_player.append(card)
        elif action.option == "play":
            if hand_of_current_player:
                card = hand_of_current_player.pop(action.card_choice)
                self.face_up.append(card)
        elif action.option == "discard":
            if hand_of_current_player:
                card = hand_of_current_player.pop(action.card_choice)
                if self.face_down:
                    self.face_down.append(card)
        elif action.option == "end game":
            if self.mode == 0:
                # you lose if either you have strictly more than the face up pile
                # or the opponent has a score between yours and the face up pile
                if sum(self.face_up) < sum(hand_of_current_player) \
                        or sum(hand_of_current_player) <= sum(hand_of_other_player) <= sum(self.face_up):
                    self.winner = (player_id + 1) % 2
                else:
                    self.winner = player_id
            else:
                if sum(self.face_up) > sum(hand_of_current_player) \
                        or sum(hand_of_current_player) >= sum(hand_of_other_player) >= sum(self.face_up):
                    self.winner = (player_id + 1) % 2
                else:
                    self.winner = player_id


class Agent:
    def __init__(
            self,
            player_id: int,
            ai: bool = True,
            depth_level: int = 1,
            logging: bool = False):

        self.player_id = player_id
        self.ai = ai
        self.depth_level = depth_level
        self.logging = logging

    @property
    def opponent_id(self):
        return (self.player_id + 1) % 2

    def score(self, known_state: State) -> float:
        face_up_sum = sum(known_state.face_up)
        current_player_sum = sum(known_state.hands_of_players[self.player_id])
        opponent_count = len(known_state.hands_of_players[self.opponent_id])
        face_down_count = len(known_state.face_down)
        if face_down_count + opponent_count != 0:
            unknown_estimated_avg = (66 - face_up_sum - current_player_sum) / (face_down_count + opponent_count)
        else:
            unknown_estimated_avg = 0
        opponent_estimated_sum = unknown_estimated_avg * face_down_count
        penalty = min((face_up_sum - current_player_sum), 0)
        score = current_player_sum - opponent_estimated_sum + 66 * penalty
        if known_state.winner is None:
            return score
        elif known_state.winner == self.player_id:
            return math.inf
        else:
            return -math.inf

    def valid_actions(self, state) -> list:
        card_count = len(state.hands_of_players[self.player_id])
        actions = [Action("end game")]
        actions.extend([Action("play", n) for n in range(card_count)])
        actions.extend([Action("discard", n) for n in range(card_count)])
        if state.face_up:
            actions.append(Action("draw"))
        return actions

    def take_decision(self, known_state: State) -> Action:
        if self.ai:
            best_score = -math.inf
            best_action = Action("end game")
            for action in self.valid_actions(known_state):
                copy_state = copy.deepcopy(known_state)
                copy_state.apply(self.player_id, action)

                if self.depth_level > 1 and copy_state.winner is None:
                    opponent = Agent(player_id=self.opponent_id, depth_level=self.depth_level - 1)

                    face_up_sum = sum(copy_state.face_up)
                    current_player_sum = sum(copy_state.hands_of_players[self.player_id])
                    opponent_count = len(copy_state.hands_of_players[self.opponent_id])
                    face_down_count = len(copy_state.face_down)
                    if face_down_count + opponent_count != 0:
                        unknown_estimated_avg = (66 - face_up_sum - current_player_sum) / (
                                face_down_count + opponent_count)
                    else:
                        unknown_estimated_avg = 0

                    player_hand = [0 for _ in copy_state.hands_of_players[self.player_id]]
                    opponent_hand = [unknown_estimated_avg for _ in copy_state.hands_of_players[self.opponent_id]]

                    opponent_state = copy.deepcopy(copy_state)
                    opponent_state.hands_of_players[self.player_id] = player_hand
                    opponent_state.hands_of_players[self.opponent_id] = opponent_hand

                    opponent_action = opponent.take_decision(opponent_state)
                    copy_state.apply(self.opponent_id, opponent_action)

                if self.score(copy_state) >= best_score:
                    best_action = action
                    best_score = self.score(copy_state)
            if self.logging:
                print(str(known_state))
            return best_action
        else:
            actions = self.valid_actions(known_state)
            action = None
            while True:

                while pygame.event.wait() and not pygame.mouse.get_pressed()[0]:
                    pass
                (x, y) = pygame.mouse.get_pos()
                print(f"outside click {(x, y)}")

                if 0 < x < 750 and 70 < y < 70 + img_height:
                    action = Action("draw")
                elif 580 < x < 780 and 625 < y < 675:
                    action = Action("end game")
                else:
                    for i in range(len(known_state.hands_of_players[0])):
                        if 20 + i * 100 < x < 20 + i * 100 + img_width and 440 < y < 440 + img_height:

                            print("inside")
                            while pygame.event.wait() and not pygame.mouse.get_pressed()[0]:
                                pass

                            (x, y) = pygame.mouse.get_pos()
                            print(f"click {(x, y)}")

                            if 0 < x < 750 and 70 < y < 70 + img_height:
                                action = Action("play", i)
                            elif 750 < x < display_width and 70 < y < 70 + img_height:
                                action = Action("discard", i)

                if action is not None and action in self.valid_actions(known_state):
                    return action


class Game:
    def __init__(self, player1: Agent, player2: Agent, mode: int = 0):
        deck = 2 * list(range(1, 6)) + 6 * list([6])
        shuffle(deck)
        if mode == 0:
            self.state = State([], deck[0:4], deck[4:10], deck[10:16], 0)
        else:
            self.state = State(deck[0:4], deck[4:10], deck[10:13], deck[13:16], 1)
        self.players = (player1, player2)
        self.current_player_id = 0

    def take_turns(self):
        if self.current_player_id == 0:
            known_state = State(
                self.state.face_up,
                [0 for _ in self.state.face_down],
                self.state.hands_of_players[0],
                [0 for _ in self.state.hands_of_players[1]])
            load_card(self.state.face_up, self.state.face_down, self.state.hands_of_players[0],
                      self.state.hands_of_players[1])
            pygame.display.update()
        else:
            known_state = State(
                self.state.face_up,
                [0 for _ in self.state.face_down],
                [0 for _ in self.state.hands_of_players[0]],
                self.state.hands_of_players[1])

        action = self.players[self.current_player_id].take_decision(known_state)

        print(f"Player {self.current_player_id + 1} will {action.option} ", end=" ")
        if action.option in ["play", "discard"]:
            print(f"{self.state.hands_of_players[self.current_player_id][action.card_choice]}", end="")
        print("\n")

        self.state.apply(self.current_player_id, action)
        print(self.state)
        gameDisplay.fill(black)
        pygame.display.update()
        if action.option == "end game":
            load_card(self.state.face_up, self.state.face_down, self.state.hands_of_players[0],
                      self.state.hands_of_players[1], end_game=1, winner=self.state.winner)
        else:
            load_card(self.state.face_up, self.state.face_down, self.state.hands_of_players[0],
                      self.state.hands_of_players[1])
        pygame.display.update()

        self.current_player_id += 1
        self.current_player_id %= 2


game = Game(Agent(player_id=0, depth_level=2, ai=False), Agent(player_id=1, depth_level=2, logging=False), mode=0)
draw_start_screen(mode_choice=1)
pygame.display.update()

wait = 1

while wait:
    while pygame.event.wait() and not pygame.mouse.get_pressed()[0]:
        pass

    (x, y) = pygame.mouse.get_pos()

    if 485 < y < 535 and 600 < x < 900:
        while game.state.winner is None:
            wait = 0
            gameDisplay.fill(black)
            pygame.display.update()
            game.take_turns()
            pygame.display.update()
        if game.state.winner is not None:
            loop = 1
            while loop:
                while pygame.event.wait() and not pygame.mouse.get_pressed()[0]:
                    pass
                (x, y) = pygame.mouse.get_pos()
                if 580 < x < 780 and 625 < y < 675:
                    gameDisplay.fill(black)
                    draw_start_screen(mode_choice=1)
                    pygame.display.update()
                    wait = 1
                    loop = 0
                elif 1300 < x < 1450 and 100 < y < 150:
                    wait = 0
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()
                    loop = 0
    elif 570 < y < 620 and 600 < x < 900:
        wait = 0
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    elif 634 < x < 789 and 265 < y < 291:
        game = Game(Agent(player_id=0, depth_level=2, ai=False), Agent(player_id=1, depth_level=2, logging=False),
                    mode=0)
        gameDisplay.fill(black)
        draw_start_screen(mode_choice=1)
        pygame.display.update()
    elif 634 < x < 789 and 302 < y < 329:
        game = Game(Agent(player_id=0, depth_level=2, ai=False), Agent(player_id=1, depth_level=2, logging=False),
                    mode=1)
        gameDisplay.fill(black)
        draw_start_screen(mode_choice=2)
        pygame.display.update()
