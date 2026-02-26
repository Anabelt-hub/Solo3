import os
import uuid

import psycopg
from psycopg.rows import dict_row
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()


# ------------------------------ DB helpers ------------------------------
def get_db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var is missing.")
    return psycopg.connect(
        DATABASE_URL,
        sslmode="require",
        row_factory=dict_row
    )


def init_db():
    """Create table if missing + ensure at least 30 seeded rows."""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id UUID PRIMARY KEY,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            genre TEXT NOT NULL,
            year INT NOT NULL,
            rating INT,
            status TEXT NOT NULL,
            notes TEXT,
            image_url TEXT NOT NULL DEFAULT ''
        );
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) AS c FROM records;")
    count = int(cur.fetchone()["c"])

    if count < 30:
        seeds = seed_records()
        need = 30 - count
        to_insert = seeds[:need]

        if to_insert:
            rows = []
            for r in to_insert:
                rows.append((
                    uuid.UUID(r["id"]),
                    r["title"],
                    r["type"],
                    r["genre"],
                    r["year"],
                    r["rating"],
                    r["status"],
                    r["notes"],
                    r["image_url"],
                ))

            cur.executemany(
                """
                INSERT INTO records (id, title, type, genre, year, rating, status, notes, image_url)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                rows
            )
            conn.commit()

    cur.close()
    conn.close()


def seed_records():
    """Return >= 35 records with image_url (so seeding has enough)."""
    def rec(title, rtype, genre, year, rating, status, image_url, notes=""):
        return {
            "id": str(uuid.uuid4()),
            "title": title,
            "type": rtype,
            "genre": genre,
            "year": year,
            "rating": rating,
            "status": status,
            "notes": notes,
            "image_url": image_url
        }

    # Public image URLs (you can swap anytime)
    return [
        rec("The Dark Knight", "Movie", "Action", 2008, 9, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/8/8a/Dark_Knight.jpg"),
        rec("Inception", "Movie", "Sci-Fi", 2010, 9, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/7/7f/Inception_ver3.jpg"),
        rec("Interstellar", "Movie", "Sci-Fi", 2014, 9, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg"),
        rec("The Matrix", "Movie", "Sci-Fi", 1999, 9, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/c/c1/The_Matrix_Poster.jpg"),
        rec("Parasite", "Movie", "Thriller", 2019, 9, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/5/53/Parasite_%282019_film%29.png"),
        rec("Get Out", "Movie", "Horror", 2017, 8, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/a/a3/Get_Out_poster.png"),
        rec("The Shawshank Redemption", "Movie", "Drama", 1994, 10, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/8/81/ShawshankRedemptionMoviePoster.jpg"),
        rec("Pulp Fiction", "Movie", "Crime", 1994, 9, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/8/82/Pulp_Fiction_cover.jpg"),
        rec("Spirited Away", "Movie", "Animation", 2001, 10, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/d/db/Spirited_Away_Japanese_poster.png"),
        rec("Avengers: Endgame", "Movie", "Action", 2019, 8, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/0/0d/Avengers_Endgame_poster.jpg"),
        rec("Dune", "Movie", "Sci-Fi", 2021, 8, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/8/8e/Dune_%282021_film%29.jpg"),
        rec("Oppenheimer", "Movie", "Drama", 2023, 9, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/4/4a/Oppenheimer_%28film%29.jpg"),
        rec("Barbie", "Movie", "Comedy", 2023, 7, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/0/0b/Barbie_2023_poster.jpg"),
        rec("Top Gun: Maverick", "Movie", "Action", 2022, 8, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/1/13/Top_Gun_Maverick_Poster.jpg"),
        rec("Knives Out", "Movie", "Mystery", 2019, 8, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/1/1f/Knives_Out_poster.jpeg"),

        rec("Breaking Bad", "Show", "Drama", 2008, 10, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/6/61/Breaking_Bad_title_card.png"),
        rec("Better Call Saul", "Show", "Drama", 2015, 9, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/6/6a/Better_Call_Saul_season_1_poster.jpg"),
        rec("Stranger Things", "Show", "Sci-Fi", 2016, 8, "Watching",
            "https://upload.wikimedia.org/wikipedia/en/f/f7/Stranger_Things_season_1.jpg"),
        rec("The Office", "Show", "Comedy", 2005, 8, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/8/80/The_Office_US_logo.svg"),
        rec("Game of Thrones", "Show", "Fantasy", 2011, 7, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/d/d8/Game_of_Thrones_title_card.jpg"),
        rec("House of the Dragon", "Show", "Fantasy", 2022, 8, "Watching",
            "https://upload.wikimedia.org/wikipedia/en/7/75/House_of_the_Dragon_logo.jpg"),
        rec("The Mandalorian", "Show", "Sci-Fi", 2019, 8, "Watching",
            "https://upload.wikimedia.org/wikipedia/en/c/c1/The_Mandalorian_season_1_poster.jpg"),
        rec("Black Mirror", "Show", "Sci-Fi", 2011, 9, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/2/24/BlackMirrorTitleCard.jpg"),
        rec("Chernobyl", "Show", "Drama", 2019, 10, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/9/9f/Chernobyl_2019_Miniseries.jpg"),
        rec("The Walking Dead", "Show", "Horror", 2010, 7, "Dropped",
            "https://upload.wikimedia.org/wikipedia/en/0/0e/TheWalkingDeadPoster.jpg"),

        # Extra to ensure we have enough to seed even if some already exist
        rec("The Grand Budapest Hotel", "Movie", "Comedy", 2014, 8, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/a/a6/The_Grand_Budapest_Hotel_Poster.jpg"),
        rec("La La Land", "Movie", "Romance", 2016, 8, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/a/ab/La_La_Land_%28film%29.png"),
        rec("The Social Network", "Movie", "Drama", 2010, 8, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/8/8c/The_Social_Network_film_poster.png"),
        rec("Spider-Man: Into the Spider-Verse", "Movie", "Animation", 2018, 9, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/8/87/Spider-Man_Into_the_Spider-Verse_poster.png"),
        rec("The Lion King", "Movie", "Animation", 1994, 9, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/3/3d/The_Lion_King_poster.jpg"),
        rec("The Boys", "Show", "Action", 2019, 8, "Watching",
            "https://upload.wikimedia.org/wikipedia/en/7/7a/The_Boys_Season_1.jpg"),
        rec("The Crown", "Show", "Drama", 2016, 8, "Planned",
            "https://upload.wikimedia.org/wikipedia/en/1/17/The_Crown_title_card.jpg"),
        rec("The Sopranos", "Show", "Drama", 1999, 10, "Planned",
            "https://upload.wikimedia.org/wikipedia/en/2/2c/The_Sopranos_title_card.jpg"),
        rec("Narcos", "Show", "Drama", 2015, 8, "Completed",
            "https://upload.wikimedia.org/wikipedia/en/1/1f/Narcos_season_1.png"),
    ]


# ------------------------------ Validation ------------------------------
def validate_record(data):
    title = (data.get("title") or "").strip()
    if not title:
        return "Title is required."

    rtype = (data.get("type") or "").strip()
    if not rtype:
        return "Type is required."

    genre = (data.get("genre") or "").strip()
    if not genre:
        return "Genre is required."

    try:
        year = int(data.get("year"))
    except Exception:
        return "Year must be a whole number."
    if year < 1900 or year > 2100:
        return "Year must be between 1900 and 2100."

    status = (data.get("status") or "").strip()
    if not status:
        return "Status is required."

    rating = data.get("rating", None)
    if rating is not None:
        try:
            rating = int(rating)
        except Exception:
            return "Rating must be a whole number."
        if rating < 1 or rating > 10:
            return "Rating must be between 1 and 10."

    image_url = (data.get("image_url") or "").strip()
    if not image_url:
        return "Image URL is required."

    return None


def parse_uuid(s):
    try:
        return uuid.UUID(str(s))
    except Exception:
        return None


def serialize_record(row: dict) -> dict:
    # psycopg returns UUID objects; jsonify needs strings
    out = dict(row)
    if "id" in out:
        out["id"] = str(out["id"])
    return out


# ------------------------------ Routes ------------------------------
@app.get("/")
def home():
    return "Solo Project 3 API running. Try /api/records and /api/stats", 200


@app.get("/api/records")
def get_records():
    """
    Query params:
      page, pageSize, search, status, sort, dir
    """
    init_db()

    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("pageSize", 10))
    page_size = max(5, min(page_size, 50))

    search = (request.args.get("search") or "").strip().lower()
    status = (request.args.get("status") or "ALL").strip()

    sort = (request.args.get("sort") or "title").strip()
    direction = (request.args.get("dir") or "asc").strip().lower()

    allowed_sort = {
        "title": "title",
        "year": "year",
        "rating": "rating",
        "genre": "genre",
        "status": "status",
        "type": "type",
    }
    sort_col = allowed_sort.get(sort, "title")
    dir_sql = "ASC" if direction != "desc" else "DESC"

    where = []
    params = []

    if search:
        where.append("LOWER(title) LIKE %s")
        params.append(f"%{search}%")

    if status != "ALL":
        where.append("status = %s")
        params.append(status)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    conn = get_db()
    cur = conn.cursor()

    # Total for paging
    cur.execute(f"SELECT COUNT(*) AS c FROM records {where_sql};", params)
    total = int(cur.fetchone()["c"])
    total_pages = max(1, (total + page_size - 1) // page_size)

    page = max(1, min(page, total_pages))
    offset = (page - 1) * page_size

    cur.execute(
        f"""
        SELECT id, title, type, genre, year, rating, status, notes, image_url
        FROM records
        {where_sql}
        ORDER BY {sort_col} {dir_sql}, title ASC
        LIMIT %s OFFSET %s;
        """,
        params + [page_size, offset]
    )
    items = [serialize_record(r) for r in cur.fetchall()]

    cur.close()
    conn.close()

    return jsonify({
        "items": items,
        "page": page,
        "pageSize": page_size,
        "total": total,
        "totalPages": total_pages
    }), 200


@app.get("/api/stats")
def get_stats():
    """Stats for the ENTIRE dataset."""
    init_db()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS c FROM records;")
    total = int(cur.fetchone()["c"])

    cur.execute("SELECT COUNT(*) AS c FROM records WHERE status='Completed';")
    completed_count = int(cur.fetchone()["c"])

    cur.execute("""
        SELECT AVG(rating) AS avg
        FROM records
        WHERE status='Completed' AND rating IS NOT NULL;
    """)
    avg = cur.fetchone()["avg"]
    avg_rating_completed = round(float(avg), 1) if avg is not None else None

    cur.execute("""
        SELECT genre, COUNT(*) AS c
        FROM records
        WHERE genre IS NOT NULL AND genre <> ''
        GROUP BY genre
        ORDER BY c DESC, genre ASC
        LIMIT 1;
    """)
    row = cur.fetchone()
    top_genre = row["genre"] if row else None

    statuses = ["Planned", "Watching", "Completed", "Dropped"]
    by_status = {s: 0 for s in statuses}
    cur.execute("SELECT status, COUNT(*) AS c FROM records GROUP BY status;")
    for r in cur.fetchall():
        if r["status"] in by_status:
            by_status[r["status"]] = int(r["c"])

    cur.close()
    conn.close()

    return jsonify({
        "totalRecords": total,
        "completedCount": completed_count,
        "avgRatingCompleted": avg_rating_completed,
        "topGenre": top_genre,
        "byStatus": by_status
    }), 200


@app.post("/api/records")
def create_record():
    init_db()

    data = request.get_json(force=True) or {}
    err = validate_record(data)
    if err:
        return jsonify({"error": err}), 400

    new_id = uuid.uuid4()

    record = {
        "id": str(new_id),
        "title": (data.get("title") or "").strip(),
        "type": (data.get("type") or "").strip(),
        "genre": (data.get("genre") or "").strip(),
        "year": int(data.get("year")),
        "rating": data.get("rating", None),
        "status": (data.get("status") or "").strip(),
        "notes": (data.get("notes") or "").strip(),
        "image_url": (data.get("image_url") or "").strip(),
    }

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO records (id, title, type, genre, year, rating, status, notes, image_url)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
    """, (
        new_id,
        record["title"],
        record["type"],
        record["genre"],
        record["year"],
        record["rating"],
        record["status"],
        record["notes"],
        record["image_url"],
    ))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify(record), 201


