FROM python:3.12.11-alpine3.22@sha256:9ba6d8cbebf0fb6546ae71f2a1c14f6ffd2fdab83af7fa5669734ef30ad48844
WORKDIR /app
COPY app.py index.html ./
USER 1000:1000
HEALTHCHECK CMD wget -qO- http://127.0.0.1:8080/health || exit 1
ENTRYPOINT ["python","/app/app.py"]
