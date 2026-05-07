import json
import requests
import threading
import discord
import re

with open("config.json", "r") as f:
    config = json.load(f)

url = "https://api.openshock.app/2/shockers/control"
headers = {
    "OpenShockToken": config["OpenShockToken"],
    "Content-Type": "application/json"
}

count = 0
lock = threading.Lock()

client = discord.Client(self_bot=True)


def shock(intensity=None, duration=None):
    global count
    with lock:
        count += 1
        count = count

    intensitys = intensity if intensity is not None else config["shock"]["intensity"]
    durations = duration if duration is not None else config["shock"]["duration"]

    payload = {
        "shocks": [
            {
                "id": config["shock"]["id"],
                "intensity": intensitys,
                "type": 1,
                "duration": durations
            }
        ],
        "customName": config["shock"]["customName"]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=3)
        response.raise_for_status()
        print(f"[{count}] Shock: {payload['shocks'][0]['intensity']}% for {payload['shocks'][0]['duration'] / 1000:.2f}s")
        return True
    except Exception as e:
        print(f"[{count}] Failed to send shock: {e}")
        return False


def asyncs(intensity=None, duration=None):
    threading.Thread(target=shock, args=(intensity, duration), daemon=True).start()


@client.event
async def on_ready():
    print("hint: this breaks discord tos so if you get banned womp womp")


@client.event
async def on_message(message):


    match = re.match(r'!shock (\d+)(?:\s+(\d+))?', message.content, re.IGNORECASE)
    if match:
        try:
            intensity = max(1, min(100, int(match.group(1))))

            duration = None
            if match.group(2):
                duration = max(100, min(30000, int(match.group(2)) * 1000))

            success = shock(intensity, duration)

            if success:
                durations = duration / 1000 if duration else config["shock"]["duration"] / 1000
                if message.author == client.user:
                    await message.edit(content=f"Shocking at {intensity}% for {durations:.1f}s")
                else:
                    await message.reply(f"Shocking at {intensity}% for {durations:.1f}s")
        except Exception as e:
            print("yea i aint fixing this error")



if __name__ == "__main__":
    discord_token = input("token: ")
    client.run(discord_token)