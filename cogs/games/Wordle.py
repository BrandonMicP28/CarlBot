import io
import json
import random
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parents[2]
with open(BASE_DIR / "assets" / "data" / "answer_list.json") as f:
    ANSWER_LIST = json.load(f)
with open(BASE_DIR / "assets" / "data" / "word_list.json") as f:
    WORD_LIST = set(word.upper() for word in json.load(f))
    for ans in ANSWER_LIST:
        WORD_LIST.add(ans)

def generate_answer():
    answer = random.choice(ANSWER_LIST)
    return answer.upper()

def verify_guess(guess):
    if len(guess) != 5:
        return False

    if guess.upper().strip() in WORD_LIST:
        return True
    return False


class Wordle:
    def __init__(self, max_guesses: int):
        self.max_guesses = max_guesses
        self.answer = generate_answer()
        self.guesses = []
        self.letter_responses = {letter: "unknown" for letter in "QWERTYUIOPASDFGHJKLZXCVBNM"}
        self.game_state = "ongoing"

    def make_guess(self, guess):
        if not verify_guess(guess) or self.game_state != "ongoing":
            return False

        guess = guess.upper().strip()
        letters_of_answer = Counter(self.answer)

        guess_response = []
        for letter in guess:
            guess_response.append([letter, "wrong"])
            if self.letter_responses.get(letter, "invalid") == "unknown":
                self.letter_responses[letter] = "wrong"

        for i in range(5):
            if guess[i] == self.answer[i]:
                guess_response[i][1] = "known"
                self.letter_responses[guess[i]] = "known"
                letters_of_answer[guess[i]] -= 1

        for i in range(5):
            if letters_of_answer.get(guess[i], 0) > 0 and guess_response[i][1] != "known":
                guess_response[i][1] = "misplaced"
                letters_of_answer[guess[i]] -= 1
                if self.letter_responses.get(guess[i], "invalid") == "wrong":
                    self.letter_responses[guess[i]] = "misplaced"

        self.guesses.append(guess_response)
        if guess == self.answer:
            self.game_state = "won"
        elif len(self.guesses) >= self.max_guesses:
             self.game_state = "lost"
        return True

    def set_answer(self, answer):
        """
        A method that replaces the old answer with a new one. This will rewrite the old guess responses
        :param answer: Wordle answer
        :return:
        """
        self.letter_responses = {letter: "unknown" for letter in "QWERTYUIOPASDFGHJKLZXCVBNM"}
        self.answer = answer
        old_guesses = ["".join(letter[0] for letter in guess) for guess in self.guesses]
        self.guesses = []

        for guess in old_guesses:
            self.make_guess(guess)

    def generate_wordle_image(self):

        def print_guesses(start_x, start_y):
            square_size = 50
            gap = 5

            for row in range(self.max_guesses):
                for col in range(len(self.answer)):
                    absolute_x = start_x + col * (square_size + gap)
                    absolute_y = start_y + row * (square_size + gap)

                    if len(self.guesses) > row:
                        guess_color = skin.get(self.guesses[row][col][1])
                    else:
                        guess_color = skin.get("unknown")

                    draw.rectangle([absolute_x, absolute_y, absolute_x + square_size, absolute_y + square_size], fill=f"#{guess_color}")

                    if len(self.guesses) > row:
                        guess_letter = self.guesses[row][col][0]
                        draw.text((absolute_x + square_size / 2, absolute_y + square_size / 2), guess_letter, font=font, fill="white", anchor="mm")

        background = Image.new("RGBA", (1000, 1000))
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype(BASE_DIR / "assets" / "fonts" / "arial.ttf", 20)
        skin = {"unknown": "D3D6DA", "wrong": "787C7E", "misplaced": "C9B458", "known": "6AAA64"}
        print_guesses(0, 0)

        buffer = io.BytesIO()
        background.save(buffer, format="PNG")
        buffer.seek(0)
        background.show()
        return buffer.read()

