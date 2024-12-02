import { Message } from '@ai-chat/shared';
import ChatMessage from './ChatMessage';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-white/80">
        <h1 className="text-4xl font-bold mb-8">ChatGPT</h1>
        <div className="max-w-xl w-full space-y-4 px-4">
          <p className="text-center text-lg">有什么可以帮忙的？</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}
    </div>
  );
} 