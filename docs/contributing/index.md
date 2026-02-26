# Contributing Documentation

Thank you for your interest in contributing to ClanGen's documentation!

## Getting Started

### Editing Pages

To make a change in the documentation, just edit the corresponding `.md` file in the `/docs` folder. Note that every page has an edit button (:material-file-edit-outline:) in the top right that will take you directly to its corresponding file.

### Creating New Pages

If you want to create a new page, create a new `.md` file. Then edit `mkdocs.yml` (in the main clangen folder) to add your new page to the navigation on the sidebar.

### Additional Resources

[Documentation Resources](documentation-resources.md){ .md-button .md-button--primary}

## Build Instructions

!!! important
    If you only want to contribute documentation, you don't **have** to do this. Building the documentation creates a local copy of the documentation website on your computer, which can be useful for previewing your changes, but isn't necessarily required.

### Using uv

1. Install uv (see [CONTRIBUTING.md](https://github.com/ClanGenOfficial/clangen/blob/development/CONTRIBUTING.md) for details).
2. Install dependencies:
   ```
   uv sync --group docs
   ```
3. Build and serve documentation:
   ```
   uv run mkdocs serve
   ```
   Running this command will build the documentation and start a local server on your computer. While the server is running, you can access the documentation at [http://localhost:8000](http://localhost:8000). The site will update whenever the files in `/docs` are changed.

### Using Docker

1. Install [Docker](https://www.docker.com).
2. Build image:
   ```
   docker buildx build . -t clangen-docs
   ```
3. Run server:
   ```
   docker run -p 8000:80 clangen-docs
   ```
4. You can access the documentation at [http://localhost:8000](http://localhost:8000). Unlike with uv, this site will *not* update when the files in `/docs` are changed. To update the site, you have to close the server, then rebuild the image and run the server again.
