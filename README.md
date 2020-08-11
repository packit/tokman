# tokman

A token manager for GitHub Applications.

## The problem

When Packit Service is accessing repositories on behalf of our users, it
authenticates with an access token retrieved using the GitHub App ID and the
GitHub App Private Key.

Tokens expire after 10 minutes or when a new token is retrieved for the same
repository.

The later creates a race condition when multiple Packit Service workers are
performing tasks on the same repository: as soon as a worker retrieves a new
token, the tokens held by the other workers for the same repository become
invalid, and any operation they might attempt with these tokens will result in
a `401 Bad Credentials` error.

`tokman` aims to solve the issue above, by factoring out the token retrieval
in a single, internal service, running alongside Packit Service. When workers
need a token to access a repository, they call the `tokman` API to retrieve
it. `tokman` handles requesting the tokens and renewing them when they expire.

`tokman`'s only guarantee about the tokens provided is that they are valid at
the time of the retrieval.

Tokens might expire though or become invalid (b/c `tokman` itself was
restarted).

Users of the API are responsible requesting a new token if a previous token
proves to be invalid.

## API

GET `tokman.<namespace>.svc/api/<namespace>/<repository>`

Response:

{
"namespace": "<namespace>",
"repository": "<namespace>",
"access_token": "..."
}

[link]: https://docs.github.com/en/developers/apps/authenticating-with-github-apps#authenticating-as-a-github-app
[installation tokens]: https://docs.github.com/en/rest/reference/apps#create-an-installation-access-token-for-an-app
