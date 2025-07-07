FROM golang:1.24

ENV HOME=/usr/cel-python
WORKDIR $HOME/tools

# pre-copy/cache go.mod for pre-downloading dependencies and only redownloading them in subsequent builds if they change
COPY go.mod go.sum ./
RUN go mod download

COPY ./*.go .
RUN go build -v -o /usr/local/bin/mkgherkin ./...

WORKDIR $HOME/textproto
ENTRYPOINT ["mkgherkin"]
