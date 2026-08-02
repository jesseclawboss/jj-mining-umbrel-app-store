FROM alpine/git:2.49.1 AS source
RUN git clone https://github.com/frstrtr/p2pool-merged-v36.git /src && cd /src && git checkout 44a10f30ea4fc8a2b60dfb47d5df7fc3b010ede7
FROM python:3.12.11-slim-bookworm
COPY --from=source /src/mm-adapter /app
RUN pip install --no-cache-dir -r /app/requirements.txt && useradd -u 1000 -m adapter
USER 1000:1000
ENTRYPOINT ["python","/app/adapter.py","--config","/config/mm-adapter.yaml"]
