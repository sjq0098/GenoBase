import sys
import importlib
import pkg_resources
import logging
from typing import List, Dict, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version() -> bool:
    """检查Python版本"""
    required_version = (3, 9)
    current_version = sys.version_info[:2]
    
    logger.info(f"当前Python版本: {sys.version}")
    if current_version >= required_version:
        logger.info("Python版本检查通过")
        return True
    else:
        logger.error(f"Python版本不满足要求，需要 {required_version} 或更高版本")
        return False

def get_required_packages() -> Dict[str, str]:
    """获取所需包列表"""
    return {
        # 核心依赖
        'fastapi': None,
        'uvicorn': None,
        'sqlalchemy': None,
        'mysql-connector-python': None,
        'pydantic': None,
        'python-jose': None,
        'passlib': None,
        'python-multipart': None,
        
        # 数据处理
        'pandas': None,
        'numpy': None,
        'biopython': None,
        
        # 工具包
        'python-dotenv': None,
        'alembic': None,
        'requests': None,
        'aiofiles': None,
        'aiomysql': None,
        
        # 测试工具
        'pytest': None,
        'black': None,
        'flake8': None,
        'mypy': None,
    }

def check_package(package_name: str) -> Tuple[bool, str]:
    """检查单个包是否安装及其版本"""
    try:
        package = pkg_resources.working_set.by_key[package_name]
        return True, package.version
    except KeyError:
        return False, "未安装"

def test_database_connection() -> bool:
    """测试数据库连接并创建数据库"""
    try:
        import mysql.connector
        # 首先尝试连接到MySQL服务器（不指定数据库）
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Sjq63100"
        )
        cursor = conn.cursor()
        
        # 创建数据库（如果不存在）
        cursor.execute("CREATE DATABASE IF NOT EXISTS genobase")
        logger.info("数据库 'genobase' 创建成功或已存在")
        
        # 切换到genobase数据库
        cursor.execute("USE genobase")
        
        # 关闭连接
        cursor.close()
        conn.close()
        logger.info("数据库连接测试成功")
        return True
    except Exception as e:
        logger.error(f"数据库连接测试失败: {str(e)}")
        return False

def test_fastapi_setup() -> bool:
    """测试FastAPI基本设置"""
    try:
        from fastapi import FastAPI
        app = FastAPI()
        logger.info("FastAPI基本设置测试成功")
        return True
    except Exception as e:
        logger.error(f"FastAPI基本设置测试失败: {str(e)}")
        return False

def test_biopython_functionality() -> bool:
    """测试BioPython基本功能"""
    try:
        from Bio import SeqIO
        from Bio.Seq import Seq
        test_seq = Seq("ATCG")
        logger.info("BioPython基本功能测试成功")
        return True
    except Exception as e:
        logger.error(f"BioPython基本功能测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    logger.info("开始环境测试...")
    
    # 检查Python版本
    python_check = check_python_version()
    
    # 检查包依赖
    packages = get_required_packages()
    package_results = []
    for package_name in packages:
        installed, version = check_package(package_name)
        package_results.append((package_name, installed, version))
        if installed:
            logger.info(f"✓ {package_name} 已安装 (版本: {version})")
        else:
            logger.error(f"✗ {package_name} 未安装")
    
    # 测试数据库连接
    db_check = test_database_connection()
    
    # 测试FastAPI设置
    fastapi_check = test_fastapi_setup()
    
    # 测试BioPython功能
    biopython_check = test_biopython_functionality()
    
    # 输出总结
    logger.info("\n测试结果总结:")
    logger.info(f"Python版本检查: {'通过' if python_check else '失败'}")
    logger.info(f"包依赖检查: {sum(1 for _, installed, _ in package_results if installed)}/{len(package_results)} 个包已安装")
    logger.info(f"数据库连接测试: {'通过' if db_check else '失败'}")
    logger.info(f"FastAPI设置测试: {'通过' if fastapi_check else '失败'}")
    logger.info(f"BioPython功能测试: {'通过' if biopython_check else '失败'}")
    
    # 返回总体测试结果
    all_passed = all([
        python_check,
        all(installed for _, installed, _ in package_results),
        db_check,
        fastapi_check,
        biopython_check
    ])
    
    if all_passed:
        logger.info("\n✓ 所有测试通过！环境配置正确。")
        return 0
    else:
        logger.error("\n✗ 部分测试失败，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 