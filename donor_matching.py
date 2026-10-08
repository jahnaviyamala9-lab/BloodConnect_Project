from flask import Flask, request, jsonify, render_template
import math

app = Flask(__name__)

COMPATIBILITY = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["A-", "B-", "AB-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"]
}

donors = [
    {
        "id": 1,
        "name": "Ravi",
        "blood_group": "O+",
        "available": True,
        "lat": 16.5062,
        "lon": 80.6480
    },
    {
        "id": 2,
        "name": "Priya",
        "blood_group": "A+",
        "available": True,
        "lat": 16.5193,
        "lon": 80.6305
    },
    {
        "id": 3,
        "name": "Arjun",
        "blood_group": "B+",
        "available": False,
        "lat": 16.5000,
        "lon": 80.6500
    },
    {
        "id": 4,
        "name": "Sneha",
        "blood_group": "O-",
        "available": True,
        "lat": 16.5100,
        "lon": 80.6400
    }
]


def distance(lat1, lon1, lat2, lon2):
    R = 6371

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dl / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def match_score(donor, recipient_group, hospital_lat, hospital_lon):

    score = 0

    if donor["blood_group"] in COMPATIBILITY.get(
        recipient_group, []
    ):
        score += 50

    if donor["available"]:
        score += 30

    d = distance(
        donor["lat"],
        donor["lon"],
        hospital_lat,
        hospital_lon
    )

    if d <= 5:
        score += 20
    elif d <= 10:
        score += 15
    elif d <= 20:
        score += 10
    else:
        score += 5

    return score, d


@app.route("/")
def home():
    return render_template("test.html")


@app.route("/test")
def test_page():
    return render_template("test.html")


@app.route("/match-donors", methods=["POST"])
def match_donors():

    data = request.get_json()

    recipient_group = data.get("blood_group")
    hospital_lat = float(data.get("latitude"))
    hospital_lon = float(data.get("longitude"))

    results = []

    for donor in donors:

        if donor["blood_group"] in COMPATIBILITY.get(
            recipient_group, []
        ):

            score, dist = match_score(
                donor,
                recipient_group,
                hospital_lat,
                hospital_lon
            )

            results.append({
                "name": donor["name"],
                "blood_group": donor["blood_group"],
                "distance": round(dist, 2),
                "match_score": score,
                "status": (
                    "Available"
                    if donor["available"]
                    else "Not Available"
                )
            })

    results.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return jsonify({
        "total_matches": len(results),
        "recommended_donors": results
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )