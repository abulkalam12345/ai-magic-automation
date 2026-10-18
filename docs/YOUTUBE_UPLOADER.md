# YouTube uploader (not activated)

The repository now contains `src/youtube_publish.py`, a fail-closed YouTube Data API adapter. It is deliberately **not called by the daily draft workflow** and no OAuth credentials have been created or added.

## Default behavior

Without `--upload`, the script only validates the MP4 and metadata and prints a dry-run summary. It makes no network request. An upload requires all of the following:

- `--upload` command-line flag.
- GitHub Actions/runtime secret `YOUTUBE_OAUTH_TOKEN_JSON` containing an authorized-user OAuth token JSON object with the `youtube.upload` scope.
- `PUBLISHING_ENABLED=true`.
- `YOUTUBE_AUTOMATION_AUTHORIZED=true`.

The default visibility is **private**. Public visibility additionally requires `--public` and `YOUTUBE_PUBLIC_PUBLISHING_APPROVED=true`. The repository does not set these variables and the workflow does not call the uploader.

## Local dry-run

Install optional dependencies only if needed:

```sh
python -m pip install -r requirements-youtube.txt
python src/youtube_publish.py --video path/to/final.mp4 --metadata path/to/metadata.json
```

## OAuth and secrets

Use Google's official OAuth flow for the intended YouTube channel and request only the `https://www.googleapis.com/auth/youtube.upload` scope. Do not paste tokens, client secrets, passwords, or cookies into chat or commit them. Store authorized token JSON only as a protected GitHub Actions secret after the channel owner has completed the official consent flow. Revoke tokens if exposed.

The app's OAuth consent configuration and any required Google verification must be completed in the Google Cloud project. API quota and successful API calls do not guarantee public upload eligibility for every project/channel.

## Current blockers

- No OAuth client or authorized channel token is configured.
- No YouTube upload has been attempted.
- No generated MP4 currently exists in the draft pipeline.
- No public-publishing runtime gates are enabled.
- The adapter has unit tests for metadata validation and fail-closed gates, but the live API path has not been exercised.

Never add this script to the scheduled workflow until OAuth is configured, a private test upload is explicitly approved and verified, and the zero-cost/API quota requirements are confirmed.
