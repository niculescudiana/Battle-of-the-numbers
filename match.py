import pygame
import sys
from random import *
from copy import deepcopy
import numpy as np
import math

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

img_width = 90
img_height = 130

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
    draw_interactive_button(300, 50, 485, mmm_orange_lite, "START")
    draw_interactive_button(300, 50, 570, red, "EXIT GAME")
    if mode_choice == 1:
        pygame.draw.circle(gameDisplay, black, (int(display_width / 2) - 100, 277), 9, 3)
    else:
        pygame.draw.circle(gameDisplay, black, (int(display_width / 2) - 100, 315), 9, 3)


def draw_text(colour, font, size, content, center_x, center_y):
    text = pygame.font.Font(font, size)
    text_surf, text_rect = text_objects(content, text, colour)
    text_rect.center = (int(center_x), center_y)
    gameDisplay.blit(text_surf, text_rect)


def draw_interactive_button(w, h, y, secondary_colour, text):
    stay_on_start_screen = True
    x = display_width / 2 - w / 2
    pygame.mouse.get_pressed()
    pygame.draw.rect(gameDisplay, secondary_colour, (int(x), y, w, h))
    draw_text(mmm_cream, "fonts/ARCADE.TTF", 50, text, display_width / 2, y + 32)
    return stay_on_start_screen


def load_card(face_up: list, face_down: list, hand_of_player1: list, hand_of_player2: list, end_game: bool = False,
              winner_id: int = 0):
    for i in range(len(face_up)):
        card = "./min/%s.jpeg" % face_up[i]
        img = pygame.image.load(card)
        gameDisplay.blit(img, (0 + i * 100, 70))

    for i in range(len(face_down)):
        card = "./min/back.jpeg"
        img = pygame.image.load(card)
        gameDisplay.blit(img, (750 + i * 50, 70))

    draw_text(mmm_cream, "fonts/ARCADE.TTF", 70, "Player 1:", 250, 420)

    for i in range(len(hand_of_player1)):
        card = "./min/%s.jpeg" % hand_of_player1[i]
        img = pygame.image.load(card)
        gameDisplay.blit(img, (20 + i * 100, 460))

    draw_text(mmm_cream, "fonts/ARCADE.TTF", 70, "Player 2:", 900, 420)

    if end_game is False:
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
        draw_text(red, "fonts/ARCADE.TTF", 80, f"Player {winner_id + 1} WON", 670, 330)
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
                 mode: int = 1):
        self.face_up = face_up
        self.face_down = face_down
        self.hands_of_players = [hand_of_player_one, hand_of_player_two]
        self.winner = None
        self.mode = mode

    # intoarce True daca jocul este inca activ adica daca nu exista un castigator
    @property
    def is_active(self):
        return self.winner is None

    def __str__(self):
        return f"{self.face_up}\n{self.hands_of_players}\n" + (
            f"And the Winner is... Player {self.winner + 1}!" if self.winner is not None else " still going")

    def apply(self, player_id: int, action: Action):
        hand_of_current_player = self.hands_of_players[player_id]
        hand_of_other_player = self.hands_of_players[(player_id + 1) % 2]
        if action.option in ["play", "discard"] and action.card_choice not in range(len(hand_of_current_player)):
            raise ValueError('Invalid action: player does not have enough cards')
        # ia ultima carte cu fata in sus si o pune in mana jucatorului curent
        if action.option == "draw":
            if self.face_up:
                card = self.face_up.pop(-1)
                hand_of_current_player.append(card)
        # ia cartea de la action.card_choice din mana jucatorului si o pune cu fata in sus
        elif action.option == "play":
            if hand_of_current_player:
                card = hand_of_current_player.pop(action.card_choice)
                self.face_up.append(card)
        # ia cartea de la action.card_choice din mana jucatorului si o pune cu fata in jos
        elif action.option == "discard":
            if hand_of_current_player:
                card = hand_of_current_player.pop(action.card_choice)
                if self.face_down:
                    self.face_down.append(card)
        elif action.option == "end game":
            if self.mode == 1:
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


