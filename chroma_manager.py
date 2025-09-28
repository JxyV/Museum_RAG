"""
Chroma数据库管理工具
用于管理Chroma数据库的创建、删除、重命名等操作
"""
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from voice_interface import build_embeddings


class ChromaManager:
    """Chroma数据库管理器"""
    
    def __init__(self):
        load_dotenv()
        self.persist_dir = os.getenv("CHROMA_PERSIST_DIR", ".chroma")
        self.embeddings = build_embeddings()
    
    def list_collections(self):
        """列出所有数据库集合"""
        if not os.path.exists(self.persist_dir):
            print("Chroma数据库目录不存在")
            return []
        
        try:
            # 尝试连接到Chroma
            client = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
            
            # 获取所有集合
            collections = client._client.list_collections()
            print(f"找到 {len(collections)} 个数据库集合:")
            for i, collection in enumerate(collections, 1):
                print(f"{i}. {collection.name}")
            return collections
        except Exception as e:
            print(f"无法列出集合: {e}")
            return []
    
    def create_collection(self, collection_name: str):
        """创建新的数据库集合"""
        try:
            vectordb = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_dir,
            )
            print(f"✅ 成功创建数据库集合: {collection_name}")
            return vectordb
        except Exception as e:
            print(f"❌ 创建集合失败: {e}")
            return None
    
    def delete_collection(self, collection_name: str):
        """删除数据库集合"""
        try:
            vectordb = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_dir,
            )
            vectordb.delete_collection()
            print(f"✅ 成功删除数据库集合: {collection_name}")
        except Exception as e:
            print(f"❌ 删除集合失败: {e}")
    
    def rename_collection(self, old_name: str, new_name: str):
        """重命名数据库集合（通过复制数据实现）"""
        try:
            # 读取原集合
            old_db = Chroma(
                collection_name=old_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_dir,
            )
            
            # 获取所有数据
            docs = old_db.get()
            if not docs['ids']:
                print("原集合为空，无需重命名")
                return
            
            # 创建新集合
            new_db = Chroma(
                collection_name=new_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_dir,
            )
            
            # 复制数据
            new_db.add(
                ids=docs['ids'],
                documents=docs['documents'],
                metadatas=docs['metadatas']
            )
            
            # 删除原集合
            old_db.delete_collection()
            
            print(f"✅ 成功重命名集合: {old_name} -> {new_name}")
        except Exception as e:
            print(f"❌ 重命名集合失败: {e}")
    
    def backup_collection(self, collection_name: str, backup_dir: str = "backup"):
        """备份数据库集合"""
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(exist_ok=True)
            
            # 复制整个Chroma目录
            chroma_backup = backup_path / f"{collection_name}_backup"
            if os.path.exists(self.persist_dir):
                shutil.copytree(self.persist_dir, chroma_backup)
                print(f"✅ 成功备份到: {chroma_backup}")
            else:
                print("❌ 源目录不存在")
        except Exception as e:
            print(f"❌ 备份失败: {e}")
    
    def restore_collection(self, backup_dir: str, collection_name: str):
        """恢复数据库集合"""
        try:
            backup_path = Path(backup_dir)
            if backup_path.exists():
                # 删除现有数据
                if os.path.exists(self.persist_dir):
                    shutil.rmtree(self.persist_dir)
                
                # 恢复备份
                shutil.copytree(backup_path, self.persist_dir)
                print(f"✅ 成功恢复集合: {collection_name}")
            else:
                print("❌ 备份目录不存在")
        except Exception as e:
            print(f"❌ 恢复失败: {e}")
    
    def get_collection_info(self, collection_name: str):
        """获取集合信息"""
        try:
            vectordb = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_dir,
            )
            
            # 获取集合信息
            docs = vectordb.get()
            count = len(docs['ids']) if docs['ids'] else 0
            
            print(f"📊 集合信息: {collection_name}")
            print(f"   文档数量: {count}")
            print(f"   存储路径: {self.persist_dir}")
            
            if count > 0:
                print(f"   示例文档: {docs['documents'][0][:100]}...")
            
            return count
        except Exception as e:
            print(f"❌ 获取集合信息失败: {e}")
            return 0


def main():
    """主函数 - 交互式数据库管理"""
    manager = ChromaManager()
    
    print("🗄️ Chroma数据库管理工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 列出所有数据库集合")
        print("2. 创建新集合")
        print("3. 删除集合")
        print("4. 重命名集合")
        print("5. 备份集合")
        print("6. 恢复集合")
        print("7. 查看集合信息")
        print("8. 退出")
        
        choice = input("\n请输入选择 (1-8): ").strip()
        
        if choice == "1":
            manager.list_collections()
        
        elif choice == "2":
            name = input("请输入新集合名称: ").strip()
            if name:
                manager.create_collection(name)
        
        elif choice == "3":
            name = input("请输入要删除的集合名称: ").strip()
            if name:
                confirm = input(f"确认删除集合 '{name}'? (y/N): ").strip().lower()
                if confirm == 'y':
                    manager.delete_collection(name)
        
        elif choice == "4":
            old_name = input("请输入原集合名称: ").strip()
            new_name = input("请输入新集合名称: ").strip()
            if old_name and new_name:
                manager.rename_collection(old_name, new_name)
        
        elif choice == "5":
            name = input("请输入要备份的集合名称: ").strip()
            if name:
                manager.backup_collection(name)
        
        elif choice == "6":
            backup_dir = input("请输入备份目录路径: ").strip()
            name = input("请输入集合名称: ").strip()
            if backup_dir and name:
                manager.restore_collection(backup_dir, name)
        
        elif choice == "7":
            name = input("请输入集合名称: ").strip()
            if name:
                manager.get_collection_info(name)
        
        elif choice == "8":
            print("👋 再见！")
            break
        
        else:
            print("❌ 无效选择，请重试")


if __name__ == "__main__":
    main()
