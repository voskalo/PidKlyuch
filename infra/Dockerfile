FROM caddy:2-alpine

COPY hello-world/index.html /usr/share/caddy/index.html

EXPOSE 80

CMD ["caddy", "file-server", "--listen", ":80", "--root", "/usr/share/caddy"]
