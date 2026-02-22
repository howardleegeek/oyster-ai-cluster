# Android SSE Streaming Chat — Codex Spec

## Task
Switch Android ChatActivity from non-streaming `/chat` to SSE streaming `/chat/stream` for a typewriter effect. Users should see text appear character-by-character instead of waiting 5+ seconds for the full response.

## Background
- Server SSE endpoint **already exists**: `POST /v1/conversations/{id}/chat/stream`
- Current Android client uses `ClawPhonesAPI.chat()` (blocking HTTP POST to `/chat`)
- ChatActivity already has `updateAssistantMessage(idx, text)` for progressive updates
- The "思考中…" placeholder currently shows for 5+ seconds before the full response replaces it

## SSE Protocol (Server Already Implements)
```
POST /v1/conversations/{conversationId}/chat/stream
Authorization: Bearer <token>
Content-Type: application/json
Body: {"message": "user text"}

Response: text/event-stream

# Progress events (one per character):
data: {"delta": "H", "done": false}
data: {"delta": "e", "done": false}
data: {"delta": "l", "done": false}
...

# Keepalive (every 15s idle):
: keepalive

# Final event:
data: {"delta": "", "done": true, "message_id": "uuid", "content": "full text"}

# Error events:
data: {"error": "daily quota exceeded", "done": true}
data: {"error": "Internal error"}
```

## Files to Modify

### 1. `ClawPhonesAPI.java` — Add streaming method
Path: `app/src/main/java/ai/clawphones/agent/chat/ClawPhonesAPI.java`

Add a new method alongside existing `chat()`:

```java
/**
 * Callback interface for SSE streaming chat responses.
 */
public interface StreamCallback {
    /** Called on each text delta (may be called hundreds of times). */
    void onDelta(String delta);
    /** Called once when streaming completes with the full content. */
    void onComplete(String fullContent, String messageId);
    /** Called on error (network, API, or stream parse error). */
    void onError(Exception error);
}

/**
 * POST /v1/conversations/{id}/chat/stream -> SSE streaming response.
 * Must be called from a background thread. Callbacks fire on the calling thread.
 */
public static void chatStream(String token, String conversationId, String message, StreamCallback callback) {
    // Implementation notes:
    // 1. Open HttpURLConnection to BASE_URL + "/v1/conversations/" + conversationId + "/chat/stream"
    // 2. Set method POST, Content-Type: application/json, Authorization: Bearer token
    // 3. Set Accept: text/event-stream
    // 4. Write body: {"message": "<user text>"}
    // 5. Read response line by line with BufferedReader
    // 6. Parse SSE format: lines starting with "data: " contain JSON
    //    - Skip empty lines and lines starting with ":" (comments/keepalive)
    // 7. Parse each data JSON:
    //    - If has "error" key -> throw ApiException
    //    - If "done" == false -> call callback.onDelta(delta)
    //    - If "done" == true -> call callback.onComplete(content, messageId)
    // 8. READ_TIMEOUT should be longer for streaming (120_000ms or more)
    //    since responses can take 30+ seconds for long answers
}
```

### 2. `ChatActivity.java` — Switch onSend() to streaming
Path: `app/src/main/java/ai/clawphones/agent/chat/ChatActivity.java`

Modify the `onSend()` method (line ~182):

**Before** (current):
```java
execSafe(() -> {
    try {
        String reply = ClawPhonesAPI.chat(mToken, mConversationId, text);
        runSafe(() -> {
            updateAssistantMessage(idx, reply);
            mBusy = false;
            setInputEnabled(true);
        });
    } catch (...) { ... }
});
```

**After** (streaming):
```java
execSafe(() -> {
    // Use StringBuilder to accumulate deltas
    final StringBuilder accumulated = new StringBuilder();

    ClawPhonesAPI.chatStream(mToken, mConversationId, text, new ClawPhonesAPI.StreamCallback() {
        @Override
        public void onDelta(String delta) {
            accumulated.append(delta);
            final String current = accumulated.toString();
            runSafe(() -> updateAssistantMessage(idx, current));
        }

        @Override
        public void onComplete(String fullContent, String messageId) {
            runSafe(() -> {
                // Use the authoritative full content from server (not accumulated)
                updateAssistantMessage(idx, fullContent != null ? fullContent : accumulated.toString());
                mBusy = false;
                setInputEnabled(true);
            });
        }

        @Override
        public void onError(Exception error) {
            runSafe(() -> {
                if (error instanceof ClawPhonesAPI.ApiException && ((ClawPhonesAPI.ApiException)error).statusCode == 401) {
                    ClawPhonesAPI.clearToken(ChatActivity.this);
                    redirectToLogin("登录已过期，请重新登录");
                    return;
                }
                String partial = accumulated.toString();
                if (!partial.isEmpty()) {
                    updateAssistantMessage(idx, partial + "\n\n⚠ 连接中断");
                } else {
                    updateAssistantMessage(idx, "请求失败: " + error.getMessage());
                }
                mBusy = false;
                setInputEnabled(true);
            });
        }
    });
});
```

### 3. Performance: Throttle UI updates
`updateAssistantMessage` calls `notifyItemChanged` which triggers RecyclerView rebind + Markdown rendering. At character-per-event rate, this could be 100+ updates/second — too many.

**Add throttling** in ChatActivity:
```java
private long mLastUpdateMs = 0;
private Runnable mPendingUpdate = null;
private static final long UPDATE_THROTTLE_MS = 50; // 20 FPS max

private void updateAssistantMessageThrottled(int index, String text) {
    if (index < 0 || index >= mMessages.size()) return;
    mMessages.get(index).text = text;

    long now = System.currentTimeMillis();
    if (now - mLastUpdateMs >= UPDATE_THROTTLE_MS) {
        mLastUpdateMs = now;
        mMainHandler.removeCallbacks(mPendingUpdate); // cancel any pending
        mAdapter.notifyItemChanged(index);
        scrollToBottom();
    } else {
        // Schedule a trailing update
        if (mPendingUpdate != null) mMainHandler.removeCallbacks(mPendingUpdate);
        mPendingUpdate = () -> {
            mLastUpdateMs = System.currentTimeMillis();
            mAdapter.notifyItemChanged(index);
            scrollToBottom();
        };
        mMainHandler.postDelayed(mPendingUpdate, UPDATE_THROTTLE_MS);
    }
}
```

Use `updateAssistantMessageThrottled` in `onDelta` callback, but keep `updateAssistantMessage` (immediate) for `onComplete`.

## Acceptance Criteria
- [ ] User sends message -> "思考中…" placeholder appears
- [ ] Within 1-2 seconds, text starts appearing character by character (typewriter effect)
- [ ] Full response replaces accumulated text when done
- [ ] Error during streaming shows partial content + warning
- [ ] 401 error still triggers auto-logout
- [ ] UI stays responsive during streaming (no ANR)
- [ ] `./gradlew assembleDebug` succeeds
- [ ] Existing non-streaming `chat()` method preserved (not deleted) for fallback

## Important Notes
- Do NOT modify server.py — the SSE endpoint already works
- Keep existing `ClawPhonesAPI.chat()` method — only ADD `chatStream()`
- The SSE format uses `data: {json}\n\n` — standard Server-Sent Events
- Lines starting with `:` are SSE comments (keepalive), skip them
- Empty lines are SSE event boundaries, skip them
- READ_TIMEOUT_MS for streaming should be 120_000 (2 min) since long responses take time
- Thread safety: onDelta is called from background thread, must `runSafe()` to update UI
