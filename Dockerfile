FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Fix Streamlit config and fallback locations
ENV XDG_CONFIG_HOME=/app/.config
ENV HOME=/app
ENV STREAMLIT_HOME=/app

RUN mkdir -p /app/.config \
    && mkdir -p /app/.streamlit \
    && chmod -R 777 /app/.config /app/.streamlit

# Optional: turn off telemetry
RUN echo "[browser]\ngatherUsageStats = false" > /app/.streamlit/config.toml

EXPOSE 8000 8501

CMD ["sh", "-c", "uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0"]

