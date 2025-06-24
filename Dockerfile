FROM ghcr.io/astral-sh/uv:debian AS uv

WORKDIR /docs

ARG GIT_COMMITTERS_ENABLED=true

COPY pyproject.toml .
COPY uv.lock .

RUN apt-get update && apt-get install -y git && \
    uv sync --no-default-groups --group docs

COPY mkdocs.yml .
COPY docs/ docs/
COPY docs-resources/ docs-resources/

COPY .git .git

RUN --mount=type=cache,target=.cache/plugin/git-committers \
    --mount=type=secret,id=mkdocs_git_committers_apikey,env=MKDOCS_GIT_COMMITTERS_APIKEY \
    uv run mkdocs build --strict

FROM nginx:alpine

COPY --from=0 /docs/site /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 