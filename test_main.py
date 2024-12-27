import unittest
from unittest.mock import patch, MagicMock
from main import Game, CollectionManager, GameRecommender

class TestGame(unittest.TestCase):
    def test_game_initialization(self):
        game = Game("Test Game", "Action", True)
        self.assertEqual(game.title, "Test Game")
        self.assertEqual(game.genre, "Action")
        self.assertTrue(game.is_completed)

class TestCollectionManager(unittest.TestCase):
    def setUp(self):
        self.manager = CollectionManager()
        self.manager.games = []

    def test_add_game(self):
        self.manager.add_game("Game 1", "Action", False)
        self.assertEqual(len(self.manager.games), 1)
        self.assertEqual(self.manager.games[0].title, "Game 1")

    def test_delete_game(self):
        self.manager.add_game("Game 1", "Action", False)
        self.manager.delete_game("Game 1")
        self.assertEqual(len(self.manager.games), 0)

    def test_edit_game(self):
        self.manager.add_game("Game 1", "Action", False)
        self.manager.edit_game("Game 1", "New Game 1", "Adventure", True)
        game = self.manager.games[0]
        self.assertEqual(game.title, "New Game 1")
        self.assertEqual(game.genre, "Adventure")
        self.assertTrue(game.is_completed)

    def test_filter_games_by_genre(self):
        self.manager.add_game("Game 1", "Action", False)
        self.manager.add_game("Game 2", "Adventure", True)
        filtered = self.manager.filter_games(genre="Action")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].title, "Game 1")

    def test_filter_games_by_completion(self):
        self.manager.add_game("Game 1", "Action", False)
        self.manager.add_game("Game 2", "Adventure", True)
        filtered = self.manager.filter_games(completed=True)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].title, "Game 2")

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_save_games(self, mock_open):
        self.manager.add_game("Game 1", "Action", False)
        self.manager.save_games()
        mock_open.assert_called_with("games.json", "w")

    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data='[{"title": "Game 1", "genre": "Action", "is_completed": false}]')
    def test_load_games(self, mock_open):
        self.manager.load_games()
        self.assertEqual(len(self.manager.games), 1)
        self.assertEqual(self.manager.games[0].title, "Game 1")

class TestGameRecommender(unittest.TestCase):
    @patch("requests.get")
    def test_get_recommendations_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <div class="search_result_row" data-ds-tagids="[19,21]">
            <span class="title">Game 1</span>
        </div>
        <div class="search_result_row" data-ds-tagids="[21]">
            <span class="title">Game 2</span>
        </div>
        '''
        mock_get.return_value = mock_response

        recommendations = GameRecommender.get_recommendations("action")
        self.assertEqual(len(recommendations), 1)
        self.assertIn("Game 1", recommendations)


    @patch("requests.get")
    def test_get_recommendations_no_matches(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ''
        mock_get.return_value = mock_response

        recommendations = GameRecommender.get_recommendations("action")
        self.assertEqual(recommendations, ["No recommendations found for this genre."])

    @patch("requests.get")
    def test_get_recommendations_failure(self, mock_get):
        mock_get.return_value.status_code = 500
        recommendations = GameRecommender.get_recommendations("action")
        self.assertEqual(recommendations, ["Unable to fetch recommendations at this time."])

if __name__ == "__main__":
    unittest.main()
