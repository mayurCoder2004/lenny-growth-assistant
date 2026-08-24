const API_BASE_URL = "http://127.0.0.1:8000";

export async function sendChatMessage({
  sessionId,
  message,
  agent = "chat",
}) {
  const response = await fetch(
    `${API_BASE_URL}/sessions/${sessionId}/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        agent,
      }),
    }
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Chat request failed (${response.status}): ${errorText}`
    );
  }

  return response.json();
}
