from fastapi.testclient import TestClient
from robot_flower_princess.main import app
from robot_flower_princess.infrastructure.persistence.in_memory_game_repository import (
	InMemoryGameRepository,
)
from robot_flower_princess.domain.entities.position import Position
from robot_flower_princess.domain.entities.robot import Robot
from robot_flower_princess.domain.value_objects.direction import Direction
from robot_flower_princess.domain.entities.board import Board
from robot_flower_princess.domain.entities.game_history import GameHistory

client = TestClient(app)


def test_autoplay_end_to_end():
	repo = InMemoryGameRepository()
	# create a small solvable board
	robot = Robot(position=Position(0, 0), orientation=Direction.EAST)
	board = Board(rows=2, cols=2, robot=robot, princess_position=Position(1, 1))
	board.flowers = {Position(0, 1)}
	board.obstacles = set()
	board.initial_flower_count = len(board.flowers)

	game_id = "e2e-autoplay"
	repo.save(game_id, board)
	repo.save_history(game_id, GameHistory())

	# Temporarily override the app dependency to use our repo
	from robot_flower_princess.infrastructure.api.dependencies import get_game_repository

	# Save any existing override and set our test override
	original_override = app.dependency_overrides.get(get_game_repository)
	app.dependency_overrides[get_game_repository] = lambda: repo

	try:
		resp = client.post(f"/api/games/{game_id}/autoplay")
		assert resp.status_code == 200
		data = resp.json()
		assert "actions_taken" in data["message"] or "board" in data
	finally:
		# restore original override
		if original_override is None:
			app.dependency_overrides.pop(get_game_repository, None)
		else:
			app.dependency_overrides[get_game_repository] = original_override
