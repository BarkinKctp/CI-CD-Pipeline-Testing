FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    bash \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

COPY entrypoint.sh /scripts/entrypoint.sh
RUN chmod +x /scripts/entrypoint.sh

ENTRYPOINT ["/scripts/entrypoint.sh"]