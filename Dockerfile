FROM python:3.12-slim

WORKDIR /docs

ARG GIT_COMMITTERS_ENABLED=true

COPY pyproject.toml .
COPY poetry.lock .

RUN apt-get update && apt-get install -y git && \
    pip install --no-cache-dir poetry && \
    poetry install --no-root --only docs

COPY mkdocs.yml .
COPY docs/ docs/
COPY docs-resources/ docs-resources/

COPY .git .git

RUN --mount=type=cache,target=.cache/plugin/git-committers \
    --mount=type=secret,id=mkdocs_git_committers_apikey,env=MKDOCS_GIT_COMMITTERS_APIKEY \
    poetry run mkdocs build --strict

FROM nginx:alpine

COPY --from=0 /docs/site /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 