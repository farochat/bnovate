import uuid
from flask import Flask, request, jsonify, send_file
import os
import db
import plot
from reader import read_csv, is_valid_polygon
import logging

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload_csv():
    username = request.args.get("username")
    username = username if username else uuid.uuid4().hex
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "No selected file"}), 400

    fpath = os.path.join(UPLOAD_FOLDER, f.filename)
    f.save(fpath)

    try:
        vertices = read_csv(fpath)
        valid, msg = is_valid_polygon(vertices)
        if not valid:
            logging.error(msg)
            raise ValueError(msg)
        else:
            db.insert(username, vertices)

        return jsonify({"message": "CSV processed and data saved!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/visualize", methods=["GET"])
def visualize():
    username = request.args.get("username")
    try:
        vertices = db.vertex_from_username(username)
        if not vertices:
            return jsonify({"error": "No polygons found"}), 404
        filepath = plot.polygon(vertices, filename=username)
        if filepath:
            return send_file(filepath, mimetype="image/png")
        else:
            return jsonify({"error": "No image sent."}), 204

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
