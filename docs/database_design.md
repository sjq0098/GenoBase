# GenoBase 生物信息管理数据库系统设计文档

## 1. 系统概述

### 1.1 系统简介
GenoBase 是一个现代化的生物信息管理数据库系统，旨在存储和管理多种类型的现代生物信息数据。系统采用前后端分离架构，后端使用 Python FastAPI 框架，前端使用 Vue.js 3 和 Element Plus，数据库采用 MySQL。

### 1.2 核心数据内容
- **物种（Organism）信息**：各物种的基本信息和分类描述
- **基因（Gene）信息**：包含基因的符号、描述、染色体位置等
- **转录本（Transcript）信息**：与基因相关的多种转录本数据
- **序列（Sequence）信息**：包括 DNA、RNA 以及 Protein 序列信息，采用子类（继承）形式区分
- **表达（Expression）信息**：各组织或条件下基因表达水平
- **文献（Publication）信息**：与基因和实验相关的科研文献

### 1.3 目标用户与使用场景
- **数据库创建者**：负责项目整体搭建和数据库结构设计
- **数据库管理者**：负责日常维护、数据导入、数据备份、权限分配等
- **数据库阅读者**：对生物信息数据进行查询、分析、批量下载
- **外部开发者**：通过 API 获取数据用于二次开发分析，需要注册账号和 API key

### 1.4 系统特性
1. **双重数据访问方式**
   - Web 前端：提供图形化查询界面，支持多关键词查询和批量下载
   - API 方式：用户注册后获得 API key，通过 REST API 进行批量数据查询和下载

2. **多级权限管理**
   - 创建者权限：系统配置、用户管理、数据导入导出
   - 管理者权限：数据维护、用户权限分配
   - 阅读者权限：数据查询和下载

3. **数据批量处理**
   - 支持大规模数据的导入和批量下载
   - 提供数据格式转换功能

4. **数据丰富性与扩展性**
   - 涵盖生物体基本信息、基因组注释和表达信息
   - 支持数据扩展和二次开发

## 2. 数据库设计

### 2.1 核心实体

#### 2.1.1 用户表 (Users)
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
```

#### 2.1.2 物种表 (Species)
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
```

#### 2.1.3 基因表 (Genes)
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
```

#### 2.1.4 转录本表 (Transcripts)
```sql
CREATE TABLE Transcripts (
    transcript_id INT PRIMARY KEY AUTO_INCREMENT,
    transcript_name VARCHAR(100) NOT NULL,
    transcript_type VARCHAR(50),
    sequence TEXT NOT NULL,
    gene_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gene_id) REFERENCES Genes(gene_id)
);
```

#### 2.1.5 蛋白质表 (Proteins)
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
```

#### 2.1.6 表达数据表 (Expression_Data)
```sql
CREATE TABLE Expression_Data (
    expression_id INT PRIMARY KEY AUTO_INCREMENT,
    gene_id INT,
    transcript_id INT,
    tissue VARCHAR(100),
    condition VARCHAR(100),
    expression_level FLOAT,
    measurement_unit VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gene_id) REFERENCES Genes(gene_id),
    FOREIGN KEY (transcript_id) REFERENCES Transcripts(transcript_id)
);
```

#### 2.1.7 文献表 (Publications)
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
```

#### 2.1.8 基因-文献关联表 (Gene_Publications)
```sql
CREATE TABLE Gene_Publications (
    gene_id INT,
    publication_id INT,
    PRIMARY KEY (gene_id, publication_id),
    FOREIGN KEY (gene_id) REFERENCES Genes(gene_id),
    FOREIGN KEY (publication_id) REFERENCES Publications(publication_id)
);
```

#### 2.1.9 实验数据表 (Experimental_Data)
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
```

### 2.2 实体关系