@app.put("/api/records/<rid>")
def update_record(rid):
    init_db()

    rid_uuid = parse_uuid(rid)
    if not rid_uuid:
        return jsonify({"error": "Invalid record id."}), 400

    data = request.get_json(force=True) or {}
    err = validate_record(data)
    if err:
        return jsonify({"error": err}), 400

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE records
        SET title=%s, type=%s, genre=%s, year=%s, rating=%s, status=%s, notes=%s, image_url=%s
        WHERE id=%s;
    """, (
        (data.get("title") or "").strip(),
        (data.get("type") or "").strip(),
        (data.get("genre") or "").strip(),
        int(data.get("year")),
        data.get("rating", None),
        (data.get("status") or "").strip(),
        (data.get("notes") or "").strip(),
        (data.get("image_url") or "").strip(),
        rid_uuid,
    ))

    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    if updated == 0:
        return jsonify({"error": "Record not found."}), 404

    return jsonify({"ok": True}), 200


@app.delete("/api/records/<rid>")
def delete_record(rid):
    init_db()

    rid_uuid = parse_uuid(rid)
    if not rid_uuid:
        return jsonify({"error": "Invalid record id."}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM records WHERE id=%s;", (rid_uuid,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Record not found."}), 404

    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    # Local dev
    port = int(os.environ.get("PORT", "5000"))
    init_db()
    app.run(host="0.0.0.0", port=port)
