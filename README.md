# Fider for Unraid

A Docker template for [Fider](https://github.com/getfider/fider), using `getfider/fider:stable`. This repository supplies the Unraid template, not the Fider application. Template code and documentation use the MIT license; Fider and the copied Fider logo use AGPL-3.0. The repository icon is a generic feedback symbol. The Fider application icon is an unchanged copy of the official project's `etc/logo.png`; see [asset attribution](icons/README.md).

## Installation

Use the repository's Community Applications listing once accepted, or add this repository URL under Unraid's Docker template repositories and select Fider. If your Unraid version does not offer that interface, copy `templates/fider.xml` to `/boot/config/plugins/dockerMan/templates-user/my-fider.xml` and select it using Docker > Add Container > Template.

1. Provision PostgreSQL separately, with persistent storage and backups. This template does not create a database or PostgreSQL container.
2. Set `BASE_URL` to your public URL. Behind a reverse proxy, use its HTTPS URL and route it to the mapped HTTP port (default 3000).
3. Set `DATABASE_URL` to a PostgreSQL URL with your own reachable hostname and credentials. `localhost` refers to Fider's container. Use a shared Docker network for container DNS, or the database server's reachable address. Percent-encode reserved characters in credentials. Choose PostgreSQL TLS options appropriate to your server; do not disable TLS for a remote untrusted connection.
4. Generate `JWT_SECRET` with `openssl rand -hex 32`; paste the result into the masked field. Keep it stable and private.
5. Set `EMAIL_NOREPLY` and your SMTP settings. Start Fider and create your site. Then optionally enable `SIGNUP_DISABLED` to disable creation of additional sites; users can still sign in to existing sites.

The PostgreSQL field starts with `postgres://USERNAME:PASSWORD@HOST:5432/DATABASE` as a format example. Replace all four uppercase values before starting Fider; this does not provision a database. Other required values are intentionally blank. Masking hides values in the Unraid form; it does not encrypt Docker environment variables. Protect template files, Docker access and backups.

## Email

SMTP is selected explicitly by default. For port 587 use STARTTLS=true and implicit TLS=false. For port 465 set STARTTLS=false and implicit TLS=true. Username and password may be blank for a server that permits unauthenticated delivery. SMTP host and port are required by Fider for SMTP, but are optional in the Unraid form to permit other providers.

Switch Advanced View on to change `EMAIL`. Add provider variables with **Add another Path, Port, Variable, Label or Device**, choosing Variable:

| Provider | EMAIL | Variables to add |
| --- | --- | --- |
| Mailgun | mailgun | EMAIL_MAILGUN_API, EMAIL_MAILGUN_DOMAIN, EMAIL_MAILGUN_REGION (US or EU) |
| Amazon SES | awsses | EMAIL_AWSSES_REGION, EMAIL_AWSSES_ACCESS_KEY_ID, EMAIL_AWSSES_SECRET_ACCESS_KEY |

Mask API keys and secret access keys. Verify sender identity and provider delivery permissions (including SES sandbox restrictions). Unused SMTP fields can be removed. `EMAIL_ALLOWLIST` and `EMAIL_BLOCKLIST` optionally filter recipients using regular expressions; allowlist takes precedence.

## Storage and backups

`BLOB_STORAGE=sql` stores images and logos in PostgreSQL, so no application data volume is needed. Back up the database and deployment configuration.

For filesystem storage set `BLOB_STORAGE=fs`, add `BLOB_STORAGE_FS_PATH=/app/uploads`, and add a read/write Path mapping from a persistent host directory such as `/mnt/user/appdata/fider/uploads` to `/app/uploads`. Ensure the container can write there and back it up.

For S3 set `BLOB_STORAGE=s3` and add `BLOB_STORAGE_S3_ENDPOINT_URL`, `BLOB_STORAGE_S3_REGION`, `BLOB_STORAGE_S3_ACCESS_KEY_ID`, `BLOB_STORAGE_S3_SECRET_ACCESS_KEY`, and `BLOB_STORAGE_S3_BUCKET`. Mask credentials. Use the endpoint and region for your S3-compatible provider. Back up the bucket as needed.

Changing the storage backend does not migrate existing uploads. Plan migration separately before changing it.

## HTTPS and advanced settings

`SSL_AUTO=false` is the default for SWAG, Nginx Proxy Manager or Traefik. Terminate HTTPS at your proxy. Direct Let's Encrypt operation requires Fider to be reachable on ports 80 and 443 and additional port mappings; toggling SSL_AUTO alone is insufficient. Manual certificates use SSL_CERT and SSL_CERT_KEY relative to `/app/etc` and require a suitable certificate mount.

The template exposes locale, logging, metrics and site creation controls in Advanced View. Other variables can be added manually. Keep the internal PORT at 3000 unless you also update the container port mapping and WebUI template reference. Fider reads environment variables at startup: apply changes through Unraid to recreate the container. For Compose deployments, use `docker compose up -d`.

The supplied environment variable reference is the configuration basis. Check compatibility against the Fider release you deploy; the stable tag can change. No live Fider/PostgreSQL/SMTP integration test is included.

## Validation and Community Applications

Run `python3 scripts/validate_templates.py`. GitHub Actions runs the same check on pushes and pull requests: XML syntax, required fields, unique Config targets, masked secrets, matching port references and repository URLs without starter placeholders. This is a repository check, not the official CA scanner.

After merging, run Validate and Scan in the Community Applications submission flow. Confirm the raw main-branch URLs resolve and test installation on Unraid before submitting. Report template problems through this repository's Issues; report application bugs upstream.
