-- GenoBase 数据库初始化

-- 创建数据库
CREATE DATABASE IF NOT EXISTS GenoBase
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE GenoBase;

-- 1. 基础用户表
CREATE TABLE IF NOT EXISTS Users (
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

-- 2. 创建者表（继承自Users）
CREATE TABLE IF NOT EXISTS Creators (
    user_id INT PRIMARY KEY,
    institution VARCHAR(100),
    research_field VARCHAR(100),
    max_storage_size BIGINT DEFAULT 1073741824, -- 默认1GB存储空间
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 3. 管理员表（继承自Users）
CREATE TABLE IF NOT EXISTS Managers (
    user_id INT PRIMARY KEY,
    department VARCHAR(100),
    access_level ENUM('full', 'limited') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 4. 读者表（继承自Users）
CREATE TABLE IF NOT EXISTS Readers (
    user_id INT PRIMARY KEY,
    organization VARCHAR(100),
    subscription_type ENUM('free', 'premium') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 用户表索引
CREATE INDEX  idx_users_username ON Users(username);
CREATE INDEX  idx_users_email ON Users(email);
CREATE INDEX  idx_users_api_key ON Users(api_key);
CREATE INDEX  idx_users_type ON Users(user_type);

-- 创建者表索引
CREATE INDEX  idx_creators_institution ON Creators(institution);
CREATE INDEX  idx_creators_research_field ON Creators(research_field);

-- 管理员表索引
CREATE INDEX  idx_managers_department ON Managers(department);
CREATE INDEX  idx_managers_access_level ON Managers(access_level);

-- 读者表索引
CREATE INDEX  idx_readers_organization ON Readers(organization);
CREATE INDEX  idx_readers_subscription ON Readers(subscription_type);

-- 2. 物种表
CREATE TABLE IF NOT EXISTS Species (
    species_id INT PRIMARY KEY AUTO_INCREMENT,
    scientific_name VARCHAR(100) NOT NULL,
    common_name VARCHAR(100),
    taxonomy_id VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 物种表索引
CREATE INDEX  idx_species_name ON Species(scientific_name);
CREATE INDEX  idx_species_taxonomy ON Species(taxonomy_id);

-- 3. 基因表
CREATE TABLE IF NOT EXISTS Genes (
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

-- 基因表索引
CREATE INDEX  idx_genes_name ON Genes(gene_name);
CREATE INDEX  idx_genes_symbol ON Genes(gene_symbol);
CREATE INDEX  idx_genes_species ON Genes(species_id);
CREATE INDEX  idx_genes_chromosome ON Genes(chromosome);

-- 4. 蛋白质表
CREATE TABLE IF NOT EXISTS Proteins (
    protein_id INT PRIMARY KEY AUTO_INCREMENT,
    protein_name VARCHAR(100) NOT NULL,
    uniprot_id VARCHAR(50),
    amino_acid_sequence TEXT NOT NULL,
    gene_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gene_id) REFERENCES Genes(gene_id)
);

-- 蛋白质表索引
CREATE INDEX  idx_proteins_name ON Proteins(protein_name);
CREATE INDEX  idx_proteins_uniprot ON Proteins(uniprot_id);
CREATE INDEX  idx_proteins_gene ON Proteins(gene_id);

-- 5. 文献表
CREATE TABLE IF NOT EXISTS Publications (
    publication_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    authors TEXT NOT NULL,
    journal VARCHAR(100),
    publication_year INT,
    doi VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 文献表索引
CREATE INDEX  idx_publications_title ON Publications(title);
CREATE INDEX  idx_publications_doi ON Publications(doi);
CREATE INDEX  idx_publications_year ON Publications(publication_year);

-- 6. 基因-文献关联表
CREATE TABLE IF NOT EXISTS Gene_Publications (
    gene_id INT,
    publication_id INT,
    PRIMARY KEY (gene_id, publication_id),
    FOREIGN KEY (gene_id) REFERENCES Genes(gene_id),
    FOREIGN KEY (publication_id) REFERENCES Publications(publication_id)
);

-- 7. 实验数据表
CREATE TABLE IF NOT EXISTS Experimental_Data (
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

-- 实验数据表索引
CREATE INDEX  idx_experiments_gene ON Experimental_Data(gene_id);
CREATE INDEX  idx_experiments_publication ON Experimental_Data(publication_id);

-- 添加注释
ALTER TABLE Users COMMENT '用户信息表';
ALTER TABLE Species COMMENT '物种信息表';
ALTER TABLE Genes COMMENT '基因信息表';
ALTER TABLE Proteins COMMENT '蛋白质信息表';
ALTER TABLE Publications COMMENT '文献信息表';
ALTER TABLE Gene_Publications COMMENT '基因-文献关联表';
ALTER TABLE Experimental_Data COMMENT '实验数据表'; 