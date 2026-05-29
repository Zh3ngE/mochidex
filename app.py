import os
import logging
import requests
from flask import Flask, render_template, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix


# Setup

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret")

app.wsgi_app = ProxyFix(app.wsgi_app)

POKEMON_API = "https://api.pokemontcg.io/v2"
API_KEY = os.environ.get("POKEMON_TCG_API_KEY", "")

HEADERS = {"X-Api-Key": API_KEY}

# Pages

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/wishlist")
def wishlist():
    return render_template("wishlist.html")


@app.route("/favorites")
def favorites():
    return render_template("favorites.html")

# API: Search Cards

@app.route("/api/search")
def search_cards():
    query = request.args.get("q", "")
    filter_type = request.args.get("filter", "name")
    rarity = request.args.get("rarity", "")

    try:
        # base query
        if filter_type == "number":
            q = f"number:{query}"
        elif filter_type == "set":
            q = f'set.name:"{query}*"'
        else:
            q = f'name:"{query}*"'

        # rarity filter
        if rarity:
            rarity_map = {
                "ex": "name:*ex",
                "gx": "name:*GX",
                "v": "name:*V",
                "fullart": 'rarity:"Illustration Rare"',
                "holo": 'rarity:"Rare Holo"',
                "trainer": "supertype:Trainer",
            }
            q += " " + rarity_map.get(rarity, "")

        r = requests.get(
            f"{POKEMON_API}/cards",
            headers=HEADERS,
            params={"q": q, "pageSize": 20},
            timeout=30,
        )

        r.raise_for_status()
        return jsonify(r.json())

    except requests.RequestException as e:
        logging.error(f"Search error: {e}")
        return jsonify({"error": "API failed", "data": []}), 500

# API: Single Card

@app.route("/api/card/<card_id>")
def get_card(card_id):
    try:
        r = requests.get(
            f"{POKEMON_API}/cards/{card_id}",
            headers=HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        return jsonify(r.json())

    except requests.RequestException as e:
        logging.error(f"Card fetch error: {e}")
        return jsonify({"error": "Card fetch failed"}), 500

# API: Sets

@app.route("/api/sets")
def get_sets():
    try:
        r = requests.get(
            f"{POKEMON_API}/sets",
            headers=HEADERS,
            params={"orderBy": "-releaseDate", "pageSize": 50},
            timeout=15,
        )
        r.raise_for_status()
        return jsonify(r.json())

    except requests.RequestException as e:
        logging.error(f"Sets error: {e}")
        return jsonify({"error": "Sets fetch failed", "data": []}), 500

# Run

if __name__ == "__main__":
    app.run(debug=True)