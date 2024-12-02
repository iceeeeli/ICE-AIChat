'use client';

import { useState, useEffect } from 'react';
import { ChatBubbleLeftIcon, UserIcon } from '@heroicons/react/24/outline';
import ChatMessage from '../../components/ChatMessage';

interface SdkConversation {
  id: string;
  title: string;
  messages: Array<{
    id: number;
    type: 'user' | 'bot';
    content: string;
    timestamp: string;
    isManual?: boolean;
  }>;
  updatedAt: string;
  isManualMode?: boolean;
}

export default function SdkChatPage() {
  const [conversations, setConversations] = useState<Array<{ id: string; title: string; updatedAt: string }>>([]);
  const [currentConversation, setCurrentConversation] = useState<SdkConversation | null>(null);
  const [manualReply, setManualReply] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isManualMode, setIsManualMode] = useState(false);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (currentConversation) {
      setIsManualMode(!!currentConversation.isManualMode);
    }
  }, [currentConversation]);

  const fetchConversations = async () => {
    try {
      const response = await fetch('http://localhost:3000/sdk/conversations');
      const data = await response.json();
      setConversations(data);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    }
  };

  const loadConversation = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:3000/sdk/conversations/${id}`);
      const data = await response.json();
      setCurrentConversation(data);
      setIsManualMode(!!data.isManualMode);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const handleManualReply = async () => {
    if (!manualReply.trim() || !currentConversation) return;

    setIsSubmitting(true);
    try {
      const response = await fetch('http://localhost:3000/sdk/manual-reply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: manualReply,
          conversationId: currentConversation.id,
        }),
      });

      if (response.ok) {
        await loadConversation(currentConversation.id);
        setManualReply('');
      }
    } catch (error) {
      console.error('Failed to send manual reply:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleManualMode = async () => {
    if (!currentConversation) return;

    try {
      const newMode = !isManualMode;
      const response = await fetch(`http://localhost:3000/sdk/conversations/${currentConversation.id}/mode`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          isManual: newMode
        }),
      });

      if (response.ok) {
        setIsManualMode(newMode);
        setCurrentConversation(prev => prev ? {
          ...prev,
          isManualMode: newMode
        } : null);
      }
    } catch (error) {
      console.error('Failed to toggle manual mode:', error);
    }
  };

  useEffect(() => {
    if (currentConversation?.id) {
      const intervalId = setInterval(() => {
        loadConversation(currentConversation.id);
      }, 5000);

      return () => clearInterval(intervalId);
    }
  }, [currentConversation?.id]);

  return (
    <div className="flex h-screen bg-[#343541]">
      {/* 侧边栏 */}
      <div className="w-64 bg-[#202123] text-gray-200 p-4">
        <h2 className="text-lg font-semibold mb-4">SDK 对话记录</h2>
        <div className="space-y-2">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => loadConversation(conv.id)}
              className={`w-full text-left p-2 hover:bg-gray-700 rounded-lg transition-colors flex items-center gap-2 ${
                currentConversation?.id === conv.id ? 'bg-gray-700' : ''
              }`}
            >
              <ChatBubbleLeftIcon className="h-4 w-4" />
              <span className="truncate">{conv.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 主内容区 */}
      <div className="flex-1 flex flex-col">
        {currentConversation ? (
          <>
            {/* 对话标题和控制栏 */}
            <div className="border-b border-gray-700 p-4 bg-[#202123] flex justify-between items-center">
              <h2 className="text-lg text-white font-medium">实时对话</h2>
              <button
                onClick={toggleManualMode}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  isManualMode
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {isManualMode ? '关闭人工介入' : '开启人工介入'}
              </button>
            </div>

            {/* 消息列表 */}
            <div className="flex-1 overflow-y-auto p-4">
              {currentConversation.messages.map((message, index) => (
                <>
                  {message.isManual && index > 0 && (
                    <div className="text-center text-sm text-gray-500 my-2">
                      ——— 人工介入 ———
                    </div>
                  )}
                  <ChatMessage key={message.id} message={message} />
                </>
              ))}
            </div>

            {/* 人工回复区域 */}
            {isManualMode && (
              <div className="border-t border-gray-700 p-4 bg-[#40414f]">
                <div className="max-w-3xl mx-auto">
                  <textarea
                    value={manualReply}
                    onChange={(e) => setManualReply(e.target.value)}
                    placeholder="输入人工回复内容..."
                    className="w-full p-3 bg-[#343541] text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
                    rows={3}
                  />
                  <button
                    onClick={handleManualReply}
                    disabled={isSubmitting || !manualReply.trim()}
                    className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? '发送中...' : '发送人工回复'}
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            选择一个对话以查看内容
          </div>
        )}
      </div>
    </div>
  );
} 