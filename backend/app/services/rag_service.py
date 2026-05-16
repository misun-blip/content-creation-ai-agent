"""
RAG 语义检索服务
基于 ChromaDB 向量数据库实现素材的语义搜索
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# 延迟导入 chromadb，避免未安装时影响其他模块
_rag_service = None


class RAGService:
    """
    RAG (Retrieval-Augmented Generation) 语义检索服务
    - 素材入库时自动生成 embedding 存入向量库
    - 检索时按语义相似度返回最相关的素材
    """

    def __init__(self, persist_dir: str = "./chroma_data"):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.client.get_or_create_collection(
                name="materials",
                metadata={"hnsw:space": "cosine"},  # 使用余弦相似度
            )
            self._available = True
            logger.info(f"ChromaDB 初始化成功，存储路径: {persist_dir}")
        except ImportError:
            logger.warning("chromadb 未安装，RAG 功能将被禁用。安装命令: pip install chromadb")
            self._available = False
        except Exception as e:
            logger.warning(f"ChromaDB 初始化失败，RAG 功能将被禁用: {e}")
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available

    def add_material(self, material_id: int, title: str, description: str = "") -> bool:
        """
        素材入库：将标题+描述生成 embedding 存入向量库
        ChromaDB 默认使用 all-MiniLM-L6-v2 模型自动生成 embedding
        """
        if not self._available:
            return False
        try:
            text = f"{title}。{description}" if description else title
            self.collection.upsert(
                ids=[str(material_id)],
                documents=[text],
                metadatas=[{"material_id": material_id, "title": title}],
            )
            logger.debug(f"素材入库向量库: id={material_id}, title={title}")
            return True
        except Exception as e:
            logger.warning(f"素材入库向量库失败 (id={material_id}): {e}")
            return False

    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        语义检索：根据查询文本返回最相似的素材
        返回格式: [{"material_id": int, "title": str, "document": str, "distance": float}, ...]
        """
        if not self._available:
            return []
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(top_k, self.collection.count() or 1),
            )

            items = []
            if results and results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    item = {
                        "material_id": int(doc_id),
                        "document": results["documents"][0][i] if results["documents"] else "",
                        "distance": results["distances"][0][i] if results["distances"] else 0,
                    }
                    if results["metadatas"] and results["metadatas"][0]:
                        item["title"] = results["metadatas"][0][i].get("title", "")
                    items.append(item)

            logger.debug(f"语义检索: query='{query}', 命中 {len(items)} 条")
            return items
        except Exception as e:
            logger.warning(f"语义检索失败: {e}")
            return []

    def delete_material(self, material_id: int) -> bool:
        """素材删除时同步清除向量"""
        if not self._available:
            return False
        try:
            self.collection.delete(ids=[str(material_id)])
            logger.debug(f"从向量库删除素材: id={material_id}")
            return True
        except Exception as e:
            logger.warning(f"从向量库删除素材失败 (id={material_id}): {e}")
            return False

    def get_count(self) -> int:
        """获取向量库中的素材数量"""
        if not self._available:
            return 0
        try:
            return self.collection.count()
        except Exception:
            return 0


def get_rag_service() -> RAGService:
    """获取 RAG 服务单例"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
