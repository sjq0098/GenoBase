# GenoBase 数据库表结构

## 1. 用户表结构

### 1.1 基础用户表 (Users)
```sql
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    user_type ENUM('creator', 'manager', 'reader') NOT NULL,
    api_key VARCHAR(64) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 1.2 创建者表 (Creators)
```sql
CREATE TABLE Creators (
    user_id INT PRIMARY KEY,
    institution VARCHAR(100),
    research_field VARCHAR(100),
    max_storage_size BIGINT DEFAULT 1073741824,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
```

### 1.3 管理员表 (Managers)
```sql
CREATE TABLE Managers (
    user_id INT PRIMARY KEY,
    department VARCHAR(100),
    access_level ENUM('full', 'limited') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
```

### 1.4 读者表 (Readers)
```sql
CREATE TABLE Readers (
    user_id INT PRIMARY KEY,
    organization VARCHAR(100),
    subscription_type ENUM('free', 'premium') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
```

### 1.5 用户表索引
```sql
-- 基础用户表索引
CREATE INDEX idx_users_username ON Users(username);
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_users_api_key ON Users(api_key);
CREATE INDEX idx_users_type ON Users(user_type);

-- 创建者表索引
CREATE INDEX idx_creators_institution ON Creators(institution);
CREATE INDEX idx_creators_research_field ON Creators(research_field);

-- 管理员表索引
CREATE INDEX idx_managers_department ON Managers(department);
CREATE INDEX idx_managers_access_level ON Managers(access_level);

-- 读者表索引
CREATE INDEX idx_readers_organization ON Readers(organization);
CREATE INDEX idx_readers_subscription ON Readers(subscription_type);
```

### 1.6 用户表关系说明
- 基础用户表(Users)作为父表
- 创建者、管理员、读者表作为子表
- 通过user_id实现继承关系
- 使用ON DELETE CASCADE确保数据一致性

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

### 8.1 用户继承关系
1. 基础用户-创建者
   - 一个基础用户可以是创建者
   - 通过 user_id 外键关联
   - 级联删除确保数据一致性

2. 基础用户-管理员
   - 一个基础用户可以是管理员
   - 通过 user_id 外键关联
   - 级联删除确保数据一致性

3. 基础用户-读者
   - 一个基础用户可以是读者
   - 通过 user_id 外键关联
   - 级联删除确保数据一致性

### 8.2 一对多关系
1. 物种-基因
   - 一个物种可以有多个基因
   - 通过 species_id 外键关联

2. 基因-蛋白质
   - 一个基因可以编码多个蛋白质
   - 通过 gene_id 外键关联

3. 基因-实验数据
   - 一个基因可以有多个实验数据
   - 通过 gene_id 外键关联

### 8.3 多对多关系
1. 基因-文献
   - 一个基因可以关联多个文献
   - 一个文献可以关联多个基因
   - 通过 Gene_Publications 关联表实现

## 9. 索引设计说明

### 9.1 用户表索引
- 基础用户表：用户名、邮箱、API密钥、用户类型
- 创建者表：机构、研究领域
- 管理员表：部门、访问级别
- 读者表：组织、订阅类型

### 9.2 主键索引
- 所有表都使用自增的 INT 类型作为主键
- 主键自动创建聚集索引

### 9.3 外键索引
- 所有外键字段都创建了索引
- 用于优化关联查询性能

### 9.4 查询优化索引
- 用户表：用户名、邮箱、API密钥
- 基因表：基因名称、符号、染色体
- 蛋白质表：蛋白质名称、UniProt ID
- 文献表：标题、DOI、发表年份

## 10. 数据完整性约束

### 10.1 用户表约束
- 非空约束：
  - 用户名、密码、邮箱、用户类型
  - 管理员访问级别
  - 读者订阅类型
- 唯一约束：
  - 用户名
  - 邮箱
  - API密钥
- 外键约束：
  - 创建者、管理员、读者表的user_id
- 枚举约束：
  - 用户类型（creator, manager, reader）
  - 管理员访问级别（full, limited）
  - 读者订阅类型（free, premium）

### 10.2 其他表约束
- 非空约束：
  - 基因名称、序列
  - 蛋白质名称、氨基酸序列
  - 文献标题、作者
- 唯一约束：
  - DOI
- 外键约束：
  - 基因表的物种ID
  - 蛋白质表的基因ID
  - 实验数据表的基因ID和文献ID
  - 基因-文献关联表的基因ID和文献ID 