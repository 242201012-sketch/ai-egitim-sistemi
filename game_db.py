import os

from models import db


def configure_database(app):

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "postgresql://neondb_owner:npg_Ds8H6CxMdmTG@ep-calm-glitter-alu03wrm-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        )

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 180,
        "pool_timeout": 30,
        "pool_size": 5,
        "max_overflow": 10
    }

    db.init_app(app)