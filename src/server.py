from fastapi import FastAPI
from request_id_helper import init_logger
from starlette_exporter import PrometheusMiddleware, handle_metrics
from starlette_request_id import RequestIdMiddleware

from src import routers
from src.conf import LOG_CONFIG, settings


def init_app():
    app_ = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        docs_url="/docs" if settings.docs_enable else None,
    )
    app_.add_middleware(PrometheusMiddleware)
    app_.add_middleware(RequestIdMiddleware)

    init_logger(LOG_CONFIG)

    app_.add_route("/metrics", handle_metrics)
    app_.include_router(routers.router)

    return app_


app = init_app()
