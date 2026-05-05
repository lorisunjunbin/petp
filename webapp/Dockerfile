FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5555 \
    SHARED_FOLDER=shared

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Ensure required images are copied during packaging by a Python script.
RUN python /app/scripts/prepare_assets.py \
    --source /app/build_assets \
    --target /app/static/images \
    --files PETP_overview.png PETP_overview_windows.png \
            HTTP_SERVICE_ENABLED.png petp_as_standard_mcp_server.png \
            claude-code-mcp-tool.png DEEPSEEK-MCP.png user_manual.png

EXPOSE 5555

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 2 app:app"]
