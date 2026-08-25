import { API_BASE_URL } from "./config";

export async function getArtifact(artifactId) {
  const response = await fetch(
    `${API_BASE_URL}/artifacts/${artifactId}`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load artifact (${response.status}).`
    );
  }

  return response.json();
}
