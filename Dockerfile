FROM python:3.8-buster

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install flytekit

RUN echo -e '#!/bin/bash\naws --endpoint-url https://minio:9000 "$@"' > /usr/bin/aws && \
    chmod +x /usr/bin/aws"$