from __future__ import annotations
import random
from pathlib import Path

from PIL import Image

BASE_DIR = Path(__file__).parents[2]
CARD_ASSET_SHEET = Image.open(BASE_DIR / "assets" / "images" / "poker_cards.png")
TABLE_BACKGROUND = Image.open(BASE_DIR / "assets" / "images" / "table_background.png")
ASSET_CARD_WIDTH = 112
ASSET_CARD_HEIGHT = 123

class Deck:
    def __init__(self, size=1):
        self.size = size
        self.cards = None
        self.shuffle()

    def shuffle(self):
        suits = ["clubs", "diamonds", "hearts", "spades"]
        ranks = ["A", 2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K"]
        self.cards = [Card(ranks[card % 13], suits[card // 13]) for _ in range(self.size) for card in range(52)]
        random.shuffle(self.cards)

    def deal(self) -> Card | None:
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            return None

    def __str__(self) -> str:
        return self.cards.__str__()

class Hand:
    def __init__(self, cards: list[Card], bet=0):
        self.cards = cards
        self.bet = bet
        self.is_doubled = False

    @property
    def blackjack_value(self) -> int:
        value = 0
        for card in [card for card in self.cards if card.is_flipped]:
            value += card.blackjack_value
        for _ in range(len([card for card in self.cards if card.rank == 'A'])):
            if value > 21:
                value -= 10

        return value

    @property
    def is_soft(self) -> bool:
        value = 0
        for card in self.cards:
            value += card.blackjack_value
        aces = len([card for card in self.cards if card.rank == 'A'])
        for _ in range(aces):
            if value > 21:
                value -= 10
                aces -= 1
        return aces != 0

    def render_image(self) -> Image.Image:
        number_of_cards = len(self.cards)
        card_distance_x = 60
        card_distance_y = 20
        padding = 10
        size_x = ASSET_CARD_WIDTH + card_distance_x * (number_of_cards - 1) + padding * 2
        size_y = ASSET_CARD_HEIGHT + card_distance_y * (number_of_cards - 1) + padding * 2

        canvas = Image.new("RGBA", (size_x, size_y))
        for i, card in enumerate(self.cards):
            card_image = card.render_image()
            canvas.paste(card_image, (i * card_distance_x + padding, i * card_distance_y + padding), card_image)
        return canvas

    def clear(self):
        self.cards.clear()


class Card:
    def __init__(self, rank: int | str, suit: str, is_flipped: bool = True):
        letter_ranks = {1: "A", 11: "J", 12: "Q", 13: "K"}
        if rank in letter_ranks.keys():
            self.rank = letter_ranks.get(rank)
        else:
            self.rank = rank

        self.suit = suit
        self.is_flipped = is_flipped

    @property
    def blackjack_value(self) -> int:
        if self.rank == 'A':
            return 11
        elif self.rank in ['J', 'Q', 'K']:
            return 10
        else:
            return self.rank

    @property
    def value(self) -> int:
        if self.rank == 'A':
            return 1
        faces = {'J': 11, 'Q': 12, 'K': 13}
        if self.rank in faces.keys():
            return faces.get(self.rank)
        return self.rank

    def render_image(self) -> Image.Image:
        gap = 1

        suits = {
            "clubs": 0,
            "diamonds": 1,
            "hearts": 2,
            "spades": 3
        }
        if self.is_flipped:
            x0 = 1 + (gap + ASSET_CARD_WIDTH) * (self.value - 1)
            y0 = 1 + (gap + ASSET_CARD_HEIGHT) * suits.get(self.suit)
            x1 = x0 + ASSET_CARD_WIDTH
            y1 = y0 + ASSET_CARD_HEIGHT
        else:
            x0 = 1 + (gap + ASSET_CARD_WIDTH) * 13
            y0 = 1 + (gap + ASSET_CARD_HEIGHT) * 1
            x1 = x0 + ASSET_CARD_WIDTH
            y1 = y0 + ASSET_CARD_HEIGHT

        cropped_card = CARD_ASSET_SHEET.crop((x0, y0, x1, y1))

        return cropped_card

    def __str__(self):
        return f'{self.rank} of {self.suit}'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit