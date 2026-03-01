# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
#
# SPDX-License-Identifier: MPL-2.0

import os
import json
import re
from dotenv import load_dotenv
import google.genai as genai
from supabase import create_client
from datetime import datetime, UTC
from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection

# Initialize WebUI and detection
ui = WebUI()
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)
# Load environment
load_dotenv()

# Supabase client
SUPABASE_URL = "https://tsuwporyrjercmuowqyn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzdXdwb3J5cmplcmNtdW93cXluIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIzNTMzMDEsImV4cCI6MjA4NzkyOTMwMX0.bKxa62sb5873KegZi5_yMKopablkNJSaw4N6gh3u45Q"
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

def upsert_recipe(category: str, recipe: dict):
    instructions = [{"time": s[0], "step": s[1]} for s in recipe.get("instructions", [])]
    try:
        sb.table("recipes").upsert({
            "category": category.lower(),
            "dish": recipe.get("dish", ""),
            "instructions": instructions,
            "storage_time": recipe.get("storageTime", 0)
        }, on_conflict="category").execute()
        print(f"Upserted recipe to Supabase: {category}")
    except Exception as e:
        print(f"Supabase upsert error: {e}")

# Preset recipe data
RECIPE_DATA = {
    "vegan": {
        "dish": "Crispy Sesame Tofu with Jasmine Rice",
        "instructions": [
            [15, "Press the extra-firm tofu between paper towels under a heavy weight to remove excess moisture."],
            [12, "Rinse jasmine rice until water runs clear, then simmer for 12 minutes in a lidded pot with a pinch of salt."],
            [None, "Cut tofu into cubes, toss in cornstarch and sea salt, and pan-fry in sesame oil until all sides are golden and crisp."],
            [None, "In a small saucepan, whisk together soy sauce, honey, rice vinegar, grated ginger, and toasted sesame oil."],
            [5, "Simmer the sauce for 5 minutes or until it reduces to a thick, glossy glaze."],
            [None, "Toss the crispy tofu in the glaze and serve over the fluffed rice, garnished with toasted sesame seeds and sliced scallions."]
        ],
        "storageTime": 3
    },
    "breakfast": {
        "dish": "Avocado Toast with Poached Egg",
        "instructions": [
            [None, "Thickly slice a loaf of sourdough and brush both sides with extra virgin olive oil."],
            [5, "Toast the bread in a 200°C oven for 5 minutes or until the edges are golden and the center is still slightly chewy."],
            [None, "In a bowl, mash a ripe avocado with lime juice, sea salt, red pepper flakes, and a hint of cumin."],
            [None, "Bring a pot of water with a splash of vinegar to a gentle simmer"],
            [3, "poach an egg for 3 minutes."],
            [None, "Spread the avocado generously on the toast, top with the poached egg, and garnish with thin radish slices and microgreens."]
        ],
        "storageTime": 1
    },
    "quickmeal": {
        "dish": "Simple One-Pot Tomato Basil Pasta",
        "instructions": [
            [1, "Finely mince garlic and sauté in olive oil in a large pan until fragrant."],
            [None, "Add a can of crushed tomatoes, dried oregano, salt, and pepper."],
            [10, "Simmer the sauce on low heat to thicken while you boil a pot of salted water."],
            [8, "Cook spaghetti or penne in the boiling water until al dente."],
            [None, "Drain pasta and toss directly into the sauce with a handful of fresh torn basil leaves and a sprinkle of parmesan."]
        ],
        "storageTime": 4
    }
}

# Initialize Gemini API for recipe generation
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None

# ============ MESSAGE HANDLERS ============

def record_sensor_samples(celsius: float):
    """Handle temperature sensor readings"""
    if celsius is None or not isinstance(celsius, (int, float)):
        print(f"Received invalid sensor samples: celsius={celsius}")
        return
    
    ui.send_message("temperature", message={
        "value": float(celsius),
        "timestamp": datetime.now(UTC).isoformat()
    })

def send_detections_to_ui(detections: dict):
    """Handle object detections"""
    for key, values in detections.items():
        for value in values:
            entry = {
                "content": key,
                "confidence": value.get("confidence"),
                "timestamp": datetime.now(UTC).isoformat()
            }
            ui.send_message("detection", message=entry)

def handle_recipe_request(recipe_name: str, difficulty: str = "medium"):
    """Handle recipe requests"""
    print("Handling Request")
    # Check preset recipes first
    if recipe_name.lower() in RECIPE_DATA:
        recipe = RECIPE_DATA[recipe_name.lower()]
        upsert_recipe(recipe_name, recipe)
        ui.send_message("recipe", message=recipe)
        return
    
    # Use Gemini API for custom recipes if available
    if not client:
        ui.send_message("recipe_error", message={
            "error": "Gemini API not configured",
            "message": "Please set GEMINI_API_KEY environment variable"
        })
        return
    
    if difficulty not in ["easy", "medium", "hard"]:
        difficulty = "medium"
    
    try:
        content = [
            {
                "role": "user",
                "parts": [{
                    "text": '''Given a tuple (food-item, difficulty: 'easy'|'medium'|'hard'), return a step-by-step recipe.
                    Easy difficulty should be quick and easy without rare ingredients.
                    Hard difficulty should be Gordon Ramsay level gourmet version.
                    Return valid JSON in structure:
                    {
                      "dish": "NAME",
                      "instructions": [
                        [time_in_minutes_or_null, "instruction_text"],
                        ...
                      ],
                      "storageTime": number_of_days
                    }
                    Return only raw JSON, no markdown wrapping.'''
                }]
            },
            {
                "role": "user",
                "parts": [{"text": f"({recipe_name}, {difficulty})"}]
            }
        ]
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content
        )
        
        parsed_recipe = parse_json(response.text)
        print("Sending back to application")
        upsert_recipe(recipe_name, parsed_recipe)
        ui.send_message("recipe", message=parsed_recipe)
        
    except Exception as e:
        ui.send_message("recipe_error", message={
            "error": str(type(e).__name__),
            "message": str(e)
        })

def parse_json(text: str) -> dict:
    """Extract and parse JSON from text"""
    match = re.match(r"\{.*\}", text, re.S)
    if not match:
        return {"error": "Invalid JSON response"}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        return {"error": f"JSON parsing failed: {str(e)}"}

def override_threshold(sid, threshold):
    """Handle confidence threshold override"""
    detection_stream.override_threshold(threshold)

# ============ REGISTER MESSAGE HANDLERS ============

ui.on_message("recipe_request", lambda sid, data: handle_recipe_request(data.get("recipe"), data.get("difficulty")))
ui.on_message("override_th", override_threshold)
detection_stream.on_detect_all(send_detections_to_ui)

# ui.on_message("api_call", process_api_call, data: dict)

# def process_api_call(data: dict):
#     """Handle API calls"""
#     ui.send_message("api_response", message=data)

# ============ RUN APPLICATION ============

App.run()


