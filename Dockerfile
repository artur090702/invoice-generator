FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    texlive-latex-extra texlive-latex-recommended \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN ./install.sh

CMD ["python3", "app.py"]
