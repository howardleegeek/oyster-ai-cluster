# WhatsApp Web Sender (free)

This sends WhatsApp messages via **WhatsApp Web** using a **persistent Chrome profile**.

- Free (no Twilio / WhatsApp Business API).
- Requires logging in once (QR scan, or phone-number login).

## Setup

```bash
cd /Users/howardli/Downloads/whatsapp-web-sender
npm install
```

## Login (QR)

```bash
node send.mjs --login-only --live-qr --wait-login-secs 900
```

It will print a **local live-QR URL** you can open in your normal browser (recommended), plus QR screenshot paths.

Scan with:

- WhatsApp Mobile -> Settings -> Linked devices -> Link a device

## Login (phone number)

If scanning QR is blocked for you:

```bash
node send.mjs --login-method phone --login-phone "+<countrycode><number>" --login-only --wait-login-secs 900
```

Follow the on-phone linking flow it shows.

## Send a message

```bash
node send.mjs --to "+14155551234" --text "hello from codex" \
  --wait-login-secs 30
```

## Dry run

```bash
node send.mjs --to "+14155551234" --text "hello" --dry-run
```

Artifacts are written to `output/`.
