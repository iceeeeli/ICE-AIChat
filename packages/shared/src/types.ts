export type MessageType = 'user' | 'bot';
export type ModelType = 'ollama' | 'baidu';

export interface Message {
  id: number;
  type: MessageType;
  content: string;
  timestamp: string;
  model?: string;
  isManual?: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
  isManualMode?: boolean;
}

export interface Model {
  name: string;
  type: ModelType;
  modified_at?: string;
  size?: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  success: boolean;
}

export interface SendMessageOptions {
  conversationId?: string;
  useKnowledge?: boolean;
  onChunk?: (data: any) => void;
}

export interface Document {
  id: string;
  title: string;
  content: string;
  type: 'txt' | 'doc' | 'docx';
  vectors: number[];
  chunks: {
    content: string;
    vector: number[];
  }[];
  createdAt: string;
  updatedAt: string;
}

export interface SearchResult {
  content: string;
  score: number;
} 