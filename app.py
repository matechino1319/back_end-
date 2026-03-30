from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import or_

from models import db, Player

# ==== CONFIG MySQL (Workbench) ====
DB_USER = "root"
DB_PASSWORD = "Mateo1319#"
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "futdata"

def create_app():
    app = Flask(__name__)
    CORS(app)

    # IMPORTANTE: la clave correcta es SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    Migrate(app, db)

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    @app.post("/api/players")
    def create_player():
        data = request.get_json(silent=True) or {}
        full_name = (data.get("full_name") or "").strip()
        if not full_name:
            return jsonify({"error": "full_name es requerido"}), 400

        player = Player(
            full_name=full_name,
            nationality=data.get("nationality"),
            position=data.get("position"),
            club=data.get("club"),
            age=data.get("age"),
            preferred_foot=data.get("preferred_foot"),
            active=bool(data.get("active", True)),
            matches=data.get("matches", 0),
            goals=data.get("goals", 0),
            assists=data.get("assists", 0),
            minutes=data.get("minutes", 0),
        )
        db.session.add(player)
        db.session.commit()
        return jsonify(player.to_dict()), 201

    @app.get("/api/players")
    def list_players():
        q = (request.args.get("q") or "").strip()
        country = (request.args.get("country") or "").strip()
        pos = (request.args.get("pos") or "").strip()
        club = (request.args.get("club") or "").strip()
        active = request.args.get("active")

        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 12)), 50)

        query = Player.query

        if q:
            like = f"%{q}%"
            query = query.filter(or_(
                Player.full_name.ilike(like),
                Player.club.ilike(like)
            ))

        if country:
            query = query.filter(Player.nationality.ilike(f"%{country}%"))

        if pos:
            query = query.filter(Player.position.ilike(f"%{pos}%"))

        if club:
            query = query.filter(Player.club.ilike(f"%{club}%"))

        if active is not None:
            active_bool = active.lower() in ("1", "true", "yes", "y", "si")
            query = query.filter(Player.active == active_bool)

        query = query.order_by(Player.full_name.asc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [p.to_dict() for p in pagination.items]

        return jsonify({
            "items": items,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        })

    @app.get("/api/players/<int:player_id>")
    def get_player(player_id: int):
        player = db.session.get(Player, player_id)
        if not player:
            abort(404)
        return jsonify(player.to_dict())

    @app.patch("/api/players/<int:player_id>")
    def patch_player(player_id: int):
        player = db.session.get(Player, player_id)
        if not player:
            abort(404)

        data = request.get_json(silent=True) or {}

        allowed = [
            "full_name", "nationality", "position", "club",
            "age", "preferred_foot", "active",
            "matches", "goals", "assists", "minutes"
        ]
        for field in allowed:
            if field in data:
                setattr(player, field, data[field])

        if "full_name" in data and not (player.full_name or "").strip():
            return jsonify({"error": "full_name no puede quedar vacío"}), 400

        db.session.commit()
        return jsonify(player.to_dict())

    @app.delete("/api/players/<int:player_id>")
    def delete_player(player_id: int):
        player = db.session.get(Player, player_id)
        if not player:
            abort(404)

        db.session.delete(player)
        db.session.commit()
        return "", 204

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)