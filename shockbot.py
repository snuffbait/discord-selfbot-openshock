import json
import requests
import threading
import time
import discord
import re

with open("config.json", "r") as f:
    config = json.load(f)

url = "https://api.openshock.app/2/shockers/control"
headers = {
    "OpenShockToken": config["OpenShockToken"],
    "Content-Type": "application/json"
}

maxsingle = 30000
maxtotal = 600000

count = 0
lock = threading.Lock()

client = discord.Client(self_bot=True)


def sendshock(intensity, durationms):
    payload = {
        "shocks": [
            {
                "id": config["shock"]["id"],
                "intensity": intensity,
                "type": 1,
                "duration": durationms
            }
        ],
        "customName": config["shock"]["customName"]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        return False


def shock(intensity=None, duration=None):
    global count
    with lock:
        count += 1
        current = count

    intensitys = intensity if intensity is not None else config["shock"]["intensity"]
    totalms = duration if duration is not None else config["shock"]["duration"]

    print(f"[{current}] shock: {intensitys}% for {totalms / 1000:.2f}s")

    remaining = totalms
    success = True

    while remaining > 0:
        chunk = min(remaining, maxsingle)
        ok = sendshock(intensitys, chunk)
        if not ok:
            print(f"[{current}] failed to send shock chunk")
            success = False
            break
        remaining -= chunk
        if remaining > 0:
            time.sleep(chunk / 1000 + 0.05)

    return success


def asyncs(intensity=None, duration=None):
    threading.Thread(target=shock, args=(intensity, duration), daemon=True).start()


@client.event
async def on_ready():
    print("hint: this breaks discord tos so if you get banned womp womp")


@client.event
async def on_message(message):
    match = re.match(r'!shock (\d+)(?:\s+(\d+(?:\.\d+)?))?', message.content, re.IGNORECASE)
    if match:
        try:
            intensity = max(1, min(100, int(match.group(1))))

            duration = None
            if match.group(2):
                seconds = float(match.group(2))
                duration = int(max(0.1, min(600, seconds)) * 1000)

            totalms = duration if duration is not None else config["shock"]["duration"]
            totals = totalms / 1000

            threading.Thread(
                target=shock,
                args=(intensity, totalms),
                daemon=True
            ).start()

            reply = f"shocking at {intensity}% for {totals:.1f}s"

            if message.author == client.user:
                await message.edit(content=reply)
            else:
                await message.reply(reply)

        except Exception:
            pass


if __name__ == "__main__":
    discordtoken = input("token: ")
    client.run(discordtoken)
