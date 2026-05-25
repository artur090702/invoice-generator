FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash python3-flask python3-venv texlive-latex-extra texlive-latex-recommended \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN ./install.sh

CMD ["/root/.local/share/geninvoice/venv/bin/python3", "app.py"]
