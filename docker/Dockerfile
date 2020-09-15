FROM python:3.8

USER root
WORKDIR /root

# Install libraries
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
        yamllint \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY . .

# Set up python environment
RUN pip install -U pip \
    && pip install -e .

ENTRYPOINT ["dbl"]
CMD ["--help"]
