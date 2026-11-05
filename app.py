import os
import secrets
import logging
import psycopg
import redis

from dotenv import load_dotenv
from flask import Flask, request, jsonify, redirect
from urllib.parse import urlparse

load_dotenv()

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

cache = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=1
)

def get_connection():
    return psycopg.connect(DATABASE_URL)


def is_valid_url(url):
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or "url" not in data:
        return jsonify({"error": "URL field is required"}), 400

    long_url = data["url"]

    if not isinstance(long_url, str) or not is_valid_url(long_url):
        return jsonify({"error": "Invalid URL"}), 400

    code = secrets.token_urlsafe(6)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO links (code, long_url)
                    VALUES (%s, %s)
                    """,
                    (code, long_url)
                )

        try:
            cache.setex(code, 3600, long_url)
        except redis.RedisError:
            app.logger.warning("Redis unavailable; database remains source of truth")

        return jsonify({
            "short_code": code,
            "original_url": long_url,
            "short_url": request.host_url + code
        }), 201

    except psycopg.Error:
        app.logger.exception("Database error")
        return jsonify({"error": "Database operation failed"}), 503


@app.route("/<code>", methods=["GET"])
def redirect_url(code):
    try:
        try:
            cached_url = cache.get(code)

            if cached_url:
                app.logger.info("CACHE HIT: %s", code)
                return redirect(cached_url, code=302)

        except redis.RedisError:
            app.logger.warning("Redis unavailable; falling back to PostgreSQL")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT long_url FROM links WHERE code = %s",
                    (code,)
                )
                result = cur.fetchone()

        if result is None:
            return jsonify({"error": "Short URL not found"}), 404

        long_url = result[0]

        try:
            cache.setex(code, 3600, long_url)
        except redis.RedisError:
            app.logger.warning("Could not populate Redis cache")

        app.logger.info("CACHE MISS: %s", code)
        return redirect(long_url, code=302)

    except psycopg.Error:
        app.logger.exception("Database error")
        return jsonify({"error": "Database operation failed"}), 503


@app.route("/health", methods=["GET"])
def health():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()

        redis_status = "connected"

        try:
            cache.ping()
        except redis.RedisError:
            redis_status = "disconnected"

        return jsonify({
            "status": "healthy" if redis_status == "connected" else "degraded",
            "database": "connected",
            "redis": redis_status
        }), 200 if redis_status == "connected" else 503

    except psycopg.Error:
        app.logger.exception("Database health check failed")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected"
        }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
