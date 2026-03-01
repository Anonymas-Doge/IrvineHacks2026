import os
import requests
import flask
from flask_cors import CORS
from dotenv import load_dotenv
import google.genai as genai
import json
import re
import time

BREAKFAST_DATA = '''{
"dish": "Avocado Toast with Poached Egg",
"instructions": [
    [null, "Thickly slice a loaf of sourdough and brush both sides with extra virgin olive oil."],
    [5, "Toast the bread in a 200°C oven for 5 minutes or until the edges are golden and the center is still slightly chewy."],
    [null, "In a bowl, mash a ripe avocado with lime juice, sea salt, red pepper flakes, and a hint of cumin."],
    [null, "Bring a pot of water with a splash of vinegar to a gentle simmer"],
    [3, "poach an egg for 3 minutes."],
    [null, "Spread the avocado generously on the toast, top with the poached egg, and garnish with thin radish slices and microgreens."]
],
"storageTime": 1
}'''

VEGAN_DATA = '''{
"dish": "Crispy Sesame Tofu with Jasmine Rice",
"instructions": [
[15, "Press the extra-firm tofu between paper towels under a heavy weight to remove excess moisture."],
[12, "Rinse jasmine rice until water runs clear, then simmer for 12 minutes in a lidded pot with a pinch of salt."],
[null, "Cut tofu into cubes, toss in cornstarch and sea salt, and pan-fry in sesame oil until all sides are golden and crisp."],
[null, "In a small saucepan, whisk together soy sauce, honey, rice vinegar, grated ginger, and toasted sesame oil."],
[5, "Simmer the sauce for 5 minutes or until it reduces to a thick, glossy glaze."],
[null, "Toss the crispy tofu in the glaze and serve over the fluffed rice, garnished with toasted sesame seeds and sliced scallions."]
],
"storageTime": 3
}'''

QUICK_MEAL_DATA = """{
"dish": "Simple One-Pot Tomato Basil Pasta",
"instructions": [
[1, "Finely mince garlic and sauté in olive oil in a large pan until fragrant."],
[null, "Add a can of crushed tomatoes, dried oregano, salt, and pepper."],
[10, "Simmer the sauce on low heat to thicken while you boil a pot of salted water."],
[8, "Cook spaghetti or penne in the boiling water until al dente."],
[null, "Drain pasta and toss directly into the sauce with a handful of fresh torn basil leaves and a sprinkle of parmesan."]
],
"storageTime": 4
}"""

FAKE_DATA = """{
	"dish": "Spaghetti and Meatballs",
	"instructions": [
		[
			null,
			"In a large bowl, combine 1 lb ground beef, 1/2 cup plain breadcrumbs, 1 large egg, 1 tsp garlic powder, 1 tsp onion powder, 1/2 tsp salt, 1/4 tsp black pepper, and 1/2 tsp dried oregano. Mix gently until just combined, being careful not to overmix."
		],
		[
			null,
			"Form the mixture into approximately 16-20 small meatballs."
		],
		[
			null,
			"Heat 1 tbsp olive oil in a large pot or deep skillet over medium-high heat. Add the meatballs and brown them on all sides, about 5-7 minutes. You don't need to cook them through."
		],
		[
			null,
			"Pour in one 24-oz jar of your favorite marinara sauce. Stir gently to coat the meatballs."
		],
		[
			15,
			"Bring the sauce to a gentle simmer, then reduce heat to low, cover, and let it cook for 15 minutes."
		],
		[
			null,
			"While the sauce simmers, bring a large pot of salted water to a rolling boil."
		],
		[
			9,
			"Add 12 oz spaghetti to the boiling water and cook according to package directions, typically 8-10 minutes, until al dente."
		],
		[
			null,
			"Carefully drain the cooked spaghetti."
		],
		[
			null,
			"Serve the spaghetti topped with meatballs and marinara sauce. Garnish with grated Parmesan cheese if desired."
		]
	],
	"storageTime": 4
}"""

load_dotenv() # load env file


