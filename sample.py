import asyncio

import httpx
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def get_span_processor():
    jaeger_exporter = JaegerExporter(
        # configure agent
        agent_host_name="jaeger",
        agent_port=6831,
        udp_split_oversized_batches=True,
    )
    return BatchSpanProcessor(jaeger_exporter)


trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "sample"}))
)
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(get_span_processor())
client = httpx.AsyncClient()
HTTPXClientInstrumentor().instrument_client(
    client, tracer_provider=trace.get_tracer_provider()
)


response = asyncio.run(client.get("http://google.com"))
print(response.status_code)
