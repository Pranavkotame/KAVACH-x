from flask import Flask, render_template, request, jsonify, session, make_response
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ============================================================
# KAVACH CTF
# One challenge. Three layers. One final flag.
# ============================================================

MAIN_FLAG = "CHAKRA{abhimanyu_would_be_proud_you_breached_the_kavach}"
TOTAL_POINTS = 600  # awarded on full completion

LAYERS = {
    "1": {
        "id": "1",
        "title": "Layer 1 ~ The Outer Wall",
        "category": "Reconnaissance",
        "difficulty": "Easy",
        "code": "ABHIMANYU",
        "encoded_hint": "QUJISU1BTllV",
        "description": (
            "Every fortress has cracks if you look close enough. "
            "Inspect the structure carefully to find what lies hidden."
        ),
        "layer": 1,
    },
    "2": {
        "id": "2",
        "title": "Layer 2 ~ The Transmission",
        "category": "Signals",
        "difficulty": "Medium",
        "code": "DRONACHARYA",
        "description": (
            "Beyond the outer wall, an intercepted transmission echoes through the corridors. "
            "Analyze the sound and decode the message."
        ),
        "audio_file": "signal.wav",
        "layer": 2,
    },
    "3": {
        "id": "3",
        "title": "Layer 3 ~ The Spiral",
        "category": "Cryptography",
        "difficulty": "Hard",
        "code": "ARJUNA",
        "description": (
            "The innermost core is protected by an ancient cipher. "
            "Decrypt the message to find the warrior who breaks the Kavach."
        ),
        "encrypted_text": "GUR JNEEVBE JUB OERNXF GUR XNINPU VF NEWHNA",
        "layer": 3,
    },
}

# ============================================================
# HELPERS
# ============================================================

def get_solved():
    return session.get("solved", [])

def get_unlocked_layer():
    return len(get_solved()) + 1

def all_complete():
    return len(get_solved()) == len(LAYERS)

# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    solved = get_solved()
    unlocked = get_unlocked_layer()
    completed = all_complete()
    return render_template(
        "index.html",
        layers=LAYERS,
        solved=solved,
        unlocked=unlocked,
        completed=completed,
        main_flag=MAIN_FLAG if completed else None,
        total_points=TOTAL_POINTS,
    )


@app.route("/challenge/<layer_id>")
def challenge(layer_id):
    if layer_id not in LAYERS:
        return "Layer not found.", 404

    layer = LAYERS[layer_id]
    solved = get_solved()
    unlocked = get_unlocked_layer()

    if layer["layer"] > unlocked:
        return render_template("locked.html", layer=layer, unlocked=unlocked)

    is_solved = layer_id in solved
    return make_response(
        render_template("challenge.html", layer=layer, is_solved=is_solved)
    )


@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    layer_id = data.get("layer_id", "")
    submitted = data.get("code", "").strip()

    if layer_id not in LAYERS:
        return jsonify({"success": False, "message": "Invalid layer."})

    layer = LAYERS[layer_id]
    solved = get_solved()
    unlocked = get_unlocked_layer()

    if layer["layer"] > unlocked:
        return jsonify({"success": False, "message": "This layer is still sealed."})

    # Check if user submitted the raw encoded string for Layer 1
    if layer_id == "1" and submitted == layer.get("encoded_hint", ""):
        return jsonify({
            "success": False,
            "message": "You found the encoded inscription. Now decode it to find the name."
        })

    # Case-insensitive comparison
    if submitted.upper() == layer["code"].upper():
        if layer_id not in solved:
            solved.append(layer_id)
            session["solved"] = solved

        completed = len(solved) == len(LAYERS)

        if completed:
            msg = "The final layer crumbles. The Kavach has fallen. Return to claim your flag."
        else:
            msg = f"Layer {layer['layer']} breached. The next layer awaits."

        return jsonify({"success": True, "message": msg, "completed": completed})
    else:
        return jsonify({"success": False, "message": "Wrong code. The Kavach holds strong."})


@app.route("/scoreboard")
def scoreboard():
    solved = get_solved()
    completed = all_complete()
    solved_layers = [LAYERS[lid] for lid in solved if lid in LAYERS]
    return render_template(
        "scoreboard.html",
        solved=solved_layers,
        total_layers=len(LAYERS),
        completed=completed,
        main_flag=MAIN_FLAG if completed else None,
        total_points=TOTAL_POINTS,
    )


@app.route("/reset")
def reset():
    session.clear()
    return '<script>window.location.href="/";</script>'


# ============================================================
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  KAVACH CTF SERVER STARTED")
    print("=" * 50)
    print("  Open: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, host="127.0.0.1", port=5000)
