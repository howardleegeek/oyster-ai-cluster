/**
 * GLM-4.6V Vision Helper for Discord Playwright Automation
 *
 * Lightweight module that sends Playwright screenshots to z.ai GLM-4.6V-Flash
 * for vision-based UI element detection. Use as fallback when CSS selectors fail.
 *
 * Usage:
 *   import { askGLMVision } from "./glm_vision_helper.mjs";
 *   const result = await askGLMVision(page, { goal: "Find and click the Reply button" });
 *   if (result?.action === "click") await page.mouse.click(result.x, result.y);
 *
 * Env vars:
 *   ZAI_API_KEY          — z.ai API key (required)
 *   ZAI_VISION_BASE_URL  — endpoint (default: https://api.z.ai/api/paas/v4)
 *   GLM_VISION_MODEL     — model (default: glm-4.6v-flash)
 */

const DEFAULT_BASE_URL = "https://api.z.ai/api/paas/v4";
const DEFAULT_MODEL = "glm-4.6v-flash";

const SYSTEM_PROMPT = [
  "You are a careful web UI agent analyzing a browser screenshot.",
  "You MUST output exactly one JSON object.",
  "Allowed actions:",
  '- {"action":"click","x":N,"y":N} — click at viewport coordinates',
  '- {"action":"type","x":N,"y":N,"text":"..."} — click then type',
  '- {"action":"not_found"} — target element not visible',
  '- {"action":"done"} — goal already satisfied',
  "Return ONLY the JSON object, no commentary.",
].join("\n");

/**
 * Call z.ai GLM-4.6V API with an image.
 * @param {string} base64Image - JPEG image as base64 string
 * @param {string} prompt - User prompt describing what to find/do
 * @param {object} [opts] - Options: model, baseUrl, apiKey, timeoutMs
 * @returns {object|null} Parsed JSON response or null on failure
 */
export async function callGLMVisionAPI(base64Image, prompt, opts = {}) {
  const apiKey = opts.apiKey || process.env.ZAI_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN;
  if (!apiKey) {
    console.error("[glm_vision] ZAI_API_KEY not set");
    return null;
  }

  const baseUrl = (opts.baseUrl || process.env.ZAI_VISION_BASE_URL || DEFAULT_BASE_URL).replace(/\/+$/, "");
  const model = opts.model || process.env.GLM_VISION_MODEL || DEFAULT_MODEL;
  const timeoutMs = opts.timeoutMs || 30_000;

  const url = `${baseUrl}/chat/completions`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const resp = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          {
            role: "user",
            content: [
              { type: "text", text: prompt },
              { type: "image_url", image_url: { url: `data:image/jpeg;base64,${base64Image}` } },
            ],
          },
        ],
        temperature: 0,
        max_tokens: 512,
      }),
      signal: controller.signal,
    });

    if (!resp.ok) {
      console.error(`[glm_vision] API error: ${resp.status} ${resp.statusText}`);
      return null;
    }

    const data = await resp.json();
    const msg = data?.choices?.[0]?.message || {};
    const text = (msg.content || msg.reasoning_content || "").trim();

    // Extract JSON from response (may be wrapped in markdown fences)
    const jsonMatch = text.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/) || text.match(/(\{[\s\S]*\})/);
    if (!jsonMatch) return null;

    return JSON.parse(jsonMatch[1]);
  } catch (e) {
    if (e.name === "AbortError") {
      console.error("[glm_vision] Request timed out");
    } else {
      console.error(`[glm_vision] Error: ${e.message}`);
    }
    return null;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Take a screenshot of the page and ask GLM-4.6V to find/act on a UI element.
 * @param {import("playwright").Page} page - Playwright page
 * @param {object} opts - { goal: string, model?, baseUrl?, apiKey?, timeoutMs? }
 * @returns {object|null} Action JSON: { action, x?, y?, text? } or null
 */
export async function askGLMVision(page, opts = {}) {
  const { goal, ...apiOpts } = opts;
  if (!goal) {
    console.error("[glm_vision] goal is required");
    return null;
  }

  try {
    const screenshotBuffer = await page.screenshot({ type: "jpeg", quality: 70, fullPage: false });
    const base64Image = screenshotBuffer.toString("base64");
    const prompt = `Goal: ${goal}\n\nAnalyze the screenshot and return the action JSON.`;
    return await callGLMVisionAPI(base64Image, prompt, apiOpts);
  } catch (e) {
    console.error(`[glm_vision] Screenshot/API error: ${e.message}`);
    return null;
  }
}
