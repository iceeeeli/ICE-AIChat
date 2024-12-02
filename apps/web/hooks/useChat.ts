import { useState, useCallback } from 'react';
import { Message } from '@ai-chat/shared';
import { api } from '@/lib/api';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);

  const sendMessage = useCallback(async (
    message: string,
    options: { useKnowledge?: boolean } = {}
  ) => {
    if (!message.trim()) return;

    const newUserMessage: Message = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const newBotMessage: Message = {
        id: Date.now() + 1,
        type: 'bot',
        content: '',
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages(prev => [...prev, newBotMessage]);

      await api.sendMessage(message, {
        conversationId: currentConversationId || undefined,
        ...options,
        onChunk: (data) => {
          if (data.conversationId && !currentConversationId) {
            setCurrentConversationId(data.conversationId);
          }
          if (data.chunk) {
            setMessages(prev => {
              const lastMessage = prev[prev.length - 1];
              if (lastMessage.type === 'bot') {
                return [
                  ...prev.slice(0, -1),
                  { ...lastMessage, content: lastMessage.content + data.chunk }
                ];
              }
              return prev;
            });
          }
        },
      });
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: Date.now() + 1,
        type: 'bot',
        content: '抱歉，我遇到了一些问题。请稍后再试。',
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [currentConversationId]);

  return {
    messages,
    isLoading,
    currentConversationId,
    sendMessage,
    setMessages,
    setCurrentConversationId,
  };
} 