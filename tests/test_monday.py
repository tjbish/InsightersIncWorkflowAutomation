from __future__ import annotations

import os

import pytest
import requests


def test_dev_monday_token_and_board_are_reachable():
    token = os.environ.get("DEV_MONDAY_API")
    board_id = os.environ.get("DEV_MONDAY_BOARD_ID")
    if not token or not board_id:
        pytest.skip("DEV_MONDAY_API and DEV_MONDAY_BOARD_ID are required for monday integration tests.")

    response = requests.post(
        "https://api.monday.com/v2",
        headers={
            "Authorization": token,
            "Content-Type": "application/json",
            "API-Version": os.environ.get("MONDAY_API_VERSION", "2024-04"),
        },
        json={
            "query": "query ($board_id: [ID!]) { boards(ids: $board_id) { id name } }",
            "variables": {"board_id": [str(board_id)]},
        },
        timeout=30,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert "errors" not in payload, payload
    boards = payload.get("data", {}).get("boards", [])
    assert boards, payload
    assert str(boards[0]["id"]) == str(board_id)
