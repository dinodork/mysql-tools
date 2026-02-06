#!/bin/bash

image_name=${1:-dev}
container_name=${2:-mydev}
username=${3:-$(whoami)}

home="/home/$username"

echo "Setting up container '$container_name' from image '$image_name' for user '$username'"

docker run -d --name "$container_name" \
       -v "$HOME/gitroot:$home/gitroot" \
       -v "$HOME/boost:$home/boost" \
       --cap-add=SYS_PTRACE "$image_name" tail -f /dev/null && \
docker cp ~/.ssh/id_rsa "$container_name:$home/.ssh/id_rsa" && \
docker cp ~/.ssh/id_rsa.pub "$container_name:$home/.ssh/id_rsa.pub" && \
docker exec -uroot "$container_name" chown "$username:$username" "$home/.ssh/id_rsa" && \
docker exec -uroot "$container_name" chown "$username:$username" "$home/.ssh/id_rsa.pub"
# Personally, I keep this file in Git and just symlink it
docker cp -L ~/.gitconfig "${container_name}:$home/"
