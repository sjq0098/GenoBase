# GenoBase 数据库表结构

## 1. 用户表 (Users)
```sql
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role ENUM('creator', 'manager', 'reader') NOT NULL,
    api_key VARCHAR(64) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_users_username ON Users(username);
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_users_api_key ON Users(api_key);
```

## 2. 物种表 (Species)
```sql
CREATE TABLE Species (
    species_id INT PRIMARY KEY AUTO_INCREMENT,
    scientific_name VARCHAR(100) NOT NULL,
    common_name VARCHAR(100),
    taxonomy_id VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_species_name ON Species(scientific_name);
CREATE INDEX idx_species_taxonomy ON Species(taxonomy_id);
```

## 3. 基因表 (Genes)
```sql
CREATE TABLE Genes (
    gene_id INT PRIMARY KEY AUTO_INCREMENT,
    gene_name VARCHAR(100) NOT NULL,
    gene_symbol VARCHAR(50),
    sequence TEXT NOT NULL,
    chromosome VARCHAR(50),
    start_position INT,
    end_position INT,
    strand ENUM('+', '-'),
    species_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (species_id) REFERENCES Species(species_id)
);

-- 索引
CREATE INDEX idx_genes_name ON Genes(gene_name);
CREATE INDEX idx_genes_symbol ON Genes(gene_symbol);
CREATE INDEX idx_genes_species ON Genes(species_id);
CREATE INDEX idx_genes_chromosome ON Genes(chromosome);
```

## 4. 蛋白质表 (Proteins)
```sql
CREATE TABLE Proteins (
    protein_id INT PRIMARY KEY AUTO_INCREMENT,
    protein_name VARCHAR(100) NOT NULL,
    uniprot_id VARCHAR(50),
    amino_acid_sequence TEXT NOT NULL,
    gene_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gene_id) REFERENCES Genes(gene_id)
);

-- 索引
CREATE INDEX idx_proteins_name ON Proteins(protein_name);
CREATE INDEX idx_proteins_uniprot ON Proteins(uniprot_id);
CREATE INDEX idx_proteins_gene ON Proteins(gene_id);
```

## 5. 文献表 (Publications)
```sql
CREATE TABLE Publications (
    publication_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    authors TEXT NOT NULL,
    journal VARCHAR(100),
    publication_year INT,
    doi VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_publications_title ON Publications(title);
CREATE INDEX idx_publications_doi ON Publications(doi);
CREATE INDEX idx_publications_year ON Publications(publication_year);
```

## 6. 基因-文献关联表 (Gene_Publications)
```sql
CREATE TABLE Gene_Publications (
    gene_id INT,
    publication_id INT,
    PRIMARY KEY (gene_id, publication_id),
    FOREIGN KEY (gene_id) REFERENCES Genes(gene_id),
    FOREIGN KEY (publication_id) REFERENCES Publications(publication_id)
);
```

## 7. 实验数据表 (Experimental_Data)
```sql
CREATE TABLE Experimental_Data (
    experiment_id INT PRIMARY KEY AUTO_INCREMENT,
    experiment_type VARCHAR(100) NOT NULL,
    conditions TEXT,
    results TEXT,
    gene_id INT,
    publication_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gene_id) REFERENCES Genes(gene_id),
    FOREIGN KEY (publication_id) REFERENCES Publications(publication_id)
);

-- 索引
CREATE INDEX idx_experiments_gene ON Experimental_Data(gene_id);
CREATE INDEX idx_experiments_publication ON Experimental_Data(publication_id);
```

## 8. 数据库关系说明

### 8.1 一对多关系
1. 物种-基因
   - 一个物种可以有多个基因
   - 通过 species_id 外键关联

2. 基因-蛋白质
   - 一个基因可以编码多个蛋白质
   - 通过 gene_id 外键关联

3. 基因-实验数据
   - 一个基因可以有多个实验数据
   - 通过 gene_id 外键关联

### 8.2 多对多关系
1. 基因-文献
   - 一个基因可以关联多个文献
   - 一个文献可以关联多个基因
   - 通过 Gene_Publications 关联表实现

## 9. 索引设计说明

### 9.1 主键索引
- 所有表都使用自增的 INT 类型作为主键
- 主键自动创建聚集索引

### 9.2 外键索引
- 所有外键字段都创建了索引
- 用于优化关联查询性能

### 9.3 查询优化索引
- 用户表：用户名、邮箱、API密钥
- 基因表：基因名称、符号、染色体
- 蛋白质表：蛋白质名称、UniProt ID
- 文献表：标题、DOI、发表年份

## 10. 数据完整性约束

### 10.1 非空约束
- 用户名、密码、邮箱
- 基因名称、序列
- 蛋白质名称、氨基酸序列
- 文献标题、作者

### 10.2 唯一约束
- 用户名
- 邮箱
- API密钥
- DOI

### 10.3 外键约束
- 基因表的物种ID
- 蛋白质表的基因ID
- 实验数据表的基因ID和文献ID
- 基因-文献关联表的基因ID和文献ID 