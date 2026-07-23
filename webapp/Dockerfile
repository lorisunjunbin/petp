FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5555 \
    SHARED_FOLDER=shared

WORKDIR /app

COPY requirements.txt /app/requirements.txt
# Use a China mirror + generous timeout/retries — the default PyPI index is slow
# and TLS-flaky from CN networks, causing "SSL: UNEXPECTED_EOF_WHILE_READING".
RUN pip install --no-cache-dir \
    --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    --timeout 120 --retries 5 \
    -r /app/requirements.txt

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
