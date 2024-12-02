import ChatInput from './ChatInput';

interface InputAreaProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  useKnowledge: boolean;
  onToggleKnowledge: (use: boolean) => void;
}

export default function InputArea({
  onSendMessage,
  isLoading,
  useKnowledge,
  onToggleKnowledge,
}: InputAreaProps) {
  return (
    <div className="border-t border-gray-800/50 bg-[#343541]">
      <div className="max-w-2xl mx-auto px-4 py-2">
        <label className="flex items-center gap-2 text-sm text-gray-400">
          <input
            type="checkbox"
            checked={useKnowledge}
            onChange={(e) => onToggleKnowledge(e.target.checked)}
            className="rounded border-gray-600 text-blue-600 focus:ring-blue-500"
          />
          使用知识库
        </label>
      </div>
      <div className="max-w-2xl mx-auto">
        <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
} 