#### 2.2.1 一对多关系
1. **物种-基因**：一个物种可以有多个基因
2. **基因-转录本**：一个基因可以有多个转录本
3. **基因-蛋白质**：一个基因可以编码多个蛋白质
4. **基因-表达数据**：一个基因可以有多个表达数据记录
5. **基因-实验数据**：一个基因可以有多个实验数据

#### 2.2.2 多对多关系
1. **基因-文献**：一个基因可以关联多个文献，一个文献可以关联多个基因

### 2.3 索引设计
- 所有表都使用自增的 INT 类型作为主键
- 所有外键字段都创建了索引
- 为常用查询字段创建索引，如基因名称、符号、染色体等

## 3. 权限设计

### 3.1 权限级别
1. **数据库创建者（Creator）**
   - 系统配置和管理
   - 用户管理（创建、修改、删除用户）
   - 数据导入和导出
   - 数据库结构修改

2. **数据库管理者（Manager）**
   - 数据维护（添加、修改、删除数据）
   - 用户权限分配
   - 数据备份和恢复
   - 系统监控

3. **数据库阅读者（Reader）**
   - 数据查询和浏览
   - 数据下载（单条或批量）
   - 个人设置管理

### 3.2 权限控制实现
- 使用 JWT（JSON Web Token）进行身份验证
- 基于角色的访问控制（RBAC）
- API 访问需要有效的 API key

## 4. 功能模块

### 4.1 Web 前端功能
1. **用户管理**
   - 用户注册和登录
   - 个人信息管理
   - API key 管理

2. **数据查询**
   - 多条件组合查询
   - 高级搜索功能
   - 查询结果导出

3. **数据可视化**
   - 基因表达热图
   - 序列比对可视化
   - 统计分析图表

4. **数据管理**（仅限创建者和管理者）
   - 数据导入和导出
   - 数据编辑和删除
   - 批量操作

### 4.2 API 功能
1. **认证 API**
   - 用户注册
   - 用户登录
   - API key 生成和管理

2. **数据查询 API**
   - 基因信息查询
   - 物种信息查询
   - 表达数据查询
   - 文献信息查询

3. **数据下载 API**
   - 单条数据下载
   - 批量数据下载
   - 数据格式转换

## 5. 技术架构

### 5.1 后端技术栈
- **框架**：Python FastAPI
- **数据库**：MySQL
- **ORM**：SQLAlchemy
- **认证**：JWT
- **文档**：Swagger/OpenAPI

### 5.2 前端技术栈
- **框架**：Vue.js 3
- **UI 组件库**：Element Plus
- **状态管理**：Vuex
- **路由**：Vue Router
- **HTTP 客户端**：Axios

### 5.3 部署架构
- **后端**：Docker 容器化部署
- **前端**：Nginx 静态文件服务
- **数据库**：MySQL 主从架构

## 6. 开发步骤

### 6.1 环境搭建
1. 安装必要软件（Python、Node.js、MySQL）
2. 创建项目目录结构
3. 初始化后端和前端项目

### 6.2 数据库开发
1. 创建数据库和表
2. 实现数据模型
3. 编写数据库迁移脚本

### 6.3 后端开发
1. 实现用户认证系统
2. 开发 API 端点
3. 实现数据导入导出功能
4. 编写单元测试

### 6.4 前端开发
1. 设计用户界面
2. 实现页面组件
3. 集成 API 调用
4. 实现数据可视化

### 6.5 测试与部署
1. 进行功能测试和性能测试
2. 部署到测试环境
3. 进行用户验收测试
4. 部署到生产环境

## 7. 注意事项

### 7.1 安全性
- 所有密码必须加密存储
- 实现 API 访问频率限制
- 防止 SQL 注入和 XSS 攻击
- 定期安全审计

### 7.2 性能优化
- 优化数据库查询
- 实现数据缓存
- 前端资源压缩和懒加载
- 大数据量处理优化

### 7.3 可维护性
- 遵循代码规范
- 编写详细文档
- 模块化设计
- 版本控制管理 