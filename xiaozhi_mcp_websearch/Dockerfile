ARG BUILD_FROM=python:3.12-slim
FROM ${BUILD_FROM}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV XIAOZHI_WEBSEARCH_CONFIG=/data/options.json

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt \
    && adduser --system --group --home /app appuser

COPY app /app/app
COPY run.sh /run.sh
RUN chmod +x /run.sh \
    && chown -R appuser:appuser /app

EXPOSE 8765

USER appuser
CMD ["/run.sh"]

