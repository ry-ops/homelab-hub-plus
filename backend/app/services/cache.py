"""
Redis-backed Flask-Caching instance.

Usage:
    from app.services.cache import cache

    @cache.cached(timeout=30, key_prefix="map_graph")
    def my_view():
        ...

    # Invalidate manually:
    cache.delete("map_graph")
"""
from flask_caching import Cache

cache = Cache()


def init_cache(app):
    cache.init_app(app)
