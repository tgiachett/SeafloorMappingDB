FROM traefik:v2.4.11
RUN mkdir -p /etc/traefik/acme \
  && touch /etc/traefik/acme/acme.json \
  && chmod 600 /etc/traefik/acme/acme.json
COPY ./compose/production/traefik/traefik.yml /etc/traefik
COPY ./compose/production/traefik/smdb.crt /certs/
COPY ./compose/production/traefik/smdb.key /certs/
