from flask import Flask, render_template, request, redirect, url_for
import json
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

class Game:
    def __init__(self, title, genre, is_completed):
        self.title = title
        self.genre = genre
        self.is_completed = is_completed

class CollectionManager:
    def __init__(self):
        self.games = []

    def add_game(self, title, genre, is_completed):
        game = Game(title, genre, is_completed)
        self.games.append(game)
        self.save_games()

    def delete_game(self, title):
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
                self.games = [Game(**game_data) for game_data in games_data]
        except FileNotFoundError:
            pass

class GameRecommender:
    @staticmethod
    def get_recommendations(genre):
        games = []
        tagids = {'action': 19, 'adventure': 21, 'racing': 9, 'rpg': 122, 'sports': 15} # steam genre id
        url = "https://store.steampowered.com/search/?filter=topsellers"
        response = requests.get(url)

        if response.status_code != 200:
            return ["Unable to fetch recommendations at this time."]

        soup = BeautifulSoup(response.text, 'html.parser')

        for game in soup.select(".search_result_row"):
            title = game.select_one(".title").text.strip()
            game_genre = game.get("data-ds-tagids", "").lower()
            new_game_genre = []
            number = ''
            for num in game_genre[1:-1]:
                if num != ',':
                    number += num
                elif num == ',':
                    new_game_genre.append(number)
                    number = ''
            for id in new_game_genre:
                if tagids[genre] == int(id):
                    games.append(title)

            if len(games) >= 5:  # Limit to top 5 recommendations
                break

        return games if games else ["No recommendations found for this genre."]

collection_manager = CollectionManager() # create collection object
collection_manager.load_games() # load previous data

@app.route("/")
def index():
    genre = request.args.get("genre", "any")
    completed = request.args.get("completed", "any")

    if completed.lower() == "any":
        completed = None
    else:
        completed = completed.lower() == "true"

    games = collection_manager.filter_games(genre=genre, completed=completed)

    recommendations = []
    if genre.lower() != "any": # only give recommendations when filtering a specific genre
        recommendations = GameRecommender.get_recommendations(genre)
        print(recommendations)

    return render_template("index.html", games=games, genres=["any", "action", "adventure", "racing", "rpg", "sports"], recommendations=recommendations)

@app.route("/add", methods=["POST"])
def add_game():
    title = request.form.get("title")
    genre = request.form.get("genre")
    is_completed = request.form.get("is_completed") == "true"
    valid_genres = ["action", "adventure", "racing", "rpg", "sports"]

    if genre.lower() not in valid_genres:
        return redirect(url_for("index", error="Invalid genre"))
    
    collection_manager.add_game(title, genre.title(), is_completed)
    return redirect(url_for("index"))

@app.route("/delete/<title>", methods=["POST"])
def delete_game(title):
    collection_manager.delete_game(title)
    return redirect(url_for("index"))

@app.route("/edit/<title>", methods=["POST"])
def edit_game(title):
    new_title = request.form.get("title")
    new_genre = request.form.get("genre")
    new_is_completed = request.form.get("is_completed") == "true"
    valid_genres = ["action", "adventure", "racing", "rpg", "sports"]

    if new_genre.lower() not in valid_genres:
        return redirect(url_for("index", error="Invalid genre"))
        
    collection_manager.edit_game(title, new_title, new_genre, new_is_completed)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)