export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function parseApiErrorMessage(text: string, status: number): string {
  let errorMessage = text || `Request failed with status ${status}`;

  try {
    const json = JSON.parse(text) as { detail?: string; error?: string; message?: string };
    errorMessage = json.detail || json.error || json.message || errorMessage;
  } catch {
    // Not JSON, keep raw response text.
  }

  return errorMessage;
}

export function formatApiError(err: unknown, fallbackMessage: string): string {
  if (err instanceof ApiError) {
    if (err.status === 422) {
      return `Input validation failed: ${err.message}`;
    }
    if (err.status >= 500) {
      return `Server error (${err.status}): ${err.message || "Please retry in a moment."}`;
    }
    if (err.status === 404) {
      return "API endpoint not found. Check API configuration and route path.";
    }
    return err.message || fallbackMessage;
  }

  if (err instanceof TypeError && err.message.includes("fetch")) {
    return "Network error: Unable to connect to API. Ensure the API server is running on http://127.0.0.1:8000";
  }

  if (err instanceof Error) {
    return err.message || fallbackMessage;
  }

  return fallbackMessage;
}

export async function apiFetch<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  try {
    const response = await fetch(input, init);
    if (!response.ok) {
      const text = await response.text();
      throw new ApiError(response.status, parseApiErrorMessage(text, response.status));
    }
    return response.json() as Promise<T>;
  } catch (err) {
    if (err instanceof TypeError && err.message.includes("fetch")) {
      throw new Error("Network error: Unable to connect to API. Ensure the API server is running on http://127.0.0.1:8000");
    }
    throw err;
  }
}

export async function apiText(input: RequestInfo | URL, init?: RequestInit): Promise<string> {
  try {
    const response = await fetch(input, init);
    if (!response.ok) {
      const text = await response.text();
      throw new ApiError(response.status, parseApiErrorMessage(text, response.status));
    }
    return response.text();
  } catch (err) {
    if (err instanceof TypeError && err.message.includes("fetch")) {
      throw new Error("Network error: Unable to connect to API. Ensure the API server is running on http://127.0.0.1:8000");
    }
    throw err;
  }
}
