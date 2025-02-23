# server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import random
from typing import Dict, List, Optional
import uvicorn

app = FastAPI()


# Data Models
class Item(BaseModel):
    name: str
    price: int


class Player(BaseModel):
    nickname: str
    credits: int
    owned_items: List[str]


# Game Configuration
CREDIT_BONUS_RANGE = (100, 1000)  # Random credits given on login
SAVE_FILE = "game_data.json"

# Game Data
game_data = {
    "items": {
        "laser_sword": {"name": "Laser Sword", "price": 500},
        "shield_generator": {"name": "Shield Generator", "price": 750},
        "stealth_device": {"name": "Stealth Device", "price": 1000},
        "repair_bot": {"name": "Repair Bot", "price": 850},
        "power_crystal": {"name": "Power Crystal", "price": 300}
    },
    "players": {}
}


# Data persistence functions
def save_game_data():
    with open(SAVE_FILE, 'w') as f:
        json.dump(game_data, f)


def load_game_data():
    try:
        with open(SAVE_FILE, 'r') as f:
            global game_data
            game_data = json.load(f)
    except FileNotFoundError:
        save_game_data()  # Create initial file if it doesn't exist


# Load data on startup
load_game_data()


# API Endpoints
@app.get("/items")
async def get_items():
    """Return all available items in the game."""
    return game_data["items"]


@app.post("/login/{nickname}")
async def login(nickname: str):
    """Handle player login, create new account if needed."""
    if nickname not in game_data["players"]:
        # Create new player
        game_data["players"][nickname] = {
            "nickname": nickname,
            "credits": 1000,  # Starting credits
            "owned_items": []
        }
        save_game_data()

    # Add random credit bonus
    bonus = random.randint(CREDIT_BONUS_RANGE[0], CREDIT_BONUS_RANGE[1])
    game_data["players"][nickname]["credits"] += bonus
    save_game_data()

    return {
        "player": game_data["players"][nickname],
        "bonus_credits": bonus
    }


@app.post("/buy/{nickname}/{item_id}")
async def buy_item(nickname: str, item_id: str):
    """Handle item purchase."""
    if nickname not in game_data["players"]:
        raise HTTPException(status_code=404, detail="Player not found")
    if item_id not in game_data["items"]:
        raise HTTPException(status_code=404, detail="Item not found")

    player = game_data["players"][nickname]
    item = game_data["items"][item_id]

    if item_id in player["owned_items"]:
        raise HTTPException(status_code=400, detail="Item already owned")
    if player["credits"] < item["price"]:
        raise HTTPException(status_code=400, detail="Insufficient credits")

    player["credits"] -= item["price"]
    player["owned_items"].append(item_id)
    save_game_data()

    return player


@app.post("/sell/{nickname}/{item_id}")
async def sell_item(nickname: str, item_id: str):
    """Handle item sale."""
    if nickname not in game_data["players"]:
        raise HTTPException(status_code=404, detail="Player not found")
    if item_id not in game_data["items"]:
        raise HTTPException(status_code=404, detail="Item not found")

    player = game_data["players"][nickname]
    item = game_data["items"][item_id]

    if item_id not in player["owned_items"]:
        raise HTTPException(status_code=400, detail="Item not owned")

    sell_price = item["price"] // 2  # Sell for half the purchase price
    player["credits"] += sell_price
    player["owned_items"].remove(item_id)
    save_game_data()

    return player


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
