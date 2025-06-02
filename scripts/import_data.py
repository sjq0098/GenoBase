#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_data.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseImporter:
    def __init__(self, host: str = "localhost", user: str = "root", 
                 password: str = "Sjq63100", database: str = "GenoBase"):
        """初始化数据库导入器"""
        self.db_config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }
        self.data_dir = "data"
        self.conn = None
        self.cursor = None

    def connect(self):
        """连接到数据库"""
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("成功连接到数据库")
        except Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def disconnect(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")

    def load_json_data(self, filename: str) -> List[Dict[str, Any]]:
        """从JSON文件加载数据"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, list) else [data]
        except Exception as e:
            logger.error(f"读取文件 {filename} 失败: {e}")
            raise

    def import_species(self):
        """导入物种数据"""
        species_data = self.load_json_data("species.json")
        insert_query = """
            INSERT INTO Species 
            (scientific_name, common_name, taxonomy_id, description)
            VALUES (%s, %s, %s, %s)
        """
        try:
            for species in species_data:
                values = (
                    species['scientific_name'],
                    species.get('common_name'),
                    species.get('taxonomy_id'),
                    species.get('description')
                )
                self.cursor.execute(insert_query, values)
            self.conn.commit()
            logger.info(f"成功导入 {len(species_data)} 条物种数据")
        except Error as e:
            self.conn.rollback()
            logger.error(f"导入物种数据失败: {e}")
            raise

    def import_users(self):
        """导入用户数据"""
        users_data = self.load_json_data("users.json")
        creators_data = self.load_json_data("creators.json")
        managers_data = self.load_json_data("managers.json")
        readers_data = self.load_json_data("readers.json")

        # 插入基础用户数据
        insert_user_query = """
            INSERT INTO Users 
            (username, password_hash, email, user_type, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            # 使用事务处理用户数据导入
            self.cursor.execute("START TRANSACTION")
            
            # 导入基础用户数据
            for user in users_data:
                values = (
                    user['username'],
                    user['password_hash'],
                    user['email'],
                    user['user_type'],
                    user.get('api_key'),
                    user.get('is_active', True)
                )
                self.cursor.execute(insert_user_query, values)
                user_id = self.cursor.lastrowid

                # 根据用户类型导入对应的特定信息
                if user['user_type'] == 'creator':
                    creator = next((c for c in creators_data if c['user_id'] == user_id), None)
                    if creator:
                        self.cursor.execute("""
                            INSERT INTO Creators 
                            (user_id, institution, research_field, max_storage_size)
                            VALUES (%s, %s, %s, %s)
                        """, (user_id, creator['institution'], 
                              creator['research_field'],
                              creator.get('max_storage_size', 1073741824)))

                elif user['user_type'] == 'manager':
                    manager = next((m for m in managers_data if m['user_id'] == user_id), None)
                    if manager:
                        self.cursor.execute("""
                            INSERT INTO Managers 
                            (user_id, department, access_level)
                            VALUES (%s, %s, %s)
                        """, (user_id, manager['department'], manager['access_level']))

                elif user['user_type'] == 'reader':
                    reader = next((r for r in readers_data if r['user_id'] == user_id), None)
                    if reader:
                        self.cursor.execute("""
                            INSERT INTO Readers 
                            (user_id, organization, subscription_type)
                            VALUES (%s, %s, %s)
                        """, (user_id, reader['organization'], reader['subscription_type']))

            self.conn.commit()
            logger.info(f"成功导入 {len(users_data)} 条用户数据")
        except Error as e:
            self.conn.rollback()
            logger.error(f"导入用户数据失败: {e}")
            raise

    def import_genes(self):
        """导入基因数据"""
        genes_data = self.load_json_data("genes.json")
        insert_query = """
            INSERT INTO Genes 
            (gene_name, gene_symbol, sequence, chromosome, 
             start_position, end_position, strand, species_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            for gene in genes_data:
                values = (
                    gene['gene_name'],
                    gene['gene_symbol'],
                    gene['sequence'],
                    gene['chromosome'],
                    gene['start_position'],
                    gene['end_position'],
                    gene['strand'],
                    gene['species_id']
                )
                self.cursor.execute(insert_query, values)
            self.conn.commit()
            logger.info(f"成功导入 {len(genes_data)} 条基因数据")
        except Error as e:
            self.conn.rollback()
            logger.error(f"导入基因数据失败: {e}")
            raise

    def import_proteins(self):
        """导入蛋白质数据"""
        proteins_data = self.load_json_data("proteins.json")
        insert_query = """
            INSERT INTO Proteins 
            (protein_name, uniprot_id, amino_acid_sequence, gene_id)
            VALUES (%s, %s, %s, %s)
        """
        try:
            for protein in proteins_data:
                values = (
                    protein['protein_name'],
                    protein['uniprot_id'],
                    protein['amino_acid_sequence'],
                    protein['gene_id']
                )
                self.cursor.execute(insert_query, values)
            self.conn.commit()
            logger.info(f"成功导入 {len(proteins_data)} 条蛋白质数据")
        except Error as e:
            self.conn.rollback()
            logger.error(f"导入蛋白质数据失败: {e}")
            raise

    def import_publications(self):
        """导入文献数据"""
        publications_data = self.load_json_data("publications.json")
        insert_query = """
            INSERT INTO Publications 
            (title, authors, journal, publication_year, doi)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            for pub in publications_data:
                values = (
                    pub['title'],
                    pub['authors'],
                    pub['journal'],
                    pub['publication_year'],
                    pub.get('doi')
                )
                self.cursor.execute(insert_query, values)
            self.conn.commit()
            logger.info(f"成功导入 {len(publications_data)} 条文献数据")
        except Error as e:
            self.conn.rollback()
            logger.error(f"导入文献数据失败: {e}")
            raise

    def import_gene_publications(self):
        """导入基因-文献关联数据"""
        gene_publications_data = self.load_json_data("gene_publications.json")
        insert_query = """
            INSERT INTO Gene_Publications 
            (gene_id, publication_id)
            VALUES (%s, %s)
        """
        try:
            for assoc in gene_publications_data:
                values = (assoc['gene_id'], assoc['publication_id'])
                self.cursor.execute(insert_query, values)
            self.conn.commit()
            logger.info(f"成功导入 {len(gene_publications_data)} 条基因-文献关联数据")
        except Error as e:
            self.conn.rollback()
            logger.error(f"导入基因-文献关联数据失败: {e}")
            raise

    def import_experimental_data(self):
        """导入实验数据"""
        experimental_data = self.load_json_data("experimental_data.json")
        insert_query = """
            INSERT INTO Experimental_Data 
            (experiment_type, conditions, results, gene_id, publication_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            for exp in experimental_data:
                values = (
                    exp['experiment_type'],
                    exp['conditions'],
                    exp['results'],
                    exp['gene_id'],
                    exp['publication_id']
                )
                self.cursor.execute(insert_query, values)
            self.conn.commit()
            logger.info(f"成功导入 {len(experimental_data)} 条实验数据")
        except Error as e:
            self.conn.rollback()
            logger.error(f"导入实验数据失败: {e}")
            raise

    def import_all_data(self):
        """按正确的顺序导入所有数据"""
        try:
            self.connect()
            
            # 导入顺序考虑外键约束
            import_sequence = [
                (self.import_species, "物种"),
                (self.import_users, "用户"),
                (self.import_genes, "基因"),
                (self.import_proteins, "蛋白质"),
                (self.import_publications, "文献"),
                (self.import_gene_publications, "基因-文献关联"),
                (self.import_experimental_data, "实验数据")
            ]

            for import_func, data_type in import_sequence:
                try:
                    logger.info(f"开始导入{data_type}数据...")
                    import_func()
                except Exception as e:
                    logger.error(f"{data_type}数据导入失败: {e}")
                    raise

            logger.info("所有数据导入完成！")

        except Exception as e:
            logger.error(f"数据导入过程中发生错误: {e}")
            raise
        finally:
            self.disconnect()

def main():
    """主函数"""
    importer = DatabaseImporter()
    try:
        importer.import_all_data()
    except Exception as e:
        logger.error(f"数据导入失败: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main()) 