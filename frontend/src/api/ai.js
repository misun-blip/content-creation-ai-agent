import request from "./index";
import { useUserStore } from "@/stores/user";

/**
 * 生成选题
 * @param {{ keywords: string, industry: string, platform: string, count?: number }} data
 */
export function generateTopics(data) {
  return request.post("/api/v1/ai/topics", data);
}

/**
 * 生成文案（一次性返回）
 * @param {{ topic: string, length?: number, style?: string, platform?: string }} data
 */
export function generateContent(data) {
  return request.post("/api/v1/ai/content", data);
}

/**
 * 流式生成文案（SSE）
 * 使用 fetch + ReadableStream 实现逐字推送
 *
 * @param {{ topic: string, length?: number, style?: string, platform?: string }} data - 请求参数
 * @param {{ onMessage: (text: string) => void, onDone?: () => void, onError?: (err: Error) => void }} callbacks - 回调
 * @returns {{ abort: () => void }} 返回可取消的控制器
 */
export function generateContentStream(data, { onMessage, onDone, onError }) {
  const controller = new AbortController();
  const userStore = useUserStore();

  fetch("/api/v1/ai/content/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(userStore.token ? { Authorization: `Bearer ${userStore.token}` } : {}),
    },
    body: JSON.stringify(data),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        // 保留最后一行（可能不完整）
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith("data: ")) continue;

          const payload = trimmed.slice(6); // 去掉 "data: "
          if (payload === "[DONE]") {
            onDone?.();
            return;
          }

          try {
            const parsed = JSON.parse(payload);
            if (parsed.error) {
              onError?.(new Error(parsed.error));
              return;
            }
            if (parsed.content) {
              onMessage(parsed.content);
            }
          } catch {
            // 忽略非 JSON 行
          }
        }
      }

      // 流正常结束但没收到 [DONE]
      onDone?.();
    })
    .catch((err) => {
      if (err.name === "AbortError") return;
      onError?.(err);
    });

  return { abort: () => controller.abort() };
}

/**
 * 内容质量评估
 * @param {{ content: string }} data
 */
export function evaluateContent(data) {
  return request.post("/api/v1/ai/evaluate", data);
}

/**
 * AI 智能配图
 * @param {{ topic: string, count?: number, platform?: string }} data
 */
export function generateImages(data) {
  return request.post("/api/v1/ai/image", data);
}
