"""Additional pages!"""

from flask import Blueprint

kibbles_bp = Blueprint(
    "kibbles",
    __name__,
    template_folder = "templates",
    static_folder = "static",
    static_url_path = "/kibbles/static",
    url_prefix = "/kibbles"
)

@kibbles_bp.route("/gathering", methods=["GET"])
def gathering():
    return ""