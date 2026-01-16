#!/bin/bash

image_name=${1:-dev}
container_name=${2:-mydev}
username=${3:-martin}

home="/home/$username"

docker run -d --name "$container_name" -v "$HOME/gitroot:$home/gitroot" \
       --cap-add=SYS_PTRACE "$image_name" tail -f /dev/null && \
docker cp ~/.ssh/id_rsa "$container_name:$home/.ssh/id_rsa" && \
docker cp ~/.ssh/id_rsa.pub "$container_name:$home/.ssh/id_rsa.pub" && \
docker exec -uroot "$container_name" chown "$username:$username" "$home/.ssh/id_rsa" && \
docker exec -uroot "$container_name" chown "$username:$username" "$home/.ssh/id_rsa.pub"
# Personally, I keep this file in Git and just symlink it
docker -L cp ~/.gitconfig "${container_name}:$home/"
