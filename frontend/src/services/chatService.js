import api from "./api";

export async function startSession(participantId, condition) {
  const response = await api.post("/api/sessions", {
    participant_id: participantId,
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
