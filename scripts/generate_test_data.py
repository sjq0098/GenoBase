#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import hashlib

class TestDataGenerator:
    def __init__(self, data_dir: str = "data"):
        """初始化数据生成器"""
        self.data_dir = data_dir
        self._ensure_data_dir()
        
        # 基础数据
        self.species = [
            {
                "scientific_name": "Homo sapiens",
                "common_name": "Human",
                "taxonomy_id": "9606",
                "description": "Modern human"
            },
            {
                "scientific_name": "Mus musculus",
                "common_name": "Mouse",
                "taxonomy_id": "10090",
                "description": "House mouse"
            },
            {
                "scientific_name": "Rattus norvegicus",
                "common_name": "Rat",
                "taxonomy_id": "10116",
                "description": "Brown rat"
            },
            {
                "scientific_name": "Drosophila melanogaster",
                "common_name": "Fruit fly",
                "taxonomy_id": "7227",
                "description": "Common fruit fly"
            },
            {
                "scientific_name": "Saccharomyces cerevisiae",
                "common_name": "Baker's yeast",
                "taxonomy_id": "4932",
                "description": "Budding yeast"
            }
        ]
        
        self.chromosomes = {
            "Homo sapiens": [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"],
            "Mus musculus": [f"chr{i}" for i in range(1, 20)] + ["chrX", "chrY"],
            "Rattus norvegicus": [f"chr{i}" for i in range(1, 21)] + ["chrX", "chrY"],
            "Drosophila melanogaster": ["2L", "2R", "3L", "3R", "4", "X", "Y"],
            "Saccharomyces cerevisiae": [f"{i}" for i in range(1, 17)]
        }
        
        self.journals = [
            "Nature", "Science", "Cell", "Genome Research", "Bioinformatics",
            "PLOS ONE", "BMC Genomics", "Nucleic Acids Research"
        ]
        
        self.experiment_types = [
            "RNA-Seq", "ChIP-Seq", "ATAC-Seq", "WGS", "WES",
            "Microarray", "Proteomics", "Metabolomics"
        ]

        self.institutions = [
            "Harvard University", "MIT", "Stanford University", 
            "Oxford University", "Cambridge University"
        ]

        self.departments = [
            "Bioinformatics", "Genomics", "Molecular Biology",
            "Systems Biology", "Computational Biology"
        ]

        self.organizations = [
            "Research Institute A", "Biotech Company B",
            "University Lab C", "Medical Center D"
        ]

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def generate_api_key(self) -> str:
        """生成随机API密钥"""
        return hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()[:64]

    def generate_users(self, num_users: int) -> Dict[str, List[Dict[str, Any]]]:
        """生成用户数据，包括基础用户和三种类型的用户"""
        users = []
        creators = []
        managers = []
        readers = []
        
        user_types = ['creator', 'manager', 'reader']
        
        for i in range(num_users):
            user_type = random.choice(user_types)
            
            # 基础用户信息
            user = {
                "username": f"user_{i}",
                "password_hash": hashlib.sha256(f"password_{i}".encode()).hexdigest(),
                "email": f"user_{i}@example.com",
                "user_type": user_type,
                "api_key": self.generate_api_key() if random.random() > 0.5 else None,
                "is_active": random.choice([True, True, True, False])  # 75%概率活跃
            }
            users.append(user)
            
            # 根据用户类型生成对应的特定信息
            if user_type == 'creator':
                creator = {
                    "user_id": i + 1,  # 假设自增ID从1开始
                    "institution": random.choice(self.institutions),
                    "research_field": random.choice(self.departments),
                    "max_storage_size": random.choice([1073741824, 2147483648, 4294967296])  # 1GB, 2GB, 4GB
                }
                creators.append(creator)
            
            elif user_type == 'manager':
                manager = {
                    "user_id": i + 1,
                    "department": random.choice(self.departments),
                    "access_level": random.choice(['full', 'limited'])
                }
                managers.append(manager)
            
            else:  # reader
                reader = {
                    "user_id": i + 1,
                    "organization": random.choice(self.organizations),
                    "subscription_type": random.choice(['free', 'premium'])
                }
                readers.append(reader)
        
        return {
            "users": users,
            "creators": creators,
            "managers": managers,
            "readers": readers
        }

    def generate_dna_sequence(self, length: int) -> str:
        """生成随机DNA序列"""
        bases = ['A', 'C', 'G', 'T']
        return ''.join(random.choices(bases, k=length))

    def generate_protein_sequence(self, length: int) -> str:
        """生成随机蛋白质序列"""
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        return ''.join(random.choices(amino_acids, k=length))

    def generate_genes(self, num_genes: int) -> List[Dict[str, Any]]:
        """生成基因数据"""
        genes = []
        for i in range(num_genes):
            species = random.choice(self.species)
            chromosome = random.choice(self.chromosomes[species["scientific_name"]])
            start_pos = random.randint(1, 1000000)
            
            gene = {
                "gene_name": f"Gene_{i}",
                "gene_symbol": f"G{i}",
                "sequence": self.generate_dna_sequence(random.randint(1000, 10000)),
                "chromosome": chromosome,
                "start_position": start_pos,
                "end_position": start_pos + random.randint(1000, 10000),
                "strand": random.choice(['+', '-']),
                "species_id": random.randint(1, len(self.species))  # 假设species_id从1开始
            }
            genes.append(gene)
        return genes

    def generate_proteins(self, num_proteins: int) -> List[Dict[str, Any]]:
        """生成蛋白质数据"""
        proteins = []
        for i in range(num_proteins):
            proteins.append({
                "protein_name": f"Protein_{i}",
                "uniprot_id": f"P{random.randint(10000, 99999)}",
                "amino_acid_sequence": self.generate_protein_sequence(random.randint(100, 1000)),
                "gene_id": random.randint(1, 1000)  # 假设有1000个基因
            })
        return proteins

    def generate_publications(self, num_publications: int) -> List[Dict[str, Any]]:
        """生成文献数据"""
        publications = []
        for i in range(num_publications):
            publications.append({
                "title": f"Research on Gene Function {i}",
                "authors": ", ".join([f"Author{j}" for j in range(random.randint(1, 5))]),
                "journal": random.choice(self.journals),
                "publication_year": random.randint(2010, 2024),
                "doi": f"10.1234/journal.{random.randint(1000, 9999)}.{i}"
            })
        return publications

    def generate_gene_publications(self, num_genes: int, num_publications: int) -> List[Dict[str, Any]]:
        """生成基因-文献关联数据"""
        associations = []
        for _ in range(num_genes * 2):  # 平均每个基因关联2篇文献
            associations.append({
                "gene_id": random.randint(1, num_genes),
                "publication_id": random.randint(1, num_publications)
            })
        # 去重
        unique_associations = list({(a["gene_id"], a["publication_id"]): a for a in associations}.values())
        return unique_associations

    def generate_experimental_data(self, num_experiments: int) -> List[Dict[str, Any]]:
        """生成实验数据"""
        experiments = []
        for i in range(num_experiments):
            experiment = {
                "experiment_type": random.choice(self.experiment_types),
                "conditions": json.dumps({
                    "temperature": f"{random.randint(20, 37)}°C",
                    "ph": round(random.uniform(6.0, 8.0), 1),
                    "time": f"{random.randint(1, 48)}h"
                }),
                "results": json.dumps({
                    "measurement": round(random.uniform(0, 100), 2),
                    "p_value": round(random.uniform(0, 0.05), 4),
                    "fold_change": round(random.uniform(-5, 5), 2)
                }),
                "gene_id": random.randint(1, 1000),  # 假设有1000个基因
                "publication_id": random.randint(1, 500)  # 假设有500篇文献
            }
            experiments.append(experiment)
        return experiments

    def save_to_json(self, data: List[Dict[str, Any]], filename: str):
        """保存数据到JSON文件"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_to_csv(self, data: List[Dict[str, Any]], filename: str):
        """保存数据到CSV文件"""
        filepath = os.path.join(self.data_dir, filename)
        if data:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

    def generate_all_test_data(self,
                             num_users: int = 100,
                             num_genes: int = 1000,
                             num_proteins: int = 800,
                             num_publications: int = 500,
                             num_experiments: int = 2000):
        """生成所有测试数据"""
        print("开始生成测试数据...")
        
        # 生成并保存物种数据
        self.save_to_json(self.species, "species.json")
        print("✓ 物种数据已生成")
        
        # 生成并保存用户相关数据
        users_data = self.generate_users(num_users)
        self.save_to_json(users_data["users"], "users.json")
        self.save_to_json(users_data["creators"], "creators.json")
        self.save_to_json(users_data["managers"], "managers.json")
        self.save_to_json(users_data["readers"], "readers.json")
        print("✓ 用户数据已生成")
        
        # 生成并保存基因数据
        genes = self.generate_genes(num_genes)
        self.save_to_json(genes, "genes.json")
        self.save_to_csv(genes, "genes.csv")
        print("✓ 基因数据已生成")
        
        # 生成并保存蛋白质数据
        proteins = self.generate_proteins(num_proteins)
        self.save_to_json(proteins, "proteins.json")
        self.save_to_csv(proteins, "proteins.csv")
        print("✓ 蛋白质数据已生成")
        
        # 生成并保存文献数据
        publications = self.generate_publications(num_publications)
        self.save_to_json(publications, "publications.json")
        self.save_to_csv(publications, "publications.csv")
        print("✓ 文献数据已生成")
        
        # 生成并保存基因-文献关联数据
        gene_publications = self.generate_gene_publications(num_genes, num_publications)
        self.save_to_json(gene_publications, "gene_publications.json")
        self.save_to_csv(gene_publications, "gene_publications.csv")
        print("✓ 基因-文献关联数据已生成")
        
        # 生成并保存实验数据
        experiments = self.generate_experimental_data(num_experiments)
        self.save_to_json(experiments, "experimental_data.json")
        self.save_to_csv(experiments, "experimental_data.csv")
        print("✓ 实验数据已生成")
        
        print("\n所有测试数据生成完成！")
        print(f"数据文件保存在: {os.path.abspath(self.data_dir)}")

def main():
    """主函数"""
    generator = TestDataGenerator()
    generator.generate_all_test_data()

if __name__ == "__main__":
    main() 