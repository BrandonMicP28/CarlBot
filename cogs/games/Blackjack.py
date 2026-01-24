from __future__ import annotations

import dataclasses
import random
from pathlib import Path

import discord
from PIL import Image, ImageDraw, ImageFont
from discord import Member

from cogs.games.CardGame import Hand, Deck

BASE_DIR = Path(__file__).parents[2]
CARD_ASSET_SHEET = Image.open(BASE_DIR / "assets" / "images" / "poker_cards.png")
TABLE_BACKGROUND = Image.open(BASE_DIR / "assets" / "images" / "table_background.png")
ASSET_CARD_WIDTH = 112
ASSET_CARD_HEIGHT = 123

def blackjack_winning_multiplier(player_hand: Hand, dealer_hand: Hand) -> float:

    player_value = player_hand.blackjack_value

    if player_value > 21:
        return 0

    dealer_value = dealer_hand.blackjack_value

    dealer_has_blackjack = False
    if len(dealer_hand.cards) == 2 and dealer_value == 21:
        dealer_has_blackjack = True

    if len(player_hand.cards) == 2 and player_value == 21:
        if not dealer_has_blackjack:
            return 2.5
        else:
            return 1
    if dealer_has_blackjack:
        return 0
    if dealer_value > 21:
        return 2

    if player_value == dealer_value:
        return 1

    return 2 if player_value > dealer_value else 0

class Blackjack:

    class Player:
        def __init__(self, member: Member, hands: list[Hand]):
            self.member = member
            self.hands = hands

    def __init__(self, members: list[discord.Member | DummyMember] | discord.Member):
        self.dealer_hand = Hand([])
        self.deck: Deck = Deck(size=6)

        if isinstance(members, discord.Member):
            members = [members]

        self.players = [self.Player(member=member, hands=[Hand([])]) for member in members]

    def deal_cards(self):

        if len(self.deck.cards) < len(self.players) * 5 + 5:
            return False

        for _ in range(2):
            for player in self.players:
                for hand in player.hands:
                    hand.cards.append(self.deck.deal())
            self.dealer_hand.cards.append(self.deck.deal())

        self.dealer_hand.cards[1].is_flipped = False

        return True

    def get_hand(self, user_id, hand_index=0) -> Hand | None:
        for player in self.players:
            if player.member.id == user_id:
                return player.hands[hand_index]
        return None

    def deal_card(self, hand: Hand):
        hand.cards.append(self.deck.deal())

    def deal_dealer(self, hit_on_soft_17=True):
        if self.dealer_hand.blackjack_value < 17 or (self.dealer_hand.blackjack_value <= 17 and self.dealer_hand.is_soft and hit_on_soft_17):
            self.dealer_hand.cards.append(self.deck.deal())
            return True
        return False

    def reset(self):
        for player in self.players:
            for hand in player.hands:
                hand.cards.clear()
        self.dealer_hand.cards.clear()

    def render_image(self, is_dealer_flipped: bool = False) -> Image.Image:

        def resize(img: Image.Image, img_scale):
            new_width = int(img.width * img_scale)
            new_height = int(img.height * img_scale)

            return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        @dataclasses.dataclass
        class RenderPlayerInfo:
            member: Member
            img: Image.Image
            bet: int

        normal_card_scale = 0.5

        dealer_padding_from_top = 50
        dealer_img = resize(self.dealer_hand.render_image(), normal_card_scale)

        background = TABLE_BACKGROUND.copy()
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype(BASE_DIR / "assets" / "fonts" / "arial.ttf", size=10)
        background_mid_width = background.width // 2
        background_mid_height = background.height // 2
        background.paste(dealer_img, (background_mid_width - dealer_img.width // 2, dealer_padding_from_top), dealer_img)

        players_info: list[RenderPlayerInfo] = []
        for player in self.players:
            for hand in player.hands:
                player_info = RenderPlayerInfo(
                    member=player.member,
                    img=resize(hand.render_image(), normal_card_scale),
                    bet=hand.bet
                )
                players_info.append(player_info)

        height_gap = 5
        card_size = 1
        while True:
            col_widths = []
            row_heights = []
            widths = []
            max_height = 0
            for data in players_info:
                new_height = data.img.height * card_size
                new_width = data.img.width * card_size
                if new_height > max_height:
                    max_height = new_height

                if sum(widths) + new_width > background.width:
                    col_widths.append(widths)
                    row_heights.append(max_height)
                    widths = []

                widths.append(new_width)

            col_widths.append(widths)
            row_heights.append(max_height)

            if sum(row_heights) > background_mid_height - height_gap * len(row_heights):
                card_size -= 0.05
            else:
                break

        total_hands_height = sum(row_heights) + height_gap * len(row_heights)

        starting_y = background_mid_height + (background_mid_height - total_hands_height) // 2
        img_index = 0
        for i, widths in enumerate(col_widths):
            starting_x = background_mid_width - sum(widths) // 2
            for width in widths:
                text_height = 5
                player_info = players_info[img_index]
                img = resize(player_info.img, card_size)

                background.paste(img, (int(starting_x), int(starting_y)), img)
                draw.text((starting_x + width //2, starting_y - text_height), f"{player_info.member.name[:int(width/6)]}: ${player_info.bet}", font=font, anchor="mm")

                starting_x += width
                img_index += 1
            starting_y += row_heights[i] + height_gap
        return background

class DummyMember:
    def __init__(self, id: int, name: str):
        self.name = name
        self.id = id
        self.bot = False
        self.mention = f"<@!{self.id}>"
        self.display_name = name

    def __str__(self):
        return self.display_name

if __name__ == "__main__":
    test_member_list = []
    member_num = 2
    for i in range(member_num):
        test_member = DummyMember(i, f"test{i}")
        test_member_list.append(test_member)

    blackjack = Blackjack(test_member_list)
    blackjack.deal_cards()
    for test_member in test_member_list:
        hand = blackjack.get_hand(test_member.id)
        for i in range(int(random.random() * 3)):
            blackjack.deal_card(hand)
    blackjack.deal_dealer()

    blackjack.render_image().show()
