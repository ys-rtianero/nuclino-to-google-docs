# Nuclino to Google Docs Sync

This repository contains a simple Python script that reads the contents of a Nuclino workspace and replicates those pages as Google Docs inside a chosen Google Drive folder.

## Requirements

* Python 3.8+
* `requests`
* `google-api-python-client`
* A Nuclino API token
* Google service account credentials with access to Drive and Docs

Install dependencies:

```bash
pip install requests google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Usage

Set the required credentials either via command line flags or environment variables.

```
NUCLINO_TOKEN=<nuclino-token>
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

Then run the script:

```bash
python nuclino_to_google_docs.py <workspace_id> <drive_folder_id>
```

All items inside the Nuclino workspace will be converted into Google Docs within the provided Drive folder. The document text is inserted at index `1` of the newly created Google Doc.
