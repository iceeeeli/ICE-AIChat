import { PlusIcon, ChatBubbleLeftIcon, TrashIcon, CodeBracketIcon } from '@heroicons/react/24/outline';

interface Conversation {
  id: string;
  title: string;
  updatedAt: string;
}

interface ConversationListProps {
  conversations: Conversation[];
  currentConversationId: string | null;
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
  onGetSdkCode: () => void;
}

export default function ConversationList({
  conversations,
  currentConversationId,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
  onGetSdkCode,
}: ConversationListProps) {
  return (
    <>
      <div className="flex flex-col gap-2">
        <button
          onClick={onNewChat}
          className="flex items-center gap-3 w-full p-3 rounded-md hover:bg-gray-700 transition-colors border border-gray-600/50 text-sm"
        >
          <PlusIcon className="h-4 w-4" />
          <span>新对话</span>
        </button>
        <button
          onClick={onGetSdkCode}
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
              onClick={() => onSelectConversation(conversation.id)}
            >
              <ChatBubbleLeftIcon className="h-4 w-4" />
              <span className="truncate">{conversation.title}</span>
            </button>
            <button
              onClick={() => onDeleteConversation(conversation.id)}
              className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500 transition-all"
            >
              <TrashIcon className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </>
  );
} 