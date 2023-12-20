#!/bin/bash
mkdir -p static/upload
mkdir -p static/jsons

# Kill the "iso-server" container if it's running
if docker ps --filter "name=iso-server" | grep -q iso-server; then
    docker stop $(docker ps -qa)
    docker kill $(docker ps -qa)
    docker rm $(docker ps -qa)
fi

# Rebuild the Docker image
docker build -t kdn-cfd-server:latest .

# Start the container with the new image
# docker run -d --name iso-server kdn-cfd-server:latest
docker run -it -d --rm --name iso-server -p 8081:5000 -v $(pwd)/static:/app/static kdn-cfd-server:latest