def draw_frame_around_card(color, card_x, card_y, thickness=10):
    # margine din stanga
    pygame.draw.rect(gameDisplay, color, (card_x - thickness, card_y, thickness, img_height))
    # margine de dreapta
    pygame.draw.rect(gameDisplay, color, (card_x + img_width, card_y, thickness, img_height))
    # margine de sus
    pygame.draw.rect(gameDisplay, color, (card_x - thickness, card_y - thickness, img_width + 2*thickness, thickness))
    # margine de jos
    pygame.draw.rect(gameDisplay, color, (card_x - thickness, card_y + img_height, img_width + 2*thickness, thickness))
    pygame.display.update()


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

    # estimeaza avantajul jucatorului self in situatia in care jocul se afla in starea known_state
    def score(self, known_state: State) -> float:
        # aici se estimeaza suma cartilor (necunoscute) din mana adversarului
        face_up_sum = sum(known_state.face_up)
        current_player_sum = sum(known_state.hands_of_players[self.player_id])
        opponent_count = len(known_state.hands_of_players[self.opponent_id])
        face_down_count = len(known_state.face_down)
        if face_down_count + opponent_count != 0:
            unknown_sum = (66 - face_up_sum - current_player_sum)
            unknown_estimated_avg = unknown_sum / (face_down_count + opponent_count)
        else:
            unknown_estimated_avg = 0
        opponent_estimated_sum = unknown_estimated_avg * face_down_count
        # daca jucatorul are mai mult decat jos, nu are cum sa castige indiferent de catrile adversarului
        # va primi o penalizare care va fi inmultita cu un numar foarte mare pentru a prioritiza sa aiba mai putin
        penalty = 66 * max((current_player_sum - face_up_sum), 0)
        score = current_player_sum - opponent_estimated_sum - penalty
        if known_state.is_active:
            # daca jocul este activ intoarce avantajul jucatorului calculat pana acum
            return score if known_state.mode == 1 else -score
        elif known_state.winner == self.player_id:
            # daca jucatorul a castigat jocul avantajul ia cea mai mare valoare pe care o poate lua
            return math.inf
        else:
            return -math.inf

    # intoarce o lista cu toate actiunile pe care le poate lua self din starea state
    def valid_actions(self, state) -> list:
        card_count = len(state.hands_of_players[self.player_id])
        actions = [Action("end game")]
        actions.extend([Action("play", n) for n in range(card_count)])
        actions.extend([Action("discard", n) for n in range(card_count)])
        if state.face_up:
            actions.append(Action("draw"))
        return actions

    def estimate_opponent_state(self, state):
        # estimeaza valoarea medie a cartilor necunoscute
        face_up_sum = sum(state.face_up)
        current_player_sum = sum(state.hands_of_players[self.player_id])
        opponent_count = len(state.hands_of_players[self.opponent_id])
        face_down_count = len(state.face_down)
        if face_down_count + opponent_count != 0:
            unknown_sum = (66 - face_up_sum - current_player_sum)
            unknown_estimated_avg = unknown_sum / (face_down_count + opponent_count)
        else:
            unknown_estimated_avg = 0

        # conventia este ca toate cartile necunoscute sa fie reprezentate ca un 0, pentru a pute fi numarate
        player_hand = [0 for _ in state.hands_of_players[self.player_id]]
        state.hands_of_players[self.player_id] = player_hand

        # calculeaza cartile pe care le ar putea avea oponentul in mana
        # media lor trebuie sa ramana egala cu unknown_estimated_avg si numarul lor egal cu opponent_count
        start = max([1, 2 * unknown_estimated_avg - 6])
        stop = min([2 * unknown_estimated_avg - 1, 6])
        opponent_hand = [i for i in np.linspace(start=start, stop=stop, num=opponent_count)]
        state.hands_of_players[self.opponent_id] = opponent_hand

    # calucueaza cea mai buna actiune pe care o poate lua self daca jocul se afla in starea known_state
    def take_decision(self, known_state: State) -> Action:
        if self.ai:
            best_score = -math.inf
            best_action = Action("end game")
            # considera fiecare actiune pe care o poate lua
            for action in self.valid_actions(known_state):
                # creaza o copie a starii curente
                # copia urmeaza sa fie modificata, dar starea curenta ramane aceasi
                future_state = deepcopy(known_state)
                # afla in ce stare s-ar afla daca s-ar intampla actiunea aleasa
                future_state.apply(self.player_id, action)

                # caluculeaza recursiv cea mai buna miscare pe care o poate lua oponentul
                if self.depth_level > 1 and future_state.is_active:
                    # creaza o instata de agent care sa ia decizia ce ar face oponentul
                    opponent = Agent(player_id=self.opponent_id, depth_level=self.depth_level - 1)
                    # o stare in care ar crede oponentul ca se afla pentru a calcula ce ar face el in acea situatie
                    opponent_state = deepcopy(future_state)
                    self.estimate_opponent_state(opponent_state)
                    # oponentul alege care ar fi cea mai buna mutare pentru el plecand de la starea opponent_state
                    opponent_action = opponent.take_decision(opponent_state)
                    # aplica actiunea aleasa pentru a estima in ce stare se va afla jocul dupa actiunea oponentului
                    future_state.apply(self.opponent_id, opponent_action)

                # cauta actiunea care rezulta in cel mai mare avantaj
                if self.score(future_state) >= best_score:
                    best_action = action
                    best_score = self.score(future_state)
            if self.logging:
                print(str(known_state))
            return best_action
        else:
            action = None
            while True:

                while pygame.event.wait() and not pygame.mouse.get_pressed()[0]:
                    pass
                (x, y) = pygame.mouse.get_pos()

                if 0 < x < 750 and 70 < y < 70 + img_height:
                    action = Action("draw")
                elif 580 < x < 780 and 625 < y < 675:
                    action = Action("end game")
                else:
                    for i in range(len(known_state.hands_of_players[0])):
                        if 20 + i * 100 < x < 20 + i * 100 + img_width and 460 < y < 460 + img_height:

                            # highlight player card
                            draw_frame_around_card(mmm_orange_lite, card_x=20+i*100, card_y=460)

                            while pygame.event.wait() and not pygame.mouse.get_pressed()[0]:
                                pass

                            (x, y) = pygame.mouse.get_pos()

                            if 0 < x < 750 and 70 < y < 70 + img_height:
                                action = Action("play", i)
                            elif 750 < x < display_width and 70 < y < 70 + img_height:
                                action = Action("discard", i)

                            # mask highlight
                            draw_frame_around_card(black, card_x=20+i*100, card_y=460)

                if action is not None and action in self.valid_actions(known_state):
                    return action


