FROM docker.io/alpine:3.24.0

RUN apk add --no-cache python3 py3-pip

WORKDIR /bdd

RUN python3 -m venv venv
ADD requirements.txt /bdd/
RUN ./venv/bin/python3 -m pip install -r requirements.txt

ADD spellbook /bdd/spellbook

EXPOSE 8080
ENTRYPOINT ["/bdd/venv/bin/python3", "-m", "spellbook", "--port=8080", "--config=/data/spellbook.yaml"]
