import { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export default function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className="p-4">
      <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          placeholder="发送消息..."
          className="w-full resize-none rounded-xl border border-gray-700/50 bg-[#40414f] pl-4 pr-12 py-3 text-white focus:outline-none focus:border-gray-600 shadow-lg max-h-48"
          rows={1}
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !message.trim()}
          className="absolute right-3 bottom-3 p-1 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-700/50 disabled:hover:bg-transparent disabled:hover:text-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          <PaperAirplaneIcon className="h-5 w-5" />
        </button>
      </form>
      <p className="mt-2 text-xs text-center text-gray-500">
        按 Enter 发送，Shift + Enter 换行
      </p>
    </div>
  );
} 