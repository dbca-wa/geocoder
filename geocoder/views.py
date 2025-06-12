import re

from flask import Blueprint, abort, jsonify, render_template, request, send_from_directory
from sqlalchemy.sql import text

from .database import db

bp = Blueprint("geocoder", __name__)
LON_LAT_PATTERN = re.compile(r"(?P<lon>-?[0-9]+.[0-9]+),\s*(?P<lat>-?[0-9]+.[0-9]+)")
ALPHANUM_PATTERN = re.compile(r"[^A-Za-z0-9\s]+")


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/api/<object_id>")
def detail(object_id):
    sql = text("""SELECT object_id, address_nice, owner, ST_AsText(centroid), ST_AsText(envelope), ST_AsText(boundary), data
               FROM shack_address
               WHERE object_id=:object_id""")

    sql = sql.bindparams(object_id=object_id)
    record = db.session.execute(sql).fetchone()

    if record:
        return jsonify(
            {
                "object_id": record[0],
                "address": record[1],
                "owner": record[2],
                "centroid": record[3],
                "envelope": record[4],
                "boundary": record[5],
                "data": record[6],
            }
        )
    else:
        return jsonify({})


@bp.get("/api/geocode")
def geocode():
    """This route will accept a query parameter (`q` or `point`), and query for matching land parcels.
    `point` must be a string that parses as <float>,<float> and will be used to query for intersection with the `boundary`
    spatial column.
    `q` will be parsed as free text (non-alphanumeric characters will be ignored) and will be used to perform a text search
    against the `tsv` column.
    Query results will be returned as serialised JSON objects.
    An optional `limit` parameter may be passed in to limit the maximum number of results returned, otherwise the route
    defaults to a maximum of five results (no sorting is carried out, so these are simply the first five results from the
    query.
    """
    q = request.args.get("q", "", type=str)
    point = request.args.get("point", "", type=str)
    if not q and not point:
        abort(400, "Invalid request parameters")

    # Point intersection query
    if point:  # Must be in the format lon,lat
        m = LON_LAT_PATTERN.match(point)
        if m:
            lon, lat = m.groups()
            # Validate `lon` and `lat` by casting them to float values.
            try:
                lon, lat = float(lon), float(lat)
            except ValueError:
                abort(400, "Invalid coordinate")

            ewkt = f"SRID=4326;POINT({lon} {lat})"
            sql = text("""SELECT object_id, address_nice, owner, ST_AsText(centroid), ST_AsText(envelope), ST_AsText(boundary), data
                FROM shack_address
                WHERE ST_Intersects(boundary, ST_GeomFromEWKT(:ewkt))""")
            sql = sql.bindparams(ewkt=ewkt)
            record = db.session.execute(sql).fetchone()

            # Serialise and return any query result.
            if record:
                return jsonify(
                    {
                        "object_id": record[0],
                        "address": record[1],
                        "owner": record[2],
                        "centroid": record[3],
                        "envelope": record[4],
                        "boundary": record[5],
                        "data": record[6],
                    }
                )
            else:
                return jsonify({})
        else:
            abort(400, "Invalid coordinate")

    # Address query
    # Sanitise the input query: remove any non-alphanumeric/whitespace characters.
    q = re.sub(ALPHANUM_PATTERN, "", q)
    words = q.split()  # Split words on whitespace.
    tsquery = "&".join(words)

    # Default to return a maximum of five results, allow override via `limit`.
    if "limit" in request.args:
        limit = request.args.get("limit", type=int)
    else:
        limit = 5

    sql = text("""SELECT object_id, address_nice, owner, ST_X(centroid), ST_Y(centroid)
        FROM shack_address
        WHERE tsv @@ to_tsquery(:tsquery)
        LIMIT :limit""")
    sql = sql.bindparams(tsquery=tsquery, limit=limit)
    records = db.session.execute(sql).fetchall()

    # Serialise and return any query results.
    return jsonify(
        [
            {
                "object_id": record[0],
                "address": record[1],
                "owner": record[2],
                "lon": record[3],
                "lat": record[4],
            }
            for record in records
        ]
    )


@bp.get("/livez")
def liveness():
    return "OK"


@bp.get("/readyz")
def readiness():
    # Returns a HTTP 500 error if database connection unavailable.
    db.session.execute(text("SELECT 1")).fetchone()
    return "OK"


@bp.get("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico")
