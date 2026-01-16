FROM ubuntu:24.04

ARG username

RUN useradd -m "$username" && chsh -s /bin/bash "$username"
RUN mkdir "/home/$username/.ssh" -m 700 && chown "$username:$username" "/home/$username/.ssh"

RUN echo "export PATH=$PATH:/home/$username/gitroot/scripts"\
":/home/$username/gitroot/mysql-tools\n" \
'. /usr/share/bash-completion/completions/git' \
>> "/home/$username/.bashrc"

RUN yes | unminimize

# libantlr4-runtime-dev and libudev-dev are needed for mysqlshell

RUN apt update && apt -y install build-essential cmake zlib1g-dev ninja-build \
  libssl-dev libreadline-dev libcurl4-openssl-dev \
  libkrb5-dev libldap-dev libsasl2-dev \
  pkg-config libtirpc-dev bison sudo exuberant-ctags \
  python3 black git pylint lsof net-tools vim file man \
  locate lsb-release tree gdb nano cmake-curses-gui curl \
  inetutils-ping clang-format-15 clang-tidy clangd \
  libantlr4-runtime-dev libudev-dev \
  unzip colordiff

RUN PERL_MM_USE_DEFAULT=1 cpan install JSON.pm

USER "$username"
WORKDIR "/home/$username"
