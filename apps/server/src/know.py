import os
from pathlib import Path
from typing import List, Dict, Any
import json
import requests
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import docx
import uuid
import tiktoken

# 创建知识库目录
KNOWLEDGE_DIR = Path(__file__).parent.parent.parent.parent / 'data' / 'knowledge'
KNOWLEDGE_DIR.mkdir(exist_ok=True, parents=True)

# Ollama API 配置
OLLAMA_URL = "http://localhost:11434/api/embeddings"

def get_embedding(text: str) -> List[float]:
    """获取文本的向量表示"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "mistral",
                "prompt": text
            }
        )
        result = response.json()
        print(f"获取向量成功: {len(result['embedding'])} 维")
        return result['embedding']
    except Exception as e:
        print(f"获取向量失败: {str(e)}")
        raise

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """将文本分割成小块"""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        chunks = []
        
        current_chunk = []
        current_size = 0
        
        for token in tokens:
            current_chunk.append(token)
            current_size += 1
            
            if current_size >= chunk_size:
                chunks.append(encoding.decode(current_chunk))
                current_chunk = []
                current_size = 0
        
        if current_chunk:
            chunks.append(encoding.decode(current_chunk))
        
        print(f"文本分块完成: {len(chunks)} 个块")
        return chunks
    except Exception as e:
        print(f"文本分块失败: {str(e)}")
        raise

def process_document(file_path: Path, doc_type: str) -> Dict[str, Any]:
    """处理文档并生成向量"""
    print(f"开始处理文档: {file_path}")
    try:
        # 读取文档内容
        if doc_type == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif doc_type in ['doc', 'docx']:
            doc = docx.Document(file_path)
            content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        
        print(f"文档内容长度: {len(content)} 字符")
        
        # 分块并生成向量
        chunks = chunk_text(content)
        chunk_vectors = []
        
        for i, chunk in enumerate(chunks):
            print(f"处理第 {i+1}/{len(chunks)} 个文本块")
            vector = get_embedding(chunk)
            chunk_vectors.append({
                'content': chunk,
                'vector': vector
            })
        
        # 生成文档向量（使用所有块的平均向量）
        doc_vector = np.mean([chunk['vector'] for chunk in chunk_vectors], axis=0).tolist()
        
        # 创建文档记录
        document = {
            'id': str(uuid.uuid4()),
            'title': file_path.stem,
            'content': content,
            'type': doc_type,
            'vectors': doc_vector,
            'chunks': chunk_vectors,
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        # 保存文档
        save_document(document)
        print(f"文档处理完成: {document['id']}")
        return document
        
    except Exception as e:
        print(f"处理文档失败: {str(e)}")
        raise

def save_document(document: Dict[str, Any]) -> None:
    """保存文档到知识库"""
    try:
        file_path = KNOWLEDGE_DIR / f"{document['id']}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
        print(f"文档已保存: {file_path}")
    except Exception as e:
        print(f"保存文档失败: {str(e)}")
        raise

def search_knowledge(query: str, top_k: int = 3, similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
    """搜索知识库"""
    try:
        print(f"开始搜索: {query}")
        query_vector = get_embedding(query)
        
        results = []
        knowledge_files = list(KNOWLEDGE_DIR.glob('*.json'))
        print(f"找到 {len(knowledge_files)} 个知识文档")
        
        for file_path in knowledge_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    document = json.load(f)
                
                # 计算每个块与查询的相似度
                for chunk in document['chunks']:
                    similarity = cosine_similarity(
                        [query_vector], 
                        [chunk['vector']]
                    )[0][0]
                    
                    print(f"块相似度: {similarity:.4f}")
                    
                    if similarity > similarity_threshold:
                        results.append({
                            'content': chunk['content'],
                            'score': float(similarity)
                        })
            except Exception as e:
                print(f"处理文档 {file_path} 时出错: {str(e)}")
                continue
        
        # 按相似度排序并返回前 top_k 个结果
        results.sort(key=lambda x: x['score'], reverse=True)
        top_results = results[:top_k]
        
        print(f"找到 {len(top_results)} 个相关结果")
        for i, result in enumerate(top_results):
            print(f"结果 {i+1}: 相似度 {result['score']:.4f}")
            print(f"内容: {result['content'][:100]}...")
        
        return top_results
        
    except Exception as e:
        print(f"搜索失败: {str(e)}")
        raise

def get_all_documents() -> List[Dict[str, Any]]:
    """获取所有文档的基本信息"""
    try:
        documents = []
        for file_path in KNOWLEDGE_DIR.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                doc = json.load(f)
                documents.append({
                    'id': doc['id'],
                    'title': doc['title'],
                    'type': doc['type'],
                    'createdAt': doc['createdAt']
                })
        print(f"获取到 {len(documents)} 个文档")
        return sorted(documents, key=lambda x: x['createdAt'], reverse=True)
    except Exception as e:
        print(f"获取文档列表失败: {str(e)}")
        raise 