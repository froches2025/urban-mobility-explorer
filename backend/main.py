import math
import os
from contextlib import closing
from datetime import date

from flask import Flask, jsonify, request
from flask_cors import CORS

from db import get_db_connection
from spatial_utils import filter_zones_by_radius

app = Flask(__name__)
CORS(app)

SORT_COLUMNS = {
    "pickup_time": "t.pickup_datetime",
    "pickup_zone": "pickup.zone_name",
    "dropoff_zone": "dropoff.zone_name",
    "distance": "t.trip_distance",
    "duration_min": "t.trip_duration_min",
    "fare": "t.fare_amount",
    "cost_per_mile": "t.fare_amount / NULLIF(t.trip_distance, 0)",
    "speed": "t.avg_speed_mph",
}


def number_arg(name, *, minimum=None, maximum=None, default=None):
    value = request.args.get(name)
    if value in (None, ""):
        return default
    try:
        result = float(value)
    except ValueError:
        raise ValueError(f"{name} must be a number")
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    if minimum is not None and result < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    if maximum is not None and result > maximum:
        raise ValueError(f"{name} must be at most {maximum}")
    return result


def filter_query():
    clauses = []
    params = []
    start = request.args.get("start")
    end = request.args.get("end")
    if start:
        date.fromisoformat(start)
        clauses.append("date(t.pickup_datetime) >= date(?)")
        params.append(start)
    if end:
        date.fromisoformat(end)
        clauses.append("date(t.pickup_datetime) <= date(?)")
        params.append(end)
    hour_min = number_arg("hour_min", minimum=0, maximum=23)
    hour_max = number_arg("hour_max", minimum=0, maximum=23)
    if hour_min is not None:
        clauses.append("CAST(strftime('%H', t.pickup_datetime) AS INTEGER) >= ?")
        params.append(hour_min)
    if hour_max is not None:
        clauses.append("CAST(strftime('%H', t.pickup_datetime) AS INTEGER) <= ?")
        params.append(hour_max)
    if hour_min is not None and hour_max is not None and hour_min > hour_max:
        raise ValueError("hour_min must not exceed hour_max")
    for name, column, minimum, maximum in (
        ("min_distance", "t.trip_distance", 0, None),
        ("max_distance", "t.trip_distance", 0, None),
        ("min_fare", "t.fare_amount", 0, None),
        ("max_fare", "t.fare_amount", 0, None),
    ):
        value = number_arg(name, minimum=minimum, maximum=maximum)
        if value is not None:
            operator = ">=" if name.startswith("min_") else "<="
            clauses.append(f"{column} {operator} ?")
            params.append(value)
    min_distance = request.args.get("min_distance")
    max_distance = request.args.get("max_distance")
    min_fare = request.args.get("min_fare")
    max_fare = request.args.get("max_fare")
    if min_distance and max_distance and float(min_distance) > float(max_distance):
        raise ValueError("min_distance must not exceed max_distance")
    if min_fare and max_fare and float(min_fare) > float(max_fare):
        raise ValueError("min_fare must not exceed max_fare")
    borough = request.args.get("borough") or request.args.get("boroughs")
    if borough:
        clauses.append("borough.borough_name = ?")
        params.append(borough)
    return clauses, params


def trip_from_clause():
    return (
        " FROM trips t "
        "JOIN zones pickup ON pickup.zone_id = t.pickup_zone_id "
        "JOIN zones dropoff ON dropoff.zone_id = t.dropoff_zone_id "
        "JOIN boroughs borough ON borough.borough_id = pickup.borough_id "
    )


def trip_row(row):
    return {
        "pickup_time": row["pickup_datetime"],
        "pickup_zone": row["pickup_zone"],
        "dropoff_zone": row["dropoff_zone"],
        "distance": row["trip_distance"],
        "duration_min": row["trip_duration_min"],
        "fare": row["fare_amount"],
        "cost_per_mile": (
            round(row["fare_amount"] / row["trip_distance"], 2)
            if row["trip_distance"]
            else None
        ),
        "speed": row["avg_speed_mph"],
    }