# ------- UN-COMMENT OUT WHEN WE USE THE REAL API --------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY: raise RuntimeError("GEMINI API KEY NOT SET!")
client = genai.Client(api_key=GEMINI_API_KEY)

RECIPE_URL = "https://recipe-api.com/api/v1/recipes"

app = flask.Flask(__name__)
CORS(app)

@app.route("/chat", methods=["GET"])
def chat():
    # time.sleep(4) # simulating time for
    
    
    
    recipe = flask.request.args.get("q")
    difficulty = flask.request.args.get("difficulty")

    if (recipe == "vegan"):
        return flask.jsonify(
            parse_json(VEGAN_DATA)
        )
    elif recipe == "breakfast":
        return flask.jsonify(
            parse_json(BREAKFAST_DATA)
        )
    elif recipe == "quickmeal":
        return flask.jsonify(
            parse_json(QUICK_MEAL_DATA)
        )

    content = []
    content.append({
        "role": "user",
        "parts": [
            {
                "text":
                '''given a tuple (food-item, difficulty: 'easy'|'medium'|'hard'), return a step by step recipe for it.
                easy difficulty should be a quick easy recipe without rare ingredents.
                hard difficulty should be gordan ramsey level gormet version of recipe.
                You should return In a valid JSON form in the structure:
                \\{
                  dish: NAME_OF_DISH,
                  instructions: [
                    [time, instruction],
                    [time, instruction]
                  ]
                  storageTime: NUMBER_OF_DAYS_BEFORE_FOOD_GOES_BAD
                \\}
                time should be in minutes, and only appear if it is time where the cooker can step away from the kitchen (i.e. 30: int, if instruction is "boil for 30 minutes)
                if not, time can be null.
                return nothing else but the raw json, (do not have it wrapped in a markdown block it should go through json.loads() in python w/o error)
                ''' 
            }
        ]
    })
    content.append({
        "role": "user",
        "parts": [{"text":f"({recipe}, {difficulty})"}]
    })

    if not recipe:
        flask.abort(400, "Missing 'dish'")
    if not difficulty in ["easy", "medium", "hard"]:
        flask.abort(400, "Invalid Difficulty")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content
        )

        parsed_text = response.text[8:-3]
        print("response:\n", parsed_text)
        return flask.jsonify(
            parse_json(parsed_text)
        )

    except Exception as e:
        flask.abort(500, str(e))

# returns id of first recipe that fits query
@app.route("/getRecipe")
def parse_recipe(data):
    item_name = data["data"]["name"]
    instructions = []
    for i in data["data"]["instructions"]:
        text = i["text"]
        duration = i["structured"]["duration"] if i["structured"]["duration"] else None
        action = i["structured"]["action"] if i["structured"]["action"] else None
        temperature = i["structured"]["temperature"]["fahrenheit"] if i["structured"]["temperature"]["fahrenheit"] else None
        instructions.append((text, action, duration,  temperature))
    #return instructions
def get_recipe():
    query_string = flask.request.args.get("q")
    res = requests.get(f"{RECIPE_URL}?q={query_string}", headers={
     "Content-Type": "application/json",
     "X-API-Key": os.getenv("API_KEY")
    })
    print(os.getenv("API_KEY"))
    print("RES")
    print(res)
    if not res.ok: flask.abort(500, "could not get data from recipes api")
    if len(res.json()["data"]) == 0: flask.abort(400, "given query is not a valid recipe in the api")

    return res.json()["data"][0]["id"]

@app.route("/getInstruction/<id>")
def get_instruction(id="06ff1c50-c861-4585-a575-4ad9b9dd9707"):
    res = requests.get(f"{RECIPE_URL}/{id}", headers={
     "Content-Type": "application/json",
     "X-API-Key": os.getenv("API_KEY")
    })

    if not res.ok: flask.abort(500, "could not get data from recipes api")

    return res.json()

def parse_json(text):
    match = re.match(r"\{.*\}", text, re.S)
    if not match: return {"error":"not a valid json"}
    return json.loads(match.group(0))

if __name__ == "__main__":
    app.run(debug=True, port=5001)

