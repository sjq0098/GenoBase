#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import logging
import os
import sys
from typing import Dict, Any, List, Tuple, Optional
from tabulate import tabulate
import getpass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('genobase_console.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GenoBaseConsole:
    """GenoBase 控制台应用程序"""
    
    def __init__(self, host: str = "localhost", user: str = "root", 
                 password: str = None, database: str = "GenoBase"):
        """初始化控制台应用程序"""
        if password is None:
            password = getpass.getpass("请输入MySQL密码: ")
            
        self.db_config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }
        self.conn = None
        self.cursor = None
        
    def connect(self) -> bool:
        """连接到数据库"""
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor(dictionary=True)
            logger.info("成功连接到数据库")
            return True
        except Error as e:
            logger.error(f"数据库连接失败: {e}")
            return False
            
    def disconnect(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
            
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询并返回结果"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            logger.error(f"查询执行失败: {e}")
            return []
            
    def execute_procedure(self, procedure: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行存储过程并返回结果"""
        try:
            self.cursor.callproc(procedure, params or ())
            # 获取所有结果集
            results = []
            for result in self.cursor.stored_results():
                results.extend(result.fetchall())
            return results
        except Error as e:
            logger.error(f"存储过程执行失败: {e}")
            # 重新抛出异常，让调用者处理
            raise e
            
    def print_table(self, data: List[Dict[str, Any]]):
        """以表格形式打印数据"""
        if not data:
            print("没有数据")
            return
            
        headers = data[0].keys()
        rows = [list(row.values()) for row in data]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        
    def show_menu(self):
        """显示主菜单"""
        menu = """
GenoBase 控制台应用程序
======================

1. 查询操作
2. 添加操作
3. 更新操作
4. 删除操作
5. 视图查询
0. 退出

请选择操作: """
        return input(menu)
        
    def show_query_menu(self):
        """显示查询菜单"""
        menu = """
查询操作
=======

1. 查询所有物种
2. 查询所有用户
3. 查询特定物种的基因
4. 查询特定基因的蛋白质
5. 查询特定基因的文献
6. 查询特定基因的实验数据
0. 返回主菜单

请选择操作: """
        return input(menu)
        
    def show_add_menu(self):
        """显示添加菜单"""
        menu = """
添加操作
=======

1. 添加新物种
2. 添加新基因
3. 添加新蛋白质（触发器控制）
4. 添加新文献
5. 添加新实验数据（触发器控制）
0. 返回主菜单

请选择操作: """
        return input(menu)
        
    def show_update_menu(self):
        """显示更新菜单"""
        menu = """
更新操作
=======

1. 更新基因名称（存储过程控制）
2. 更新物种信息（存储过程控制）
3. 更新用户信息
0. 返回主菜单

请选择操作: """
        return input(menu)
        
    def show_delete_menu(self):
        """显示删除菜单"""
        menu = """
删除操作
=======

1. 删除物种及其关联数据（事务控制）
2. 删除基因
3. 删除蛋白质
4. 删除文献
5. 删除实验数据
0. 返回主菜单

请选择操作: """
        return input(menu)
        
    def show_view_menu(self):
        """显示视图查询菜单"""
        menu = """
视图查询
=======

1. 查询基因-物种-蛋白质数量视图
2. 查询基因研究活跃度视图
3. 查询用户角色信息视图
0. 返回主菜单

请选择操作: """
        return input(menu)
        
    # 查询操作实现
    def query_all_species(self):
        """查询所有物种"""
        query = "SELECT * FROM Species"
        results = self.execute_query(query)
        print("\n所有物种信息:")
        self.print_table(results)
        
    def query_all_users(self):
        """查询所有用户"""
        query = "SELECT * FROM Users"
        results = self.execute_query(query)
        print("\n所有用户信息:")
        self.print_table(results)
        
    def query_genes_by_species(self):
        """查询特定物种的基因"""
        # 先显示所有物种
        self.query_all_species()
        
        species_id = input("\n请输入物种ID: ")
        query = "SELECT * FROM Genes WHERE species_id = %s"
        results = self.execute_query(query, (species_id,))
        print(f"\n物种ID {species_id} 的基因信息:")
        self.print_table(results)
        
    def query_proteins_by_gene(self):
        """查询特定基因的蛋白质"""
        gene_id = input("\n请输入基因ID: ")
        query = "SELECT * FROM Proteins WHERE gene_id = %s"
        results = self.execute_query(query, (gene_id,))
        print(f"\n基因ID {gene_id} 的蛋白质信息:")
        self.print_table(results)
        
    def query_publications_by_gene(self):
        """查询特定基因的文献"""
        gene_id = input("\n请输入基因ID: ")
        query = """
        SELECT p.* 
        FROM Publications p
        JOIN Gene_Publications gp ON p.publication_id = gp.publication_id
        WHERE gp.gene_id = %s
        """
        results = self.execute_query(query, (gene_id,))
        print(f"\n基因ID {gene_id} 的文献信息:")
        self.print_table(results)
        
    def query_experiments_by_gene(self):
        """查询特定基因的实验数据"""
        gene_id = input("\n请输入基因ID: ")
        query = "SELECT * FROM Experimental_Data WHERE gene_id = %s"
        results = self.execute_query(query, (gene_id,))
        print(f"\n基因ID {gene_id} 的实验数据:")
        self.print_table(results)
        
    # 添加操作实现
    def add_species(self):
        """添加新物种"""
        scientific_name = input("请输入物种学名: ")
        common_name = input("请输入物种俗名: ")
        taxonomy_id = input("请输入分类ID: ")
        description = input("请输入描述: ")
        
        query = """
        INSERT INTO Species (scientific_name, common_name, taxonomy_id, description)
        VALUES (%s, %s, %s, %s)
        """
        
        try:
            self.cursor.execute(query, (scientific_name, common_name, taxonomy_id, description))
            self.conn.commit()
            print(f"成功添加物种 {scientific_name}，ID为 {self.cursor.lastrowid}")
        except Error as e:
            self.conn.rollback()
            print(f"添加物种失败: {e}")
            
    def add_gene(self):
        """添加新基因"""
        # 先显示所有物种
        self.query_all_species()
        
        gene_name = input("请输入基因名称: ")
        gene_symbol = input("请输入基因符号: ")
        sequence = input("请输入基因序列: ")
        chromosome = input("请输入染色体: ")
        start_position = input("请输入起始位置: ")
        end_position = input("请输入终止位置: ")
        strand = input("请输入链方向 (+/-): ")
        species_id = input("请输入物种ID: ")
        
        query = """
        INSERT INTO Genes (gene_name, gene_symbol, sequence, chromosome, 
                          start_position, end_position, strand, species_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            self.cursor.execute(query, (gene_name, gene_symbol, sequence, chromosome, 
                                       start_position, end_position, strand, species_id))
            self.conn.commit()
            print(f"成功添加基因 {gene_name}，ID为 {self.cursor.lastrowid}")
        except Error as e:
            self.conn.rollback()
            print(f"添加基因失败: {e}")
            
    def add_protein(self):
        """添加新蛋白质（触发器控制）"""
        protein_name = input("请输入蛋白质名称: ")
        uniprot_id = input("请输入UniProt ID: ")
        amino_acid_sequence = input("请输入氨基酸序列: ")
        gene_id = input("请输入基因ID: ")
        
        query = """
        INSERT INTO Proteins (protein_name, uniprot_id, amino_acid_sequence, gene_id)
        VALUES (%s, %s, %s, %s)
        """
        
        try:
            self.cursor.execute(query, (protein_name, uniprot_id, amino_acid_sequence, gene_id))
            self.conn.commit()
            print(f"成功添加蛋白质 {protein_name}，ID为 {self.cursor.lastrowid}")
        except Error as e:
            self.conn.rollback()
            print(f"添加蛋白质失败: {e}")
            
    def add_publication(self):
        """添加新文献"""
        title = input("请输入文献标题: ")
        authors = input("请输入作者: ")
        journal = input("请输入期刊名称: ")
        publication_year = input("请输入发表年份: ")
        doi = input("请输入DOI: ")
        
        query = """
        INSERT INTO Publications (title, authors, journal, publication_year, doi)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            self.cursor.execute(query, (title, authors, journal, publication_year, doi))
            self.conn.commit()
            print(f"成功添加文献 {title}，ID为 {self.cursor.lastrowid}")
        except Error as e:
            self.conn.rollback()
            print(f"添加文献失败: {e}")
            
    def add_experiment(self):
        """添加新实验数据（触发器控制）"""
        experiment_type = input("请输入实验类型: ")
        conditions = input("请输入实验条件: ")
        results = input("请输入实验结果: ")
        gene_id = input("请输入基因ID: ")
        publication_id = input("请输入文献ID: ")
        
        query = """
        INSERT INTO Experimental_Data (experiment_type, conditions, results, gene_id, publication_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            self.cursor.execute(query, (experiment_type, conditions, results, gene_id, publication_id))
            self.conn.commit()
            print(f"成功添加实验数据，ID为 {self.cursor.lastrowid}")
        except Error as e:
            self.conn.rollback()
            print(f"添加实验数据失败: {e}")
            
    # 更新操作实现
    def update_gene_name(self):
        """更新基因名称（存储过程控制）"""
        gene_id = input("请输入要更新的基因ID: ")
        new_gene_name = input("请输入新的基因名称: ")
        
        try:
            results = self.execute_procedure("UpdateGeneAndProteinInfo", (gene_id, new_gene_name))
            print("更新结果:")
            self.print_table(results)
        except Error as e:
            print(f"更新基因名称失败: {e}")
            
    def update_species_info(self):
        """更新物种信息（存储过程控制）"""
        # 先显示所有物种
        self.query_all_species()
        
        species_id = input("请输入要更新的物种ID: ")
        scientific_name = input("请输入新的学名（留空表示不更新）: ")
        common_name = input("请输入新的俗名（留空表示不更新）: ")
        description = input("请输入新的描述（留空表示不更新）: ")
        
        # 将空字符串转换为None
        scientific_name = scientific_name if scientific_name else None
        common_name = common_name if common_name else None
        description = description if description else None
        
        try:
            results = self.execute_procedure("UpdateSpeciesInfo", 
                                           (species_id, scientific_name, common_name, description))
            print("更新结果:")
            self.print_table(results)
        except Error as e:
            print(f"更新物种信息失败: {e}")
            
    def update_user_info(self):
        """更新用户信息"""
        # 先显示所有用户
        self.query_all_users()
        
        user_id = input("请输入要更新的用户ID: ")
        username = input("请输入新的用户名（留空表示不更新）: ")
        email = input("请输入新的邮箱（留空表示不更新）: ")
        is_active = input("请输入是否活跃（1=是，0=否，留空表示不更新）: ")
        
        # 构建更新语句
        update_parts = []
        params = []
        
        if username:
            update_parts.append("username = %s")
            params.append(username)
        
        if email:
            update_parts.append("email = %s")
            params.append(email)
        
        if is_active:
            update_parts.append("is_active = %s")
            params.append(int(is_active))
        
        if not update_parts:
            print("没有提供任何更新信息")
            return
        
        query = f"UPDATE Users SET {', '.join(update_parts)} WHERE user_id = %s"
        params.append(user_id)
        
        try:
            self.cursor.execute(query, tuple(params))
            self.conn.commit()
            print(f"成功更新用户ID {user_id}，影响行数: {self.cursor.rowcount}")
        except Error as e:
            self.conn.rollback()
            print(f"更新用户信息失败: {e}")
            
    # 删除操作实现
    def delete_species(self):
        """删除物种及其关联数据（事务控制）"""
        # 先显示所有物种
        self.query_all_species()
        
        species_id = input("请输入要删除的物种ID: ")
        confirm = input(f"确定要删除物种ID {species_id} 及其所有关联数据吗？(y/n): ")
        
        if confirm.lower() != 'y':
            print("操作已取消")
            return
        
        try:
            # 首先尝试使用存储过程
            try:
                results = self.execute_procedure("DeleteSpeciesWithRelatedData", (species_id,))
                print("删除结果:")
                self.print_table(results)
                return
            except Error as e:
                # 如果存储过程不存在，则使用手动事务方式删除
                if "PROCEDURE" in str(e) and "does not exist" in str(e):
                    logger.info("存储过程不存在，使用手动事务方式删除")
                    # 确保连接处于干净状态
                    if self.conn.in_transaction:
                        self.conn.rollback()
                    self.delete_species_manually(species_id)
                else:
                    raise e
        except Error as e:
            # 确保任何错误都会回滚事务
            if self.conn.in_transaction:
                self.conn.rollback()
            print(f"删除物种失败: {e}")
            
    def delete_species_manually(self, species_id):
        """手动事务方式删除物种及其关联数据"""
        try:
            # 确保不在事务中
            if self.conn.in_transaction:
                self.conn.rollback()
                
            # 开始事务
            self.conn.start_transaction()
            
            # 检查物种是否存在
            self.cursor.execute("SELECT COUNT(*) as count FROM Species WHERE species_id = %s", (species_id,))
            result = self.cursor.fetchone()
            if not result or result['count'] == 0:
                self.conn.rollback()
                print("物种ID不存在")
                return
                
            # 删除该物种相关的实验数据（如果有）
            try:
                self.cursor.execute("""
                    DELETE FROM Experimental_Data 
                    WHERE gene_id IN (SELECT gene_id FROM Genes WHERE species_id = %s)
                """, (species_id,))
                exp_deleted = self.cursor.rowcount
            except Error as e:
                # 可能表不存在或其他错误，继续尝试删除其他关联数据
                logger.warning(f"删除实验数据时出错: {e}")
                exp_deleted = 0
            
            # 删除该物种基因与文献的关联（如果有）
            try:
                self.cursor.execute("""
                    DELETE FROM Gene_Publications 
                    WHERE gene_id IN (SELECT gene_id FROM Genes WHERE species_id = %s)
                """, (species_id,))
                pub_deleted = self.cursor.rowcount
            except Error as e:
                logger.warning(f"删除基因-文献关联时出错: {e}")
                pub_deleted = 0
            
            # 删除该物种相关的蛋白质（如果有）
            try:
                self.cursor.execute("""
                    DELETE FROM Proteins 
                    WHERE gene_id IN (SELECT gene_id FROM Genes WHERE species_id = %s)
                """, (species_id,))
                prot_deleted = self.cursor.rowcount
            except Error as e:
                logger.warning(f"删除蛋白质时出错: {e}")
                prot_deleted = 0
            
            # 删除该物种的基因（如果有）
            try:
                self.cursor.execute("DELETE FROM Genes WHERE species_id = %s", (species_id,))
                gene_deleted = self.cursor.rowcount
            except Error as e:
                logger.warning(f"删除基因时出错: {e}")
                gene_deleted = 0
            
            # 最后删除物种本身
            self.cursor.execute("DELETE FROM Species WHERE species_id = %s", (species_id,))
            species_deleted = self.cursor.rowcount
            
            # 提交事务
            self.conn.commit()
            
            print(f"删除成功: 物种({species_deleted}), 基因({gene_deleted}), 蛋白质({prot_deleted}), 基因-文献关联({pub_deleted}), 实验数据({exp_deleted})")
            
        except Error as e:
            if self.conn.in_transaction:
                self.conn.rollback()
            print(f"删除物种失败: {e}")
            
    def delete_gene(self):
        """删除基因"""
        gene_id = input("请输入要删除的基因ID: ")
        confirm = input(f"确定要删除基因ID {gene_id} 吗？(y/n): ")
        
        if confirm.lower() != 'y':
            print("操作已取消")
            return
        
        query = "DELETE FROM Genes WHERE gene_id = %s"
        
        try:
            self.cursor.execute(query, (gene_id,))
            self.conn.commit()
            print(f"成功删除基因ID {gene_id}，影响行数: {self.cursor.rowcount}")
        except Error as e:
            self.conn.rollback()
            print(f"删除基因失败: {e}")
            
    def delete_protein(self):
        """删除蛋白质"""
        protein_id = input("请输入要删除的蛋白质ID: ")
        confirm = input(f"确定要删除蛋白质ID {protein_id} 吗？(y/n): ")
        
        if confirm.lower() != 'y':
            print("操作已取消")
            return
        
        query = "DELETE FROM Proteins WHERE protein_id = %s"
        
        try:
            self.cursor.execute(query, (protein_id,))
            self.conn.commit()
            print(f"成功删除蛋白质ID {protein_id}，影响行数: {self.cursor.rowcount}")
        except Error as e:
            self.conn.rollback()
            print(f"删除蛋白质失败: {e}")
            
    def delete_publication(self):
        """删除文献"""
        publication_id = input("请输入要删除的文献ID: ")
        confirm = input(f"确定要删除文献ID {publication_id} 吗？(y/n): ")
        
        if confirm.lower() != 'y':
            print("操作已取消")
            return
        
        query = "DELETE FROM Publications WHERE publication_id = %s"
        
        try:
            self.cursor.execute(query, (publication_id,))
            self.conn.commit()
            print(f"成功删除文献ID {publication_id}，影响行数: {self.cursor.rowcount}")
        except Error as e:
            self.conn.rollback()
            print(f"删除文献失败: {e}")
            
    def delete_experiment(self):
        """删除实验数据"""
        experiment_id = input("请输入要删除的实验数据ID: ")
        confirm = input(f"确定要删除实验数据ID {experiment_id} 吗？(y/n): ")
        
        if confirm.lower() != 'y':
            print("操作已取消")
            return
        
        query = "DELETE FROM Experimental_Data WHERE experiment_id = %s"
        
        try:
            self.cursor.execute(query, (experiment_id,))
            self.conn.commit()
            print(f"成功删除实验数据ID {experiment_id}，影响行数: {self.cursor.rowcount}")
        except Error as e:
            self.conn.rollback()
            print(f"删除实验数据失败: {e}")
            
    # 视图查询实现
    def query_gene_protein_count(self):
        """查询基因-物种-蛋白质数量视图"""
        query = "SELECT * FROM GeneProteinCountBySpecies"
        results = self.execute_query(query)
        print("\n基因-物种-蛋白质数量视图:")
        self.print_table(results)
        
    def query_gene_research_activity(self):
        """查询基因研究活跃度视图"""
        query = "SELECT * FROM GeneResearchActivity ORDER BY activity_score DESC LIMIT 20"
        results = self.execute_query(query)
        print("\n基因研究活跃度视图 (Top 20):")
        self.print_table(results)
        
    def query_user_role_info(self):
        """查询用户角色信息视图"""
        query = "SELECT * FROM UserRoleInfo"
        results = self.execute_query(query)
        print("\n用户角色信息视图:")
        self.print_table(results)
        
    def run(self):
        """运行控制台应用程序"""
        if not self.connect():
            print("无法连接到数据库，程序退出")
            return
        
        try:
            while True:
                choice = self.show_menu()
                
                if choice == '0':
                    break
                elif choice == '1':  # 查询操作
                    self.handle_query_menu()
                elif choice == '2':  # 添加操作
                    self.handle_add_menu()
                elif choice == '3':  # 更新操作
                    self.handle_update_menu()
                elif choice == '4':  # 删除操作
                    self.handle_delete_menu()
                elif choice == '5':  # 视图查询
                    self.handle_view_menu()
                else:
                    print("无效的选择，请重试")
        finally:
            self.disconnect()
            
    def handle_query_menu(self):
        """处理查询菜单"""
        while True:
            choice = self.show_query_menu()
            
            if choice == '0':
                break
            elif choice == '1':
                self.query_all_species()
            elif choice == '2':
                self.query_all_users()
            elif choice == '3':
                self.query_genes_by_species()
            elif choice == '4':
                self.query_proteins_by_gene()
            elif choice == '5':
                self.query_publications_by_gene()
            elif choice == '6':
                self.query_experiments_by_gene()
            else:
                print("无效的选择，请重试")
                
    def handle_add_menu(self):
        """处理添加菜单"""
        while True:
            choice = self.show_add_menu()
            
            if choice == '0':
                break
            elif choice == '1':
                self.add_species()
            elif choice == '2':
                self.add_gene()
            elif choice == '3':
                self.add_protein()
            elif choice == '4':
                self.add_publication()
            elif choice == '5':
                self.add_experiment()
            else:
                print("无效的选择，请重试")
                
    def handle_update_menu(self):
        """处理更新菜单"""
        while True:
            choice = self.show_update_menu()
            
            if choice == '0':
                break
            elif choice == '1':
                self.update_gene_name()
            elif choice == '2':
                self.update_species_info()
            elif choice == '3':
                self.update_user_info()
            else:
                print("无效的选择，请重试")
                
    def handle_delete_menu(self):
        """处理删除菜单"""
        while True:
            choice = self.show_delete_menu()
            
            if choice == '0':
                break
            elif choice == '1':
                self.delete_species()
            elif choice == '2':
                self.delete_gene()
            elif choice == '3':
                self.delete_protein()
            elif choice == '4':
                self.delete_publication()
            elif choice == '5':
                self.delete_experiment()
            else:
                print("无效的选择，请重试")
                
    def handle_view_menu(self):
        """处理视图查询菜单"""
        while True:
            choice = self.show_view_menu()
            
            if choice == '0':
                break
            elif choice == '1':
                self.query_gene_protein_count()
            elif choice == '2':
                self.query_gene_research_activity()
            elif choice == '3':
                self.query_user_role_info()
            else:
                print("无效的选择，请重试")

def main():
    """主函数"""
    print("欢迎使用 GenoBase 控制台应用程序")
    console = GenoBaseConsole()
    console.run()
    print("感谢使用 GenoBase 控制台应用程序，再见！")

if __name__ == "__main__":
    main() 