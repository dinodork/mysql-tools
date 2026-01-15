#!/bin/bash

image_name=${1:-dev}
username=${2:-martin}

docker build . -t "$image_name" --build-arg username="$username"