class Game:
    def __init__(self, player1: Agent, player2: Agent, mode: int = 1):
        deck = 2 * list(range(1, 6)) + 6 * list([6])
        shuffle(deck)
        if mode == 1:
            self.state = State([], deck[0:4], deck[4:10], deck[10:16], mode)
        else:
            self.state = State(deck[0:4], deck[4:10], deck[10:13], deck[13:16], mode)
        self.players = (player1, player2)
        self.current_player_id = 0

    def take_turns(self):
        # creaza o stare in care sunt numai cartiile cunoscute
        # toate cartile necunoscute vor fi reprezentate ca un 0, pentru a pute fi numarate
        known_state = State(
            self.state.face_up,
            [0 for _ in self.state.face_down],
            [(card if self.current_player_id == 0 else 0) for card in self.state.hands_of_players[0]],
            [(0 if self.current_player_id == 0 else card) for card in self.state.hands_of_players[1]])
        if self.current_player_id == 0:
            load_card(self.state.face_up, self.state.face_down, self.state.hands_of_players[0],
                      self.state.hands_of_players[1])
            pygame.display.update()

        action = self.players[self.current_player_id].take_decision(known_state)

        print(f"Player {self.current_player_id + 1} will {action.option} ", end=" ")
        if action.option is "play":
            print(f"{self.state.hands_of_players[self.current_player_id][action.card_choice]}", end="")
        print("\n")
        self.state.apply(self.current_player_id, action)

        gameDisplay.fill(black)
        pygame.display.update()
        load_card(self.state.face_up, self.state.face_down,
                  self.state.hands_of_players[0],
                  self.state.hands_of_players[1],
                  end_game=action.option == "end game", winner_id=self.state.winner)
        pygame.display.update()

        self.current_player_id += 1
        self.current_player_id %= 2


wait = 1
game_mode = 1

while wait:
    game = Game(Agent(player_id=0, ai=False), Agent(player_id=1, depth_level=3), mode=game_mode)
    gameDisplay.fill(black)
    draw_start_screen(mode_choice=game_mode)
    pygame.display.update()

    while pygame.event.wait() and not pygame.mouse.get_pressed()[0]:
        pass

    (x, y) = pygame.mouse.get_pos()

    # buton de start game
    if 485 < y < 535 and 600 < x < 900:
        while game.state.is_active:
            wait = 0
            gameDisplay.fill(black)
            pygame.display.update()
            game.take_turns()
        # jocul s-a terminat
        pygame.display.update()
        loop = 1
        while loop:
            while pygame.event.wait() and not pygame.mouse.get_pressed()[0]:
                pass
            (x, y) = pygame.mouse.get_pos()
            # buton de play again
            if 580 < x < 780 and 625 < y < 675:
                gameDisplay.fill(black)
                draw_start_screen(mode_choice=game_mode)
                pygame.display.update()
                wait = 1
                loop = 0
            # buton de exit
            elif 1300 < x < 1450 and 100 < y < 150:
                wait = 0
                pygame.display.quit()
                pygame.quit()
                sys.exit()
    # buton de exit
    elif 570 < y < 620 and 600 < x < 900:
        wait = 0
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    elif 634 < x < 789 and 265 < y < 291:
        game_mode = 1
    elif 634 < x < 789 and 302 < y < 329:
        game_mode = 2
