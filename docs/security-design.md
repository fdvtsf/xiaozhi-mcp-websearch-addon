# Security Design

## Boundaries

This add-on only performs public web search and public URL text extraction. It does not:

- Read Home Assistant entities.
- Call Home Assistant APIs.
- Call Supervisor APIs.
- Control devices.
- Access local files through URL schemes.
- Download binary files to disk.

## Safe mode

`safe_mode=true` is enabled by default. It blocks:

- `127.0.0.0/8`
- `localhost`
- `0.0.0.0`
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`
- IPv6 loopback, private, link-local, multicast, reserved, and unspecified addresses
- link-local and metadata addresses such as `169.254.169.254`
- Home Assistant and Supervisor hostnames such as `homeassistant`, `hassio`, and `supervisor`
- Common router setup hostnames

Every redirect target is checked before the next request is made.

## URL rules

`fetch_url` only accepts `http` and `https`. It rejects `file://`, `ftp://`, `data://`, embedded credentials, empty URLs, and private network destinations.

## Response rules

The fetcher sets a User-Agent, timeout, response byte limit, and output character limit. HTML is parsed as text only; scripts are never executed. PDF, image, video, audio, archive, octet-stream, and executable-like content types are rejected.

## Secrets

Bocha, Baidu Qianfan, Brave, and future tokens must come from add-on options. Secrets are not hard-coded. Configuration summaries and logging pass through redaction helpers so keys, bearer tokens, passwords, and secrets are replaced with `***`.
