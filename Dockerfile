FROM python:3.8-buster

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install awscli

WORKDIR src
COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# FIXME: Move up again
COPY setup.py .
COPY flytekitplugins/ ./flytekitplugins
RUN pip install . --no-deps

RUN echo '#!/bin/bash\n/usr/local/bin/aws --endpoint-url http://minio.flyte.svc.cluster.local:9000 "$@"' > /usr/bin/aws && \
    chmod +x /usr/bin/aws
ENV PATH="/usr/bin:$PATH"
ENV AWS_ACCESS_KEY_ID=minio
ENV AWS_SECRET_ACCESS_KEY=miniostorage
ENV PYTHONPATH="/root":$PYTHONPATH