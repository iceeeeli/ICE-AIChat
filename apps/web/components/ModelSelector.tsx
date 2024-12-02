import { useState, useEffect } from 'react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

interface Model {
  name: string;
  type: 'ollama' | 'baidu';
  modified_at?: string;
  size?: number;
}

interface ModelSelectorProps {
  currentModel: string;
  onModelChange: (model: string) => void;
}

export default function ModelSelector({ currentModel, onModelChange }: ModelSelectorProps) {
  const [models, setModels] = useState<Model[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const response = await fetch('http://localhost:3000/models');
      const data = await response.json();
      setModels(data.models);
    } catch (error) {
      console.error('Failed to fetch models:', error);
    }
  };

  const handleModelChange = async (model: string) => {
    try {
      const response = await fetch('http://localhost:3000/models/current', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ model }),
      });
      
      if (response.ok) {
        onModelChange(model);
      }
    } catch (error) {
      console.error('Failed to change model:', error);
    }
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:text-white transition-colors"
      >
        <span>模型: {currentModel}</span>
        <ChevronDownIcon className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-1 w-56 bg-[#202123] border border-gray-700 rounded-md shadow-lg overflow-hidden">
          {models.map((model) => (
            <button
              key={model.name}
              onClick={() => handleModelChange(model.name)}
              className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-700 transition-colors ${
                currentModel === model.name ? 'bg-gray-700 text-white' : 'text-gray-300'
              }`}
            >
              <div className="flex justify-between items-center">
                <span>{model.name}</span>
                <span className="text-xs text-gray-500">{model.type}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
} 