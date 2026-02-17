import requests
import time
import pandas as pd

# ==============================
# 🔑 CONFIGURATION
# ==============================

API_KEY = "api_key"  # <-- PASTE YOUR API KEY
REGION = "sea"  # use sea since it worked for you
MY_PUUID = "puuid"  # <-- your puuid

headers = {
    "X-Riot-Token": API_KEY
}

# ==============================
# 📋 MATCH IDS
# ==============================

match_ids = [
    "match_id"
]

# ==============================
# 🚀 FETCH MATCH DATA
# ==============================

all_rows = []

for match_id in match_ids:
    url = f"https://{REGION}.api.riotgames.com/tft/match/v1/matches/{match_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        match_data = response.json()
        game_info = match_data["info"]

        # Game-level info
        game_meta = {
            "match_id": match_id,
            "endOfGameResult": game_info.get("end_of_game_result"),
            "gameCreation": game_info.get("game_datetime"),
            "gameId": match_data.get("metadata", {}).get("match_id"),
            "game_datetime": game_info.get("game_datetime"),
            "game_length": game_info.get("game_length"),
            "game_version": game_info.get("game_version"),
            "game_variation": game_info.get("game_variation"),
            "mapId": game_info.get("map_id"),
            "queue_id": game_info.get("queue_id"),
            "tft_game_type": game_info.get("tft_game_type"),
            "tft_set_core_name": game_info.get("tft_set_core_name"),
            "tft_set_number": game_info.get("tft_set_number")
        }

        # Participant-level info
        for participant in game_info.get("participants", []):
            if participant.get("puuid") != MY_PUUID:
                continue  # skip anyone not you

            row = game_meta.copy()
            row.update({
                "puuid": participant.get("puuid"),
                "placement": participant.get("placement"),
                "level": participant.get("level"),
                "gold_left": participant.get("gold_left"),
                "last_round": participant.get("last_round"),
                "players_eliminated": participant.get("players_eliminated"),
                "time_eliminated": participant.get("time_eliminated"),
                "total_damage_to_players": participant.get("total_damage_to_players"),
                "win": participant.get("win"),
                "companion": str(participant.get("companion")),
                "traits": "; ".join(
                    [f"{t['name']}({t['num_units']})" for t in participant.get("traits", [])]
                ),
                "units": "; ".join(
                    [f"{u.get('character_id')}[{','.join(map(str, u.get('items', [])))}]" for u in participant.get("units", [])]
                )
            })

            all_rows.append(row)
            print(f"✅ Fetched {match_id} for your puuid")

    else:
        print(f"❌ Error {response.status_code} for {match_id}")

    # Rate limit protection
    time.sleep(1.2)

# ==============================
# 💾 SAVE TO CSV
# ==============================

df = pd.DataFrame(all_rows)
df.to_csv("my_tft_dataset.csv", index=False)

print(" DONE! Dataset saved as my_tft_dataset.csv")
