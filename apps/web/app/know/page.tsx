'use client';

import { useState, useRef } from 'react';
import { Document } from '@ai-chat/shared';
import { CloudArrowUpIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = async () => {
    try {
      const response = await fetch('http://localhost:3000/knowledge');
      const data = await response.json();
      setDocuments(data);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    }
  };

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:3000/knowledge/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      await fetchDocuments();
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#343541]">
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-white">知识库管理</h1>
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept=".txt,.doc,.docx"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleUpload(file);
            }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-800"
          >
            <CloudArrowUpIcon className="h-5 w-5" />
            {isUploading ? '上传中...' : '上传文档'}
          </button>
        </div>

        <div className="grid gap-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-[#444654] rounded-lg p-4 flex items-center gap-4"
            >
              <DocumentTextIcon className="h-8 w-8 text-blue-400" />
              <div>
                <h3 className="text-lg font-medium text-white">{doc.title}</h3>
                <p className="text-sm text-gray-400">
                  上传时间：{new Date(doc.createdAt).toLocaleString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 