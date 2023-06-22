import json

def load():
    try:
        with open("config.json","r") as file:
            return json.loads(file.read())
    except FileNotFoundError:
        return {
            "screenWidth": 960,
            "screenHeight": 540,
            
            "leftBorder": 0.1,
            "rightBorder": 0.9,
            "topBorder": 0.1,
            "bottomBorder": 0.9
        }

def save(config):
    with open("config.json","w") as file:
        file.write(json.dumps(config))