class DatabaseConnectionError(Exception):
    """数据库连接错误"""
    pass

class DatabaseNotFoundError(Exception):
    """数据库未找到错误"""
    pass

class DatabaseNotInitializedError(Exception):
    """数据库未初始化错误"""
    pass

class StorageConnectionError(Exception):
    """存储连接错误"""
    pass

class VectorStoreConnectionError(Exception):
    """向量存储连接错误"""
    pass
    