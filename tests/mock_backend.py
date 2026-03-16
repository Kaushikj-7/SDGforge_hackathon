import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/api/verify", methods=["POST"])
def verify():
    data = request.json
    print("\n" + "=" * 50)
    print("MOCK BACKEND RECEIVED PAYLOAD:")
    print("=" * 50)
    print(json.dumps(data, indent=2))
    print("=" * 50 + "\n")

    # Return standard formatted response for frontend success
    return jsonify(
        {
            "status": "safe",
            "corrected_fact": "Mocked validation complete.",
            "explanation": "This is a dummy response from the mock backend verifying your JSON contract is correct.",
            "source_links": ["https://mock-source.com"],
            "proof_chain": [
                {"node": "User Claim", "type": "input"},
                {"node": "Mock DB", "type": "db_query"},
                {"node": "Verified", "type": "debunk"},
            ],
        }
    )


if __name__ == "__main__":
    print("Mock Backend running on http://localhost:5000")
    app.run(port=5000, debug=True)
