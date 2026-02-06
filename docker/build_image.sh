#!/bin/bash

image_name=${1:-dev}
username=${2:-$(whoami)}

echo "Building image '$image_name' for user '$username'"

docker build . -t "$image_name" --build-arg username="$username"
