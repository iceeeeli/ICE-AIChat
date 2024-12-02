export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';

export const ROUTES = {
  HOME: '/',
  KNOWLEDGE: '/know',
  SDK_CHAT: '/sdk-chat',
} as const;

export const MESSAGE_TYPES = {
  USER: 'user',
  BOT: 'bot',
} as const;

export const MODEL_TYPES = {
  OLLAMA: 'ollama',
  BAIDU: 'baidu',
} as const; 