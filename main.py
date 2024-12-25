from flask import Flask
import json

app = Flask(__name__)

class Game:
    def __init__(self, title, genre, is_completed):
        self.title = title
        self.genre = genre
        self.is_completed= is_completed

class CollectionManager:
    def __init__(self):
        self.games = []
    
    def add_games(self,title, genre, is_completed):
        game = Game(title, genre, is_completed)
        self.games.append(game)
        self.save_games()
    
    def delete_games(self, title):
        self.games = [game for game in self.games if game.title != title]
        self.save_games()

    def edit_game(self, title, new_title, new_genre, new_is_completed):
        for game in self.games:
            if game.title == title:
                game.title = new_title
                game.genre = new_genre
                game.is_completed = new_is_completed
                self.save_games()
                return
    
    def filter_games(self, genre=None, completed=None):
        filtered = self.games
        if genre and genre.lower() != "any":
            filtered = [game for game in filtered if game.genre.lower() == genre.lower()]
        if completed is not None:
            filtered = [game for game in filtered if game.is_completed == completed]
        return filtered

    def save_games(self):
        with open("games.json", "w") as f:
            json.dump([game.__dict__ for game in self.games], f)
    
    def load_games(self):
        try:
            with open("games.json", "r") as f:
                games_data = json.load(f)
                self.games = [Game(**games_data) for game_data in games_data]
        except FileNotFoundError:
            pass