# Claw Nation Node (Web)

Goal: use OysterRepublic's phone fleet as the fastest way to get global camera coverage.

## Run locally

1. Start relay:

```bash
cd /Users/howardli/Downloads/claw-nation/relay
node src/server.js
```

2. Open the web node page:

- Open `/Users/howardli/Downloads/claw-nation/node-web/index.html` in a browser.
- Set `Relay Base URL` to `http://127.0.0.1:8787`.
- Click `Register Node` then `Start Mapping`.

3. Open the world heatmap:

- Open `/Users/howardli/Downloads/claw-nation/node-web/map.html` in a browser.
- Set `Relay Base URL` to `http://127.0.0.1:8787`.
- It calls `GET /v1/world/cells` and renders an H3 hex overlay heatmap.

## Deploy (recommended)

To use on real phones, host both:

- Relay behind HTTPS
- This page behind HTTPS (or serve it from the relay domain)

Because mobile browsers require HTTPS for camera + GPS.

## Data model

Each phone publishes `frame` events:

- `lat/lon` + `h3_res` -> server computes `cell`
- `jpeg_base64` -> relay stores `/v1/blobs/<event_id>.jpg` and logs metadata

Query:

- `GET /v1/world/events?cell=<h3>&limit=50`
- `GET /v1/world/cells?res=9&limit=5000&hours=24`
- `GET /v1/world/stats?res=9&hours=24`
