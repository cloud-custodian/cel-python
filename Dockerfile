#Dockerfile to create an Ubuntu image with curl, git, vim, and uv
# docker build -t dev-ubuntu .
# docker image prune
# docker run --name working -it dev-ubuntu
# From the interactive prompt, cd /home/cel-python, run commands normally.
# docker container rm working

FROM ubuntu:latest

# Update package manager and install curl command
RUN apt update && apt install -y aptitude
RUN aptitude install -y curl
RUN aptitude install -y git
RUN aptitude install -y vim 

# Install uv using the curl command
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Use GIT to get the package
RUN cd /home && git clone https://github.com/cloud-custodian/cel-python.git

# Run the bash terminal on container startup
CMD /bin/bash

