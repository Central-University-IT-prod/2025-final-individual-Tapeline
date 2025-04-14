import asyncio
import sys

from litestar.plugins.prometheus import PrometheusConfig

from prodadvert.config import Config
from prodadvert.controllers.http.advertisements import AdvertisementsController, MetricsController
from prodadvert.controllers.http.advertisers import AdvertisersController
from prodadvert.controllers.http.ai import AIController
from prodadvert.controllers.http.campaigns import CampaignsController
from prodadvert.controllers.http.clients import ClientsController
from prodadvert.controllers.http.exc_handlers import handler_mapping
from prodadvert.controllers.http.utils import TimeController, PingController, ProfanityController
from prodadvert.di import AppProvider
from prodadvert.instrumentation import InstrumentationProvider

if sys.platform == "win32":
    from asyncio import WindowsSelectorEventLoopPolicy

from dishka import make_async_container
from dishka.integrations import litestar as litestar_integration
from litestar import Litestar
from litestar.logging import LoggingConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin

config = Config()
container = make_async_container(
    AppProvider(),
    context={
        Config: config,
    }
)


def get_app() -> Litestar:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    logging_config = LoggingConfig(
        root={"level": "INFO", "handlers": ["queue_listener"]},
        formatters={
            "standard": {
                "format": (
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            }
        },
        log_exceptions="always",
    )
    instrumentation = InstrumentationProvider()
    prometheus_config = PrometheusConfig(group_path=False)
    litestar_app = Litestar(
        debug=config.mode.debug_mode,
        route_handlers=[
            ClientsController,
            AdvertisersController,
            CampaignsController,
            AdvertisementsController,
            MetricsController,
            TimeController,
            PingController,
            ProfanityController,
            #PrometheusController,
            AIController
        ],
        middleware=[
            prometheus_config.middleware,
            *instrumentation.create_middlewares()
        ],
        exception_handlers=handler_mapping,  # type: ignore
        openapi_config=OpenAPIConfig(
            title="PRODAdvert",
            description="PROD'25 Finals Solution",
            version="1.0.0",
            render_plugins=[
                SwaggerRenderPlugin(),
            ],
            path="/docs",
        ),
        logging_config=logging_config,
    )
    litestar_integration.setup_dishka(container, litestar_app)
    instrumentation.configure_app(litestar_app)
    return litestar_app
