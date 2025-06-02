use genobase;

-- 1.1 查询所有活跃用户
SELECT username, email, user_type 
FROM Users 
WHERE is_active = TRUE;

-- 1.2 按物种查找基因数量
SELECT s.scientific_name, COUNT(g.gene_id) as gene_count
FROM Species s
LEFT JOIN Genes g ON s.species_id = g.species_id
GROUP BY s.species_id, s.scientific_name;

-- 1.3 查找特定染色体上的所有基因
SELECT gene_name, chromosome, start_position, end_position
FROM Genes
WHERE chromosome = 'chr1'
ORDER BY start_position;


-- 2.1 查询每个基因相关的蛋白质和实验数据
SELECT 
    g.gene_name,
    p.protein_name,
    p.uniprot_id,
    COUNT(DISTINCT e.experiment_id) as experiment_count
FROM Genes g
LEFT JOIN Proteins p ON g.gene_id = p.gene_id
LEFT JOIN Experimental_Data e ON g.gene_id = e.gene_id
GROUP BY g.gene_id, g.gene_name, p.protein_name, p.uniprot_id;

-- 2.2 查询每个用户的详细信息（根据用户类型）
SELECT 
    u.username,
    u.email,
    u.user_type,
    CASE 
        WHEN u.user_type = 'creator' THEN c.institution
        WHEN u.user_type = 'manager' THEN m.department
        WHEN u.user_type = 'reader' THEN r.organization
    END as affiliation
FROM Users u
LEFT JOIN Creators c ON u.user_id = c.user_id
LEFT JOIN Managers m ON u.user_id = m.user_id
LEFT JOIN Readers r ON u.user_id = r.user_id;

-- 3.1 统计每种实验类型的数量和平均结果
SELECT 
    experiment_type,
    COUNT(*) as experiment_count,
    COUNT(DISTINCT gene_id) as unique_genes
FROM Experimental_Data
GROUP BY experiment_type;

-- 3.2 查询发表文献最多的前10个基因
SELECT 
    g.gene_name,
    COUNT(gp.publication_id) as publication_count
FROM Genes g
JOIN Gene_Publications gp ON g.gene_id = gp.gene_id
GROUP BY g.gene_id, g.gene_name
ORDER BY publication_count DESC
LIMIT 10;


-- 4.1 找出比平均长度更长的基因
SELECT 
    gene_name,
    LENGTH(sequence) as sequence_length
FROM Genes
WHERE LENGTH(sequence) > (
    SELECT AVG(LENGTH(sequence)) FROM Genes
);

-- 4.2 查找有关联蛋白质但没有实验数据的基因
SELECT g.gene_name
FROM Genes g
WHERE EXISTS (
    SELECT 1 FROM Proteins p WHERE p.gene_id = g.gene_id
)
AND NOT EXISTS (
    SELECT 1 FROM Experimental_Data e WHERE e.gene_id = g.gene_id
);

-- 5.1 使用窗口函数按物种统计基因分布
SELECT 
    s.scientific_name,
    g.chromosome,
    COUNT(*) as genes_in_chromosome,
    COUNT(*) OVER (PARTITION BY s.species_id) as total_genes_in_species
FROM Species s
JOIN Genes g ON s.species_id = g.species_id
GROUP BY s.species_id, s.scientific_name, g.chromosome;

-- 5.2 使用递归CTE查询基因位置重叠
WITH RECURSIVE overlapping_genes AS (
    -- 基础查询：找出所有可能重叠的基因对
    SELECT 
        g1.gene_id as gene1_id,
        g1.gene_name as gene1_name,
        g2.gene_id as gene2_id,
        g2.gene_name as gene2_name
    FROM Genes g1
    JOIN Genes g2 ON 
        g1.chromosome = g2.chromosome AND
        g1.gene_id < g2.gene_id AND
        g1.end_position >= g2.start_position AND
        g1.start_position <= g2.end_position
)
SELECT * FROM overlapping_genes;