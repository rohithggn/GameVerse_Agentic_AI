import os
# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, jsonify, session
# pyrefly: ignore [missing-import]
from groq import Groq
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "gameverse-fallback-secret")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are GameVerse AI, an expert gaming assistant and game recommender. You help users discover amazing games across all genres, provide gaming tips, tutorials, and personalized recommendations.

Your personality:
- Enthusiastic and knowledgeable about games
- You cover all platforms: PC, Console, Mobile
- You recommend games with brief descriptions and why someone would enjoy them
- You can suggest games based on genre, mood, playstyle, or similar games
- You provide helpful gaming tips and beginner guides
- When recommending games, mention the genre and platform availability
- Keep responses concise but informative (2-3 paragraphs max)
- Use gaming terminology naturally
- If asked about non-gaming topics, gently steer back to gaming

Always format game titles in bold when mentioning them."""

# Curated game data with real image links
GAMES_DATA = {
    "action": {
        "name": "Action",
        "icon": "⚔️",
        "description": "Fast-paced combat, explosions, and adrenaline-pumping gameplay",
        "color": "#ff4444",
        "games": [
            {
                "title": "Fortnite",
                "description": "Battle royale with building mechanics. Free-to-play with constant updates and events.",
                "platform": "PC, Console, Mobile",
                "rating": 4.5,
                "link": "https://www.epicgames.com/fortnite/en-US/download",
                "image_url": "https://cdn2.unrealengine.com/fortnite-battle-royale-chapter-4-season-2-mega-1920x1080-87a3cb2f9dd2.jpg"
            },
            {
                "title": "Apex Legends",
                "description": "Squad-based battle royale with unique character abilities and fast movement.",
                "platform": "PC, Console",
                "rating": 4.6,
                "link": "https://store.steampowered.com/app/1172470/Apex_Legends/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1172470/header.jpg"
            },
            {
                "title": "DOOM Eternal",
                "description": "Rip and tear through hordes of demons in this intense first-person shooter.",
                "platform": "PC, Console",
                "rating": 4.8,
                "link": "https://store.steampowered.com/app/782330/DOOM_Eternal/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/782330/header.jpg"
            },
            {
                "title": "Devil May Cry 5",
                "description": "Stylish action combat with three playable characters and incredible combos.",
                "platform": "PC, Console",
                "rating": 4.7,
                "link": "https://store.steampowered.com/app/601150/Devil_May_Cry_5/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/601150/header.jpg"
            }
        ]
    },
    "adventure": {
        "name": "Adventure",
        "icon": "🗺️",
        "description": "Explore vast worlds, uncover mysteries, and embark on epic journeys",
        "color": "#44bb44",
        "games": [
            {
                "title": "The Witcher 3: Wild Hunt",
                "description": "Open-world RPG adventure with rich storytelling and meaningful choices.",
                "platform": "PC, Console, Switch",
                "rating": 4.9,
                "link": "https://store.steampowered.com/app/292030/The_Witcher_3_Wild_Hunt/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/292030/header.jpg"
            },
            {
                "title": "Red Dead Redemption 2",
                "description": "Epic tale of outlaws in the American frontier with stunning open world.",
                "platform": "PC, Console",
                "rating": 4.9,
                "link": "https://store.steampowered.com/app/1174180/Red_Dead_Redemption_2/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1174180/header.jpg"
            },
            {
                "title": "Uncharted 4",
                "description": "Cinematic adventure following Nathan Drake on his greatest treasure hunt.",
                "platform": "PC, PlayStation",
                "rating": 4.8,
                "link": "https://store.steampowered.com/app/1659420/UNCHARTED_Legacy_of_Thieves_Collection/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1659420/header.jpg"
            },
            {
                "title": "Horizon Zero Dawn",
                "description": "Hunt robotic creatures in a beautiful post-apocalyptic open world.",
                "platform": "PC, PlayStation",
                "rating": 4.7,
                "link": "https://store.steampowered.com/app/1151640/Horizon_Zero_Dawn_Complete_Edition/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1151640/header.jpg"
            }
        ]
    },
    "rpg": {
        "name": "RPG",
        "icon": "🧙",
        "description": "Level up, craft your story, and become the hero of your own tale",
        "color": "#9944ff",
        "games": [
            {
                "title": "Elden Ring",
                "description": "Massive open-world action RPG by FromSoftware and George R.R. Martin.",
                "platform": "PC, Console",
                "rating": 4.9,
                "link": "https://store.steampowered.com/app/1245620/ELDEN_RING/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1245620/header.jpg"
            },
            {
                "title": "Baldur's Gate 3",
                "description": "D&D-based CRPG with unparalleled freedom and deep narrative choices.",
                "platform": "PC, PlayStation",
                "rating": 4.9,
                "link": "https://store.steampowered.com/app/1086940/Baldurs_Gate_3/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1086940/header.jpg"
            },
            {
                "title": "Final Fantasy XVI",
                "description": "Action-driven Final Fantasy with spectacular combat and an epic story.",
                "platform": "PC, PlayStation",
                "rating": 4.6,
                "link": "https://store.steampowered.com/app/1642170/FINAL_FANTASY_XVI/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1642170/header.jpg"
            },
            {
                "title": "Persona 5 Royal",
                "description": "Stylish turn-based JRPG blending high school life with supernatural adventures.",
                "platform": "PC, Console",
                "rating": 4.8,
                "link": "https://store.steampowered.com/app/1687950/Persona_5_Royal/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1687950/header.jpg"
            }
        ]
    },
    "strategy": {
        "name": "Strategy",
        "icon": "♟️",
        "description": "Outsmart opponents with tactical thinking and resource management",
        "color": "#ffaa00",
        "games": [
            {
                "title": "Civilization VI",
                "description": "Build an empire from the ground up spanning thousands of years of history.",
                "platform": "PC, Console, Mobile",
                "rating": 4.7,
                "link": "https://store.steampowered.com/app/289070/Sid_Meiers_Civilization_VI/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/289070/header.jpg"
            },
            {
                "title": "Age of Empires IV",
                "description": "Real-time strategy set across medieval civilizations with epic battles.",
                "platform": "PC",
                "rating": 4.5,
                "link": "https://store.steampowered.com/app/1466860/Age_of_Empires_IV/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1466860/header.jpg"
            },
            {
                "title": "XCOM 2",
                "description": "Turn-based tactical combat against alien invaders with permadeath stakes.",
                "platform": "PC, Console",
                "rating": 4.6,
                "link": "https://store.steampowered.com/app/268500/XCOM_2/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/268500/header.jpg"
            },
            {
                "title": "Total War: Warhammer III",
                "description": "Massive fantasy battles combining real-time tactics and turn-based strategy.",
                "platform": "PC",
                "rating": 4.5,
                "link": "https://store.steampowered.com/app/1142710/Total_War_WARHAMMER_III/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1142710/header.jpg"
            }
        ]
    },
    "puzzle": {
        "name": "Puzzle",
        "icon": "🧩",
        "description": "Challenge your mind with brain-bending puzzles and clever mechanics",
        "color": "#00cccc",
        "games": [
            {
                "title": "Portal 2",
                "description": "Mind-bending portal puzzles with brilliant humor and co-op mode.",
                "platform": "PC, Console",
                "rating": 4.9,
                "link": "https://store.steampowered.com/app/620/Portal_2/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/620/header.jpg"
            },
            {
                "title": "The Witness",
                "description": "Explore a mysterious island filled with hundreds of interconnected puzzles.",
                "platform": "PC, Console",
                "rating": 4.5,
                "link": "https://store.steampowered.com/app/210970/The_Witness/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/210970/header.jpg"
            },
            {
                "title": "Baba Is You",
                "description": "Manipulate the rules of each level to solve creative logic puzzles.",
                "platform": "PC, Switch",
                "rating": 4.7,
                "link": "https://store.steampowered.com/app/736260/Baba_Is_You/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/736260/header.jpg"
            },
            {
                "title": "Tetris Effect",
                "description": "The classic puzzle game reimagined with stunning visuals and music.",
                "platform": "PC, Console",
                "rating": 4.6,
                "link": "https://store.steampowered.com/app/1003590/Tetris_Effect_Connected/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1003590/header.jpg"
            }
        ]
    },
    "racing": {
        "name": "Racing",
        "icon": "🏎️",
        "description": "Feel the speed with high-octane racing across stunning tracks",
        "color": "#ff6600",
        "games": [
            {
                "title": "Forza Horizon 5",
                "description": "Open-world racing across Mexico with hundreds of cars and stunning visuals.",
                "platform": "PC, Xbox",
                "rating": 4.8,
                "link": "https://store.steampowered.com/app/1551360/Forza_Horizon_5/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1551360/header.jpg"
            },
            {
                "title": "Need for Speed Unbound",
                "description": "Street racing with a unique anime-inspired art style and car customization.",
                "platform": "PC, Console",
                "rating": 4.3,
                "link": "https://store.steampowered.com/app/1846380/Need_for_Speed_Unbound/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1846380/header.jpg"
            },
            {
                "title": "Gran Turismo 7",
                "description": "The ultimate driving simulator with real-world cars and tracks.",
                "platform": "PlayStation, PC",
                "rating": 4.6,
                "link": "https://store.steampowered.com/app/2440510/Gran_Turismo_7/",
                "image_url": "https://image.api.playstation.com/vulcan/ap/rnd/202109/1321/yZ7dnmjzVAaATjQlCNqERvum.png"
            },
            {
                "title": "Mario Kart 8 Deluxe",
                "description": "Fun and chaotic kart racing with beloved Nintendo characters.",
                "platform": "Switch",
                "rating": 4.8,
                "link": "https://www.nintendo.com/us/store/products/mario-kart-8-deluxe-switch/",
                "image_url": "https://assets.nintendo.com/image/upload/ar_16:9,c_lpad,w_1240/b_white/f_auto/q_auto/ncom/software/switch/70010000000153/102c9a9d20c529baad5a08ce2c91845bbcc08fba5ed8bf0ccb270a6c236e7dd7"
            }
        ]
    },
    "horror": {
        "name": "Horror",
        "icon": "👻",
        "description": "Face your fears in terrifying atmospheres and survival scenarios",
        "color": "#880000",
        "games": [
            {
                "title": "Resident Evil 4 Remake",
                "description": "Survival horror masterpiece remade with modern graphics and gameplay.",
                "platform": "PC, Console",
                "rating": 4.8,
                "link": "https://store.steampowered.com/app/2050650/Resident_Evil_4/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2050650/header.jpg"
            },
            {
                "title": "Phasmophobia",
                "description": "Co-op ghost hunting with voice recognition and terrifying encounters.",
                "platform": "PC, Console",
                "rating": 4.6,
                "link": "https://store.steampowered.com/app/739630/Phasmophobia/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/739630/header.jpg"
            },
            {
                "title": "Alan Wake 2",
                "description": "Psychological horror thriller blending live-action and gameplay seamlessly.",
                "platform": "PC, Console",
                "rating": 4.7,
                "link": "https://www.epicgames.com/store/en-US/p/alan-wake-2",
                "image_url": "https://cdn2.unrealengine.com/alan-wake-2-key-art-1920x1080-999318898144.jpg"
            },
            {
                "title": "Silent Hill 2 Remake",
                "description": "Remake of the iconic psychological horror classic with modern visuals.",
                "platform": "PC, PlayStation",
                "rating": 4.6,
                "link": "https://store.steampowered.com/app/2124490/SILENT_HILL_2/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2124490/header.jpg"
            }
        ]
    },
    "sports": {
        "name": "Sports",
        "icon": "⚽",
        "description": "Compete in your favorite sports from football to basketball and beyond",
        "color": "#22aa22",
        "games": [
            {
                "title": "EA Sports FC 25",
                "description": "The world's most popular football simulation with updated rosters and gameplay.",
                "platform": "PC, Console",
                "rating": 4.3,
                "link": "https://store.steampowered.com/app/2669320/EA_SPORTS_FC_25/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2669320/header.jpg"
            },
            {
                "title": "NBA 2K25",
                "description": "Basketball simulation with deep career mode and online multiplayer.",
                "platform": "PC, Console",
                "rating": 4.2,
                "link": "https://store.steampowered.com/app/2688840/NBA_2K25/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2688840/header.jpg"
            },
            {
                "title": "Rocket League",
                "description": "Soccer meets cars in this unique and addictive free-to-play competitive game.",
                "platform": "PC, Console",
                "rating": 4.7,
                "link": "https://www.epicgames.com/store/en-US/p/rocket-league",
                "image_url": "https://cdn2.unrealengine.com/rocket-league-key-art-1920x1080-6060c41094dc.jpg"
            },
            {
                "title": "WWE 2K24",
                "description": "Wrestling simulation with a massive roster and creative match types.",
                "platform": "PC, Console",
                "rating": 4.3,
                "link": "https://store.steampowered.com/app/2492180/WWE_2K24/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2492180/header.jpg"
            }
        ]
    },
    "simulation": {
        "name": "Simulation",
        "icon": "🏗️",
        "description": "Build, manage, and simulate entire worlds and complex systems",
        "color": "#44aaff",
        "games": [
            {
                "title": "Cities: Skylines II",
                "description": "Build and manage sprawling cities with deep simulation mechanics.",
                "platform": "PC, Console",
                "rating": 4.4,
                "link": "https://store.steampowered.com/app/949230/Cities_Skylines_II/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/949230/header.jpg"
            },
            {
                "title": "The Sims 4",
                "description": "Create and control virtual people in the ultimate life simulation.",
                "platform": "PC, Console",
                "rating": 4.5,
                "link": "https://www.ea.com/games/the-sims/the-sims-4",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1222670/header.jpg"
            },
            {
                "title": "Microsoft Flight Simulator",
                "description": "Photorealistic flight simulation of the entire planet Earth.",
                "platform": "PC, Xbox",
                "rating": 4.7,
                "link": "https://store.steampowered.com/app/1250410/Microsoft_Flight_Simulator_2024/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1250410/header.jpg"
            },
            {
                "title": "Stardew Valley",
                "description": "Charming farming simulation with RPG elements and a wholesome community.",
                "platform": "PC, Console, Mobile",
                "rating": 4.9,
                "link": "https://store.steampowered.com/app/413150/Stardew_Valley/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/413150/header.jpg"
            }
        ]
    },
    "fighting": {
        "name": "Fighting",
        "icon": "🥊",
        "description": "Master combos and face off in intense one-on-one battles",
        "color": "#ff2266",
        "games": [
            {
                "title": "Street Fighter 6",
                "description": "The legendary fighting franchise returns with a modern World Tour mode.",
                "platform": "PC, Console",
                "rating": 4.7,
                "link": "https://store.steampowered.com/app/1364780/Street_Fighter_6/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1364780/header.jpg"
            },
            {
                "title": "Mortal Kombat 1",
                "description": "Brutal fighting game with a rebooted universe and cinematic story mode.",
                "platform": "PC, Console",
                "rating": 4.5,
                "link": "https://store.steampowered.com/app/1971870/Mortal_Kombat_1/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1971870/header.jpg"
            },
            {
                "title": "Tekken 8",
                "description": "Next-gen 3D fighting with aggressive gameplay and stunning graphics.",
                "platform": "PC, Console",
                "rating": 4.6,
                "link": "https://store.steampowered.com/app/1778820/TEKKEN_8/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1778820/header.jpg"
            },
            {
                "title": "Guilty Gear Strive",
                "description": "Gorgeous anime-style fighter with rock soundtrack and unique characters.",
                "platform": "PC, Console",
                "rating": 4.7,
                "link": "https://store.steampowered.com/app/1384160/Guilty_Gear_Strive/",
                "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1384160/header.jpg"
            }
        ]
    }
}

# Tutorials data
TUTORIALS_DATA = [
    {
        "id": 1,
        "category": "beginner",
        "title": "Getting Started with PC Gaming",
        "description": "Learn the basics of PC gaming: setting up your rig, installing games, optimizing settings, and understanding FPS, resolution, and graphics options.",
        "icon": "🖥️",
        "steps": [
            "Choose your gaming platform (Steam, Epic Games, GOG)",
            "Create an account and browse the store",
            "Check system requirements before purchasing",
            "Download and install your first game",
            "Configure graphics settings for best performance",
            "Set up your controller or keyboard/mouse bindings"
        ]
    },
    {
        "id": 2,
        "category": "beginner",
        "title": "Understanding Game Genres",
        "description": "A comprehensive guide to different game genres, what makes each unique, and how to find the perfect genre for your playstyle.",
        "icon": "📚",
        "steps": [
            "Action games: Fast reflexes and combat focus",
            "RPGs: Character progression and story choices",
            "Strategy: Planning, resource management, tactics",
            "Adventure: Exploration and narrative-driven",
            "Puzzle: Logic and problem-solving challenges",
            "Try free-to-play games from each genre to discover your preference"
        ]
    },
    {
        "id": 3,
        "category": "beginner",
        "title": "Setting Up Game Controllers",
        "description": "How to connect and configure controllers for PC gaming, including Xbox, PlayStation, and third-party controllers.",
        "icon": "🎮",
        "steps": [
            "Connect your controller via USB or Bluetooth",
            "Install necessary drivers (if needed)",
            "Configure controller in Steam Big Picture mode",
            "Customize button mappings per game",
            "Calibrate analog sticks and triggers",
            "Test your setup in a simple game first"
        ]
    },
    {
        "id": 4,
        "category": "advanced",
        "title": "Optimizing Game Performance",
        "description": "Advanced techniques to boost FPS, reduce input lag, and get the smoothest gaming experience from your hardware.",
        "icon": "⚡",
        "steps": [
            "Update GPU drivers to the latest version",
            "Disable unnecessary background processes",
            "Adjust in-game settings: shadows, AA, draw distance",
            "Enable hardware-accelerated GPU scheduling",
            "Use DLSS/FSR for better FPS without quality loss",
            "Monitor temperatures and adjust fan curves"
        ]
    },
    {
        "id": 5,
        "category": "advanced",
        "title": "Competitive Gaming Tips",
        "description": "Level up your competitive gameplay with pro strategies for FPS, MOBA, and fighting games.",
        "icon": "🏆",
        "steps": [
            "Practice aim training with tools like Aim Lab",
            "Learn map callouts and positioning",
            "Study pro player strategies and VOD reviews",
            "Master movement mechanics (strafing, bunny hopping)",
            "Develop game sense and prediction skills",
            "Maintain a healthy practice schedule to avoid burnout"
        ]
    },
    {
        "id": 6,
        "category": "advanced",
        "title": "Game Modding Basics",
        "description": "Introduction to game modding: finding mods, installing them safely, and even creating your own simple mods.",
        "icon": "🔧",
        "steps": [
            "Find trusted modding sites (Nexus Mods, ModDB)",
            "Install a mod manager (Vortex, MO2)",
            "Read mod descriptions and compatibility notes",
            "Always backup your game files before modding",
            "Check load order for multiple mods",
            "Join modding communities for support and resources"
        ]
    },
    {
        "id": 7,
        "category": "genre",
        "title": "Mastering Battle Royale Games",
        "description": "Strategies and tips for winning in battle royale games like Fortnite, Apex Legends, and PUBG.",
        "icon": "🎯",
        "steps": [
            "Choose your landing spot wisely",
            "Prioritize loot: weapons, shields, healing",
            "Master the zone rotation and positioning",
            "Learn when to engage vs. when to avoid fights",
            "Practice building (Fortnite) or movement abilities",
            "Play with a coordinated squad and communicate"
        ]
    },
    {
        "id": 8,
        "category": "genre",
        "title": "RPG Character Building Guide",
        "description": "How to build effective characters in RPGs: stats, skill trees, gear optimization, and party composition.",
        "icon": "🧙",
        "steps": [
            "Understand core stats (STR, DEX, INT, etc.)",
            "Plan your build around a specific playstyle",
            "Don't spread skill points too thin — specialize",
            "Match gear to your build's strengths",
            "Balance your party with different roles",
            "Save often and experiment with different approaches"
        ]
    }
]


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat messages using Groq API."""
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Get or initialize conversation history from session
    if "history" not in session:
        session["history"] = []

    # Add user message to history
    session["history"].append({"role": "user", "content": user_message})

    # Keep only last 20 messages to avoid token limits
    conversation = session["history"][-20:]

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation,
            model="qwen/qwen3.8-27b",
            temperature=0.7,
            max_tokens=1024,
        )

        ai_response = completion.choices[0].message.content

        # Add AI response to history
        session["history"].append({"role": "assistant", "content": ai_response})
        session.modified = True

        return jsonify({"response": ai_response})

    except Exception as e:
        return jsonify({"error": f"AI service error: {str(e)}"}), 500


@app.route("/chat/clear", methods=["POST"])
def clear_chat():
    """Clear conversation history."""
    session.pop("history", None)
    return jsonify({"status": "cleared"})


@app.route("/games")
def games():
    """Return all games data, optionally filtered by genre."""
    genre = request.args.get("genre", "").lower()
    if genre and genre in GAMES_DATA:
        return jsonify({genre: GAMES_DATA[genre]})
    return jsonify(GAMES_DATA)


@app.route("/tutorials")
def tutorials():
    """Return tutorials data, optionally filtered by category."""
    category = request.args.get("category", "").lower()
    if category:
        filtered = [t for t in TUTORIALS_DATA if t["category"] == category]
        return jsonify(filtered)
    return jsonify(TUTORIALS_DATA)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
