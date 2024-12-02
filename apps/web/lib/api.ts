import { SendMessageOptions } from '@ai-chat/shared';

const API_BASE_URL = 'http://localhost:3000';

export async function fetchWithSSE<T = any>(
  url: string,
  options: RequestInit & { onChunk?: (data: any) => void }
): Promise<T> {
  const { onChunk, ...fetchOptions } = options;
  const response = await fetch(`${API_BASE_URL}${url}`, fetchOptions);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  
  if (!reader) {
    throw new Error('No reader available');
  }
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(5));
          onChunk?.(data);
        } catch (e) {
          console.error('Error parsing SSE data:', e);
        }
      }
    }
  }
  
  return {} as T;
}

export const api = {
  async getModels() {
    const response = await fetch(`${API_BASE_URL}/models`);
    return response.json();
  },
  
  async setCurrentModel(model: string) {
    const response = await fetch(`${API_BASE_URL}/models/current`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model }),
    });
    return response.json();
  },
  
  async getConversations() {
    const response = await fetch(`${API_BASE_URL}/conversations`);
    return response.json();
  },
  
  async getConversation(id: string) {
    const response = await fetch(`${API_BASE_URL}/conversations/${id}`);
    return response.json();
  },
  
  async deleteConversation(id: string) {
    const response = await fetch(`${API_BASE_URL}/conversations/${id}`, {
      method: 'DELETE',
    });
    return response.json();
  },
  
  async sendMessage(message: string, options: SendMessageOptions) {
    return fetchWithSSE('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        ...options,
      }),
    });
  },
}; 