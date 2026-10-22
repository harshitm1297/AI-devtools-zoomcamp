from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


@dataclass(frozen=True)
class Telemetry:
    tracer: trace.Tracer
    assessment_counter: metrics.Counter
    assessment_duration: metrics.Histogram
    extraction_counter: metrics.Counter
    grounding_failures: metrics.Counter
    logger: logging.Logger


def configure_telemetry(app) -> Telemetry:
    resource = Resource.create(
        {
            "service.name": "guardian-angel",
            "service.version": os.getenv("APP_VERSION", "dev"),
            "deployment.environment.name": os.getenv("APP_ENV", "development"),
        }
    )
    mode = os.getenv("OTEL_EXPORTER_MODE", "none").lower()
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
    tracer_provider = TracerProvider(resource=resource)
    logger_provider = LoggerProvider(resource=resource)
    readers = []
    if mode == "otlp":
        tracer_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
        )
        readers.append(
            PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=endpoint, insecure=True),
                export_interval_millis=int(os.getenv("OTEL_METRIC_EXPORT_INTERVAL_MS", "5000")),
            )
        )
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(OTLPLogExporter(endpoint=endpoint, insecure=True))
        )
    elif mode != "none":
        raise ValueError("OTEL_EXPORTER_MODE must be 'none' or 'otlp'")

    meter_provider = MeterProvider(resource=resource, metric_readers=readers)
    trace.set_tracer_provider(tracer_provider)
    metrics.set_meter_provider(meter_provider)
    if mode == "otlp":
        FastAPIInstrumentor.instrument_app(app, excluded_urls="healthz")

    logger = logging.getLogger("guardian-angel")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.handlers.clear()
    if mode == "otlp":
        logger.addHandler(LoggingHandler(level=logging.INFO, logger_provider=logger_provider))

    meter = metrics.get_meter("guardian-angel")
    return Telemetry(
        tracer=trace.get_tracer("guardian-angel"),
        assessment_counter=meter.create_counter(
            "guardian_angel.assessments", unit="{assessment}",
            description="Assessment attempts by bounded outcome",
        ),
        assessment_duration=meter.create_histogram(
            "guardian_angel.assessment_duration", unit="s",
            description="End-to-end assessment duration",
        ),
        extraction_counter=meter.create_counter(
            "guardian_angel.receipt_extractions", unit="{extraction}",
            description="Receipt extraction attempts by bounded outcome",
        ),
        grounding_failures=meter.create_counter(
            "guardian_angel.grounding_failures", unit="{failure}",
            description="Rejected explanations with invalid evidence citations",
        ),
        logger=logger,
    )

