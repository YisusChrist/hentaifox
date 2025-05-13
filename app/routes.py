from typing import Any

from flask import jsonify, render_template

from app import app
from app.scrape import extract_id_from_url, generate_random_id, scrape_with_retries


@app.route("/hentaifox/<path:input_data>", methods=["GET"])
def scrape(input_data: str):
    try:
        if input_data == "random":
            random_id: int = generate_random_id()
            data: dict[str, Any] | None = scrape_with_retries(random_id)
            return jsonify(data)

        if "hentaifox.com" in input_data:
            dj_id: str | None = extract_id_from_url(input_data)
            if dj_id:
                data = scrape_with_retries(int(dj_id))
                return jsonify(data)

        if input_data.isdigit():
            data = scrape_with_retries(int(input_data))
            return jsonify(data)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Invalid input. Please provide a valid ID, URL, or 'random'",
                }
            ),
            400,
        )

    except Exception as error:
        print(f"Error processing request: {error}")
        return jsonify({"success": False, "message": str(error)}), 500


@app.route("/", methods=["GET"])
def documentation() -> str:
    return render_template("index.html")
