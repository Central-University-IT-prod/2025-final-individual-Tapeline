from asgi_monitor.integrations.litestar import (
    TracingConfig,
    MetricsConfig,
    build_tracing_middleware,
    build_metrics_middleware,
    add_metrics_endpoint,
)
from asgi_monitor.logging import configure_logging
from litestar import Litestar
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider


class InstrumentationProvider:
    def create_middlewares(self):
        configure_logging(level="INFO", json_format=True, include_trace=False)

        resource = Resource.create(
            attributes={
                "service.name": "litestar",
            },
        )
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)

        trace_config = TracingConfig(
            tracer_provider=tracer_provider
        )
        self.metrics_config = MetricsConfig(
            app_name="litestar", include_trace_exemplar=True
        )
        return [
            build_tracing_middleware(trace_config),
            build_metrics_middleware(self.metrics_config)
        ]

    def configure_app(self, app: Litestar) -> None:
        add_metrics_endpoint(
            app,
            self.metrics_config.registry,
            openmetrics_format=False
        )
