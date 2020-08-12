# tokman

A token manager for GitHub Applications.

## The problem

When Packit Service is accessing repositories on behalf of our users, it
authenticates with an access token retrieved using the GitHub App ID and the
GitHub App Private Key.

Tokens expire after 60 minutes or when a new token is retrieved for the same
repository.

The later creates a race condition when multiple Packit Service workers are
performing tasks on the same repository: as soon as a worker retrieves a new
token, the tokens held by the other workers for the same repository become
invalid, and any operation they might attempt with these tokens will result in
a `401 Bad Credentials` error.

`tokman` aims to solve the issue above, by factoring out the token retrieval
in a single, internal service, running alongside Packit Service. When workers
need a token to access a repository, they call the `tokman` API to retrieve
it. `tokman` handles requesting the tokens and renewing them when (or some
time before) they expire.

`tokman`'s only guarantee about the tokens provided is that they are valid at
the time of the retrieval.

Tokens might expire though or become invalid (b/c `tokman` itself was
restarted).

Users of the API are responsible requesting a new token if a previous token
proves to be invalid.

## API

```
GET <tokman_url>/api/<namespace>/<repository>

200 OK

{
    "namespace": "<namespace>",
    "repository": "<repository>",
    "access_token": "<...>"
}

400 BAD REQUEST

{
    "error": "Failed to retrieve a token: App is not installed on <namespace>/<repository>"
}
```

## Development

`make build` builds the image.

`make re-build` builds the image ignoring any cache and making sure the latest
base image pulled.

Before running the app locally, make sure you create `config.py` by making a
copy of `config.py.example`. Update the value of `GITHUB_APP_ID` with the
ID of the GitHub App you want to use. Copy to corresponding private key in the
current directory as `private-key.pem` or indicate the directory where it's
stored by setting `SECRETS_DIR`.

Start the application container with `make run`.

The number of worker threads started by gunicorn can be controlled by setting
`WORKERS`.

The logging level used can be configured by setting `LOG_LEVEL` to "info",
"warning", "debug".

For development purposes you can also use `flask run` to run the application.
Before doing so:

- Create and activate a Python virtual environment (with `mkvirtualenv tokman`, for example).
- Install the app and the dependencies in the environment: `pip install -e .`
- Configure flask for development mode: `export FLASK_ENV=development`.

[link]: https://docs.github.com/en/developers/apps/authenticating-with-github-apps#authenticating-as-a-github-app
[installation tokens]: https://docs.github.com/en/rest/reference/apps#create-an-installation-access-token-for-an-app
