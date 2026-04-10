# check=skip=SecretsUsedInArgOrEnv
FROM ubuntu:26.04

ARG username

RUN useradd -m "$username" && chsh -s /bin/bash "$username"
RUN mkdir "/home/$username/.ssh" -m 700 && chown "$username:$username" "/home/$username/.ssh"

RUN echo \
"\n"\
"export PATH=$PATH:/home/$username/gitroot/scripts"\
":/home/$username/gitroot/mysql-tools\n"\
"\n"\
'. /usr/share/bash-completion/completions/git\n'\
>> "/home/$username/.bashrc"

# libantlr4-runtime-dev and libudev-dev are needed for mysqlshell

RUN apt update && apt -y install build-essential cmake zlib1g-dev ninja-build \
  libssl-dev libreadline-dev libcurl4-openssl-dev libkrb5-dev libldap-dev \
  libsasl2-dev pkg-config libtirpc-dev bison sudo exuberant-ctags python3 \
  black git pylint lsof net-tools vim file man locate lsb-release tree gdb \
  nano cmake-curses-gui curl inetutils-ping clang-tidy \
  clangd libantlr4-runtime-dev libudev-dev unzip colordiff locales \
  libexpat1-dev ccache valgrind mold clang \
  && sed -i 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
  && locale-gen en_US.UTF-8 \
  && update-locale LANG=en_US.UTF-8 \
  && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV SSH_AUTH_SOCK=/ssh-agent

USER "$username"
WORKDIR "/home/$username"
