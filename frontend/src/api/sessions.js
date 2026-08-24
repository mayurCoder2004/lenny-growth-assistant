const API_BASE_URL = "http://127.0.0.1:8000";

export async function getUserSessions(userId) {
  const response = await fetch(
    `${API_BASE_URL}/sessions/user/${userId}`
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Failed to load sessions (${response.status}): ${errorText}`
    );
  }

  return response.json();
}

export async function getSessionMessages(sessionId) {
  const response = await fetch(
    `${API_BASE_URL}/sessions/${sessionId}/messages`
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Failed to load messages (${response.status}): ${errorText}`
    );
  }

  return response.json();
}

export async function createSession({
  userId,
  title = "New Chat",
}) {
  const response = await fetch(
    `${API_BASE_URL}/sessions`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: userId,
        title,
      }),
    }
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Failed to create session (${response.status}): ${errorText}`
    );
  }

  return response.json();
}
