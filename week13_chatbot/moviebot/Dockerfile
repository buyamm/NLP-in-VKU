# ============================================================
# Dockerfile for Rasa server
# Base image: rasa/rasa:3.6.4
# ============================================================

FROM rasa/rasa:3.6.4

# Switch to root so we can copy files and set permissions
USER root

WORKDIR /app

# Copy all project files into the image
# (config.yml, domain.yml, data/, etc. are baked in — no bind mounts needed)
COPY --chown=root:root . /app

# Rasa 3.x writes assistant_id back to config.yml on first train/run.
# Make sure the file is writable.
RUN chmod 666 /app/config.yml

# Expose Rasa HTTP API port
EXPOSE 5005

# Stay as root so Rasa can write config.yml freely
# (acceptable for a local dev / demo container)
CMD ["run", "--enable-api", "--cors", "*", "--debug", \
     "--endpoints", "endpoints.yml", \
     "--credentials", "credentials.yml"]
