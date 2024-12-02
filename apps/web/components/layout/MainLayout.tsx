'use client';

import { ReactNode } from 'react';
import { Bars3Icon } from '@heroicons/react/24/outline';
import ModelSelector from '../common/ModelSelector';

interface MainLayoutProps {
  children: ReactNode;
  sidebar: ReactNode;
  isSidebarOpen: boolean;
  setIsSidebarOpen: (open: boolean) => void;
  currentModel: string;
  onModelChange: (model: string) => void;
}

export default function MainLayout({
  children,
  sidebar,
  isSidebarOpen,
  setIsSidebarOpen,
  currentModel,
  onModelChange,
}: MainLayoutProps) {
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
          {sidebar}
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

        {/* 模型选择器 */}
        <div className="absolute top-4 right-4 z-50">
          <ModelSelector
            currentModel={currentModel}
            onModelChange={onModelChange}
          />
        </div>

        {children}
      </div>
    </div>
  );
} 