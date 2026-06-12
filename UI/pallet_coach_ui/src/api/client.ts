export async function apiFetch<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  try {
    const response = await fetch(input, init);
    if (!response.ok) {
      const text = await response.text();
      let errorMessage = text || `Request failed with status ${response.status}`;
      
      // Parse JSON error response if available
      try {
        const json = JSON.parse(text);
        errorMessage = json.detail || json.error || errorMessage;
      } catch {
        // Not JSON, use raw text
      }
      
      throw new Error(errorMessage);
    }
    return response.json() as Promise<T>;
  } catch (err) {
    if (err instanceof TypeError && err.message.includes('fetch')) {
      throw new Error(`Network error: Unable to connect to API. Ensure the API server is running on http://127.0.0.1:8000`);
    }
    throw err;
  }
}

export async function apiText(input: RequestInfo | URL, init?: RequestInit): Promise<string> {
  try {
    const response = await fetch(input, init);
    if (!response.ok) {
      const text = await response.text();
      let errorMessage = text || `Request failed with status ${response.status}`;
      
      // Parse JSON error response if available
      try {
        const json = JSON.parse(text);
        errorMessage = json.detail || json.error || errorMessage;
      } catch {
        // Not JSON, use raw text
      }
      
      throw new Error(errorMessage);
    }
    return response.text();
  } catch (err) {
    if (err instanceof TypeError && err.message.includes('fetch')) {
      throw new Error(`Network error: Unable to connect to API. Ensure the API server is running on http://127.0.0.1:8000`);
    }
    throw err;
  }
}
