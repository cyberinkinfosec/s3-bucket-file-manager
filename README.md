# S3-Bucket-file-manager

Most Pentesters end up juggling multiple terminal tabs, the AWS CLI, and the S3 console just to check what a set of IAM credentials can actually reach across several buckets. This is a single-file solution to that problem — a lightweight Flask web UI that lets you manage files across multiple S3 buckets from one dashboard.

## Features

- Browse multiple S3 buckets from one dashboard
- Folder-style navigation (prefix-based)
- Search files by name
- Filter by date range (last modified)
- Preview files inline (images, PDFs, text, etc.)
- Upload / download / delete objects

## Requirements

- Python 3.8+
- `flask`
- `boto3`

```bash
pip install flask boto3
```

## Setup

1. Clone the repo
2. Open the script and set your bucket list:
   ```python
   S3_BUCKETS = [
       "your-bucket-1",
       "your-bucket-2"
   ]
   ```
3. Provide credentials — **don't hardcode them in the file**. Use environment variables or an AWS profile instead:
   ```bash
   export AWS_ACCESS_KEY_ID=your-key
   export AWS_SECRET_ACCESS_KEY=your-secret
   ```
   and drop the `aws_access_key_id` / `aws_secret_access_key` args from the `boto3.client()` call so it picks up credentials from the environment automatically.

## Usage

```bash
python3 app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Notes

- Intended for local/authorized use only — there's no authentication layer on the web UI itself, so don't expose this on a public interface.
- Useful for quickly confirming the real-world scope of a given IAM key's S3 permissions (list/get/put/delete) during an authorized assessment.
