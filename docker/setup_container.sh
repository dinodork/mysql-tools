#!/bin/bash

image_name=${1:-dev}
container_name=${2:-mydev}
username=${3:-$(whoami)}

home="/home/$username"

echo "Setting up container '$container_name' from image '$image_name' for user '$username'"

copy_file_to_container() {
  source=$1
  target=${home}/$(basename $1)
  docker cp -L "${source}" "${container_name}:$target"
  docker exec -uroot "$container_name" chown "$username:$username" "$target"
}

copy_files_to_container() {
  files=$@
  for file in $files; do
    copy_file_to_container "$file"
  done
}

docker run -d --name "$container_name" \
       -v "$HOME/gitroot:$home/gitroot" \
       -v "$HOME/boost:$home/boost" \
       --cap-add=SYS_PTRACE "$image_name" tail -f /dev/null && \
copy_files_to_container $HOME/.ssh/id_rsa $HOME/.ssh/id_rsa.pub .bash_aliases .gdbinit && \
# Personally, I keep this file in Git and just symlink it
copy_file_to_container "$HOME/.gitconfig"
