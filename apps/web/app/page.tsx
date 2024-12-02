'use client';

import { useState, useRef, useEffect } from 'react';
import type { Message } from '@ai-chat/shared';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import { Bars3Icon, PlusIcon, ChatBubbleLeftIcon, TrashIcon, CodeBracketIcon } from '@heroicons/react/24/outline';
import ModelSelector from '../components/ModelSelector';

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [currentResponse, setCurrentResponse] = useState('');
  const [useKnowledge, setUseKnowledge] = useState(false);
  const [currentModel, setCurrentModel] = useState('mistral');
  const [showSdkModal, setShowSdkModal] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 加载对话列表
  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      const response = await fetch('http://localhost:3000/conversations');
      const data = await response.json();
      setConversations(data);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    }
  };

  // 加载特定对话
  const loadConversation = async (conversationId: string) => {
    try {
      const response = await fetch(`http://localhost:3000/conversations/${conversationId}`);
      const data = await response.json();
      setMessages(data.messages);
      setCurrentConversationId(conversationId);
      setIsSidebarOpen(false);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentConversationId(null);
    setIsSidebarOpen(false);
  };

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    // 创建新的用户消息
    const newUserMessage: Message = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString(),
    };

    // 如果是新对话，先清空消息列表
    if (!currentConversationId) {
      setMessages([newUserMessage]);
    } else {
      // 如果是现有对话，追加消息
      setMessages(prev => [...prev, newUserMessage]);
    }
    
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:3000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversationId: currentConversationId,
          useKnowledge
        }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No reader available');
      }

      // 创建新的机器人消息
      const newBotMessage: Message = {
        id: Date.now() + 1,
        type: 'bot',
        content: '',
        model: currentModel,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages(prev => [...prev, newBotMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(5));
              if (data.conversationId && !currentConversationId) {
                // 如果是新对话，设置对话ID
                setCurrentConversationId(data.conversationId);
              }
              if (data.chunk) {
                setMessages(prev => {
                  const lastMessage = prev[prev.length - 1];
                  if (lastMessage.type === 'bot') {
                    return [
                      ...prev.slice(0, -1),
                      {
                        ...lastMessage,
                        content: lastMessage.content + data.chunk
                      }
                    ];
                  }
                  return prev;
                });
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }

      // 对话完成后刷新对话列表
      fetchConversations();

    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: Date.now() + 1,
        type: 'bot',
        content: '抱歉，我遇到了一些问题。请稍后再试。',
        model: currentModel,
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleModelChange = (model: string) => {
    setCurrentModel(model);
  };

  // 添加删除对话功能
  const handleDeleteConversation = async (conversationId: string) => {
    try {
      const response = await fetch(`http://localhost:3000/conversations/${conversationId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchConversations();
        if (currentConversationId === conversationId) {
          handleNewChat();
        }
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  // 获取 SDK 代码
  const handleGetSdkCode = async () => {
    try {
      const response = await fetch('http://localhost:3000/sdk/script');
      const script = await response.text();
      const sdkCode = `
<!-- 在你的网页中添加以下代码 -->

${script}


<!-- 初始化聊天窗口 -->

  initAIChat();

`;
      // 复制到剪贴板
      await navigator.clipboard.writeText(sdkCode);
      alert('SDK 代码已复制到剪贴板！');
    } catch (error) {
      console.error('Failed to get SDK code:', error);
      alert('获取 SDK 代码失败，请重试。');
    }
  };

  return (
    <div className="flex h-screen bg-[#343541]">
      {/* 侧边栏 */}
      <div 
        className={`fixed md:static inset-0 bg-black/50 md:bg-transparent z-40 ${
          isSidebarOpen ? 'block' : 'hidden'
        } md:block`} 
        onClick={() => setIsSidebarOpen(false)}
      >
        <div 
          className="w-[260px] h-full bg-[#202123] text-gray-200 p-2 flex flex-col" 
          onClick={e => e.stopPropagation()}
        >
          <div className="flex flex-col gap-2">
            <button
              onClick={handleNewChat}
              className="flex items-center gap-3 w-full p-3 rounded-md hover:bg-gray-700 transition-colors border border-gray-600/50 text-sm"
            >
              <PlusIcon className="h-4 w-4" />
              <span>新对话</span>
            </button>
            <button
              onClick={handleGetSdkCode}
              className="flex items-center gap-3 w-full p-3 rounded-md hover:bg-gray-700 transition-colors border border-gray-600/50 text-sm"
            >
              <CodeBracketIcon className="h-4 w-4" />
              <span>获取 SDK 代码</span>
            </button>
          </div>
          
          <div className="flex-1 mt-4 overflow-y-auto">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`group flex items-center gap-3 w-full p-3 rounded-md hover:bg-gray-700 transition-colors text-sm mb-1 ${
                  currentConversationId === conversation.id ? 'bg-gray-700' : ''
                }`}
              >
                <button
                  className="flex-1 flex items-center gap-3 text-left"
                  onClick={() => loadConversation(conversation.id)}
                >
                  <ChatBubbleLeftIcon className="h-4 w-4" />
                  <span className="truncate">{conversation.title}</span>
                </button>
                <button
                  onClick={() => handleDeleteConversation(conversation.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500 transition-all"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="flex-1 flex flex-col h-full relative">
        {/* 移动端菜单按钮 */}
        <button
          className="md:hidden absolute top-4 left-4 z-50 p-2 text-white/80 hover:text-white"
          onClick={() => setIsSidebarOpen(true)}
        >
          <Bars3Icon className="h-6 w-6" />
        </button>

        {/* 添加模型选择器 */}
        <div className="absolute top-4 right-4 z-50">
          <ModelSelector
            currentModel={currentModel}
            onModelChange={handleModelChange}
          />
        </div>

        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-white/80">
              <h1 className="text-4xl font-bold mb-8">ChatGPT</h1>
              <div className="max-w-xl w-full space-y-4 px-4">
                <p className="text-center text-lg">有什么可以帮忙的？</p>
              </div>
            </div>
          ) : (
            <div className="w-full">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
            </div>
          )}
        </div>

        {/* 输入框 */}
        <div className="border-t border-gray-800/50 bg-[#343541]">
          <div className="max-w-2xl mx-auto px-4 py-2">
            <label className="flex items-center gap-2 text-sm text-gray-400">
              <input
                type="checkbox"
                checked={useKnowledge}
                onChange={(e) => setUseKnowledge(e.target.checked)}
                className="rounded border-gray-600 text-blue-600 focus:ring-blue-500"
              />
              使用知识库
            </label>
          </div>
          <div className="max-w-2xl mx-auto">
            <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
          </div>
        </div>
      </div>
    </div>
  );
}