@app.errorhandler(ValueError)
def invalid_request(error):
    return jsonify({"error": str(error)}), 400


@app.route("/api/summary")
def summary():
    clauses, params = filter_query()
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with closing(get_db_connection()) as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS trips, AVG(t.fare_amount) AS avg_fare, "
            "AVG(t.trip_distance) AS avg_distance, AVG(t.avg_speed_mph) AS avg_speed"
            + trip_from_clause() + where,
            params,
        ).fetchone()
    return jsonify({key: row[key] or 0 for key in ("trips", "avg_fare", "avg_distance", "avg_speed")})


@app.route("/api/hourly")
def hourly():
    clauses, params = filter_query()
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with closing(get_db_connection()) as conn:
        rows = conn.execute(
            "SELECT CAST(strftime('%H', t.pickup_datetime) AS INTEGER) AS hour, "
            "COUNT(*) AS trips" + trip_from_clause() + where
            + " GROUP BY hour ORDER BY hour",
            params,
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.route("/api/boroughs")
def boroughs():
    clauses, params = filter_query()
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with closing(get_db_connection()) as conn:
        rows = conn.execute(
            "SELECT borough.borough_name AS borough, COUNT(*) AS trips"
            + trip_from_clause() + where
            + " GROUP BY borough.borough_name ORDER BY trips DESC",
            params,
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.route("/api/zones/top")
def top_zones():
    clauses, params = filter_query()
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with closing(get_db_connection()) as conn:
        rows = conn.execute(
            "SELECT pickup.zone_name AS zone, COUNT(*) AS trips"
            + trip_from_clause() + where
            + " GROUP BY pickup.zone_name ORDER BY trips DESC LIMIT 20",
            params,
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.route("/api/fare-distance")
def fare_distance():
    clauses, params = filter_query()
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with closing(get_db_connection()) as conn:
        rows = conn.execute(
            "SELECT t.trip_distance AS distance, t.fare_amount AS fare"
            + trip_from_clause() + where
            + " ORDER BY t.trip_id LIMIT 5000",
            params,
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.route("/api/trips")
def trips():
    clauses, params = filter_query()
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    sort = request.args.get("sort", "pickup_time")
    order = request.args.get("order", "desc").lower()
    if sort not in SORT_COLUMNS:
        raise ValueError("sort is invalid")
    if order not in {"asc", "desc"}:
        raise ValueError("order must be asc or desc")
    page = int(number_arg("page", minimum=1, default=1))
    limit = int(number_arg("limit", minimum=1, maximum=100, default=10))
    with closing(get_db_connection()) as conn:
        total = conn.execute(
            "SELECT COUNT(*)" + trip_from_clause() + where, params
        ).fetchone()[0]
        rows = conn.execute(
            "SELECT t.pickup_datetime, pickup.zone_name AS pickup_zone, "
            "dropoff.zone_name AS dropoff_zone, t.trip_distance, "
            "t.trip_duration_min, t.fare_amount, t.avg_speed_mph"
            + trip_from_clause() + where
            + f" ORDER BY {SORT_COLUMNS[sort]} {order.upper()} LIMIT ? OFFSET ?",
            params + [limit, (page - 1) * limit],
        ).fetchall()
    return jsonify({"total": total, "rows": [trip_row(row) for row in rows]})


@app.route("/api/zones/nearby")
def nearby_zones():
    lat = number_arg("lat", minimum=-90, maximum=90)
    lon = number_arg("lon", minimum=-180, maximum=180)
    radius = number_arg("radius", minimum=0, default=5)
    if lat is None or lon is None:
        raise ValueError("lat and lon are required")
    with closing(get_db_connection()) as conn:
        rows = conn.execute(
            "SELECT zone_id AS id, zone_name AS name, "
            "centroid_lat AS latitude, centroid_lon AS longitude FROM zones "
            "WHERE centroid_lat IS NOT NULL AND centroid_lon IS NOT NULL"
        ).fetchall()
    return jsonify(filter_zones_by_radius([dict(row) for row in rows], lat, lon, radius))


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "").lower() == "true", port=5000)
