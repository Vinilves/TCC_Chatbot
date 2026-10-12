import api from "./api";

export async function startSession(condition) {
  const response = await api.post("/api/sessions", {
    condition,
  });

  return response.data;
}

export async function sendMessage(sessionId, question, debugMode = false) {
  const response = await api.post(
    "/api/chat/messages",
    {
      session_id: sessionId,
      question,
    },
    {
      params: debugMode ? { debug: true } : {},
    }
  );

  return response.data;
}

export async function endSession(sessionId) {
  const response = await api.post(
    `/api/sessions/${sessionId}/end`
  );

  return response.data;
}
