# Tools and utilities for working with the MySQL Source code

This repo contains scripts to make life simpler if you need to work with MySQL
doing typical development chores, such as stopping and starting mysqld and the
client. Especially if you need to jump back and forth between versions.

Ideally, in order to start the server, you should just need to type
`sqld`. Likewise, just typing `sqlc` should start the client

- `sqld` starts the server, and is meant to work uniformly across version, from
  5.7 all the way up to current trunk. It also lets you create the database.

- `sqlc` starts the client.

There is also a `Dockerfile` and scripts to build a container that is ready
for building MySQL.
