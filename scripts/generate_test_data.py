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

class TestDataGenerator:
    def __init__(self, data_dir: str = "data"):
        """初始化数据生成器"""
        self.data_dir = data_dir
        self._ensure_data_dir()
        
        # 基础数据
        self.species = [
            {"name": "Homo sapiens", "taxonomy_id": "9606", "common_name": "Human"},
            {"name": "Mus musculus", "taxonomy_id": "10090", "common_name": "Mouse"},
            {"name": "Rattus norvegicus", "taxonomy_id": "10116", "common_name": "Rat"},
            {"name": "Drosophila melanogaster", "taxonomy_id": "7227", "common_name": "Fruit fly"},
            {"name": "Saccharomyces cerevisiae", "taxonomy_id": "4932", "common_name": "Baker's yeast"}
        ]
        
        self.chromosomes = {
            "Homo sapiens": [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"],
            "Mus musculus": [f"chr{i}" for i in range(1, 20)] + ["chrX", "chrY"],
            "Rattus norvegicus": [f"chr{i}" for i in range(1, 21)] + ["chrX", "chrY"],
            "Drosophila melanogaster": [f"chr{chr}" for chr in ["2L", "2R", "3L", "3R", "4", "X", "Y"]],
            "Saccharomyces cerevisiae": [f"chr{i}" for i in range(1, 17)]
        }
        
        self.journals = [
            "Nature", "Science", "Cell", "Genome Research", "Bioinformatics",
            "PLOS ONE", "BMC Genomics", "Nucleic Acids Research"
        ]
        
        self.experiment_types = [
            "RNA-Seq", "ChIP-Seq", "ATAC-Seq", "WGS", "WES",
            "Microarray", "Proteomics", "Metabolomics"
        ]

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

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
            chromosome = random.choice(self.chromosomes[species["name"]])
            sequence_length = random.randint(1000, 10000)
            
            gene = {
                "gene_id": f"GENE{i:06d}",
                "gene_name": f"Gene_{i}",
                "gene_symbol": f"G{i}",
                "sequence": self.generate_dna_sequence(sequence_length),
                "chromosome": chromosome,
                "start_position": random.randint(1, 1000000),
                "end_position": random.randint(1000001, 2000000),
                "strand": random.choice(["+", "-"]),
                "species_id": species["taxonomy_id"]
            }
            genes.append(gene)
        return genes

    def generate_proteins(self, num_proteins: int) -> List[Dict[str, Any]]:
        """生成蛋白质数据"""
        proteins = []
        for i in range(num_proteins):
            sequence_length = random.randint(100, 1000)
            protein = {
                "protein_id": f"PROT{i:06d}",
                "protein_name": f"Protein_{i}",
                "sequence": self.generate_protein_sequence(sequence_length),
                "molecular_weight": round(random.uniform(10000, 100000), 2),
                "isoelectric_point": round(random.uniform(4.0, 10.0), 2),
                "gene_id": f"GENE{random.randint(0, 999999):06d}"
            }
            proteins.append(protein)
        return proteins

    def generate_publications(self, num_publications: int) -> List[Dict[str, Any]]:
        """生成文献数据"""
        publications = []
        for i in range(num_publications):
            year = random.randint(2010, 2023)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            publication_date = datetime(year, month, day)
            
            publication = {
                "publication_id": f"PUB{i:06d}",
                "title": f"Research Paper {i}",
                "authors": f"Author_{random.randint(1, 5)}, Author_{random.randint(6, 10)}",
                "journal": random.choice(self.journals),
                "publication_date": publication_date.strftime("%Y-%m-%d"),
                "doi": f"10.1234/paper.{i:06d}"
            }
            publications.append(publication)
        return publications

    def generate_experimental_data(self, num_experiments: int) -> List[Dict[str, Any]]:
        """生成实验数据"""
        experiments = []
        for i in range(num_experiments):
            experiment = {
                "experiment_id": f"EXP{i:06d}",
                "experiment_type": random.choice(self.experiment_types),
                "gene_id": f"GENE{random.randint(0, 999999):06d}",
                "condition": f"Condition_{random.randint(1, 5)}",
                "value": round(random.uniform(0, 100), 2),
                "p_value": round(random.uniform(0, 1), 4),
                "publication_id": f"PUB{random.randint(0, 999999):06d}"
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

    def save_to_fasta(self, sequences: List[Dict[str, str]], filename: str):
        """保存序列数据到FASTA文件"""
        filepath = os.path.join(self.data_dir, filename)
        records = []
        for seq in sequences:
            record = SeqRecord(
                Seq(seq["sequence"]),
                id=seq["gene_id"],
                description=f"gene_name={seq['gene_name']}"
            )
            records.append(record)
        SeqIO.write(records, filepath, "fasta")

    def generate_all_test_data(self, 
                             num_genes: int = 1000,
                             num_proteins: int = 800,
                             num_publications: int = 500,
                             num_experiments: int = 2000):
        """生成所有测试数据"""
        print("开始生成测试数据...")
        
        # 生成并保存物种数据
        self.save_to_json(self.species, "species.json")
        print("✓ 物种数据已生成")
        
        # 生成并保存基因数据
        genes = self.generate_genes(num_genes)
        self.save_to_json(genes, "genes.json")
        self.save_to_csv(genes, "genes.csv")
        self.save_to_fasta(genes, "genes.fasta")
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