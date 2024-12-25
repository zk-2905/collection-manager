from flask import Flask

app = Flask(__name__)

class Game:
    def __init__(self, title, genre, is_completed):
        self.title = title
        self.genre = genre
        self.is_completed= is_completed

        