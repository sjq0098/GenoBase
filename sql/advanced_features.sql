-- GenoBase 高级数据库特性
-- 包含触发器、存储过程和视图的定义

USE GenoBase;

-- =============================================
-- 1. 触发器：用于控制添加操作
-- =============================================

-- 1.1 在添加蛋白质前验证关联的基因是否存在
DELIMITER $$
CREATE TRIGGER before_protein_insert
BEFORE INSERT ON Proteins
FOR EACH ROW
BEGIN
    DECLARE gene_exists INT;
    SELECT COUNT(*) INTO gene_exists FROM Genes WHERE gene_id = NEW.gene_id;
    IF gene_exists = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot add protein: Associated gene_id does not exist.';
    END IF;
END$$
DELIMITER ;

-- 1.2 在添加实验数据前验证关联的基因是否存在
DELIMITER $$
CREATE TRIGGER before_experiment_insert
BEFORE INSERT ON Experimental_Data
FOR EACH ROW
BEGIN
    IF NEW.gene_id IS NOT NULL THEN
        DECLARE gene_exists INT;
        SELECT COUNT(*) INTO gene_exists FROM Genes WHERE gene_id = NEW.gene_id;
        IF gene_exists = 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot add experiment: Associated gene_id does not exist.';
        END IF;
    END IF;
END$$
DELIMITER ;

-- =============================================
-- 2. 存储过程：用于控制更新操作
-- =============================================

-- 2.1 更新基因名称并同步更新关联蛋白质的描述
DELIMITER $$
CREATE PROCEDURE UpdateGeneAndProteinInfo (
    IN p_gene_id INT,
    IN p_new_gene_name VARCHAR(255)
)
BEGIN
    DECLARE old_gene_name VARCHAR(255);
    DECLARE affected_rows INT;
    DECLARE base_protein_name VARCHAR(100);
    
    -- 开始事务
    START TRANSACTION;
    
    -- 获取旧的基因名称
    SELECT gene_name INTO old_gene_name FROM Genes WHERE gene_id = p_gene_id;
    
    IF old_gene_name IS NOT NULL THEN
        -- 更新基因名称
        UPDATE Genes SET gene_name = p_new_gene_name WHERE gene_id = p_gene_id;
        SET affected_rows = ROW_COUNT();
        
        IF affected_rows > 0 THEN
            -- 更新关联的蛋白质描述
            -- 首先获取蛋白质的基本名称（去除之前的重命名信息）
            UPDATE Proteins
            SET protein_name = REGEXP_REPLACE(
                protein_name,
                ' \\(Gene renamed from .*\\)$',
                ''
            )
            WHERE gene_id = p_gene_id;
            
            -- 然后添加新的重命名信息
            UPDATE Proteins
            SET protein_name = CONCAT(protein_name, ' (Gene renamed from ', old_gene_name, ' to ', p_new_gene_name, ')')
            WHERE gene_id = p_gene_id;
            
            COMMIT;
            SELECT CONCAT('Gene updated successfully. Affected proteins: ', ROW_COUNT()) AS result;
        ELSE
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Failed to update gene.';
        END IF;
    ELSE
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Gene ID not found.';
    END IF;
END$$
DELIMITER ;

-- 2.2 更新物种信息并记录变更历史
DELIMITER $$
CREATE PROCEDURE UpdateSpeciesInfo (
    IN p_species_id INT,
    IN p_scientific_name VARCHAR(100),
    IN p_common_name VARCHAR(100),
    IN p_description TEXT
)
BEGIN
    DECLARE old_scientific_name VARCHAR(100);
    DECLARE old_common_name VARCHAR(100);
    
    -- 开始事务
    START TRANSACTION;
    
    -- 获取旧的物种信息
    SELECT scientific_name, common_name 
    INTO old_scientific_name, old_common_name
    FROM Species 
    WHERE species_id = p_species_id;
    
    IF old_scientific_name IS NOT NULL THEN
        -- 更新物种信息
        UPDATE Species 
        SET 
            scientific_name = IFNULL(p_scientific_name, scientific_name),
            common_name = IFNULL(p_common_name, common_name),
            description = IFNULL(p_description, description),
            updated_at = CURRENT_TIMESTAMP
        WHERE species_id = p_species_id;
        
        -- 这里可以添加记录变更历史的逻辑
        -- 例如插入到一个Species_Changes表（如果有的话）
        
        COMMIT;
        SELECT 'Species updated successfully' AS result;
    ELSE
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Species ID not found.';
    END IF;
END$$
DELIMITER ;

-- =============================================
-- 3. 视图：用于支持查询操作
-- =============================================

-- 3.1 基因-物种-蛋白质数量视图
CREATE OR REPLACE VIEW GeneProteinCountBySpecies AS
SELECT
    g.gene_id,
    g.gene_name,
    s.scientific_name AS species_name,
    COUNT(p.protein_id) AS protein_count
FROM
    Genes g
JOIN
    Species s ON g.species_id = s.species_id
LEFT JOIN
    Proteins p ON g.gene_id = p.gene_id
GROUP BY
    g.gene_id, g.gene_name, s.scientific_name;

-- 3.2 基因研究活跃度视图（基于文献和实验数量）
CREATE OR REPLACE VIEW GeneResearchActivity AS
SELECT 
    g.gene_id,
    g.gene_name,
    COALESCE(s.scientific_name, 'Unknown') AS species_name,
    COUNT(DISTINCT gp.publication_id) AS publication_count,
    COUNT(DISTINCT e.experiment_id) AS experiment_count,
    (COUNT(DISTINCT gp.publication_id) * 2 + COUNT(DISTINCT e.experiment_id)) AS activity_score
FROM 
    Genes g
    LEFT JOIN Species s ON g.species_id = s.species_id
    LEFT JOIN Gene_Publications gp ON g.gene_id = gp.gene_id
    LEFT JOIN Experimental_Data e ON g.gene_id = e.gene_id
GROUP BY 
    g.gene_id, g.gene_name, s.scientific_name
ORDER BY 
    activity_score DESC;

-- 3.3 用户角色信息视图
CREATE OR REPLACE VIEW UserRoleInfo AS
SELECT
    u.user_id,
    u.username,
    u.email,
    u.user_type,
    u.is_active,  -- 新增
    CASE 
        WHEN u.user_type = 'creator' THEN c.institution
        WHEN u.user_type = 'manager' THEN m.department
        WHEN u.user_type = 'reader' THEN r.organization
        ELSE NULL
    END AS affiliation,
    CASE 
        WHEN u.user_type = 'creator' THEN c.research_field
        WHEN u.user_type = 'manager' THEN m.access_level
        WHEN u.user_type = 'reader' THEN r.subscription_type
        ELSE NULL
    END AS role_detail
FROM
    Users u
LEFT JOIN
    Creators c ON u.user_id = c.user_id
LEFT JOIN
    Managers m ON u.user_id = m.user_id
LEFT JOIN
    Readers r ON u.user_id = r.user_id;

-- =============================================
-- 4. 事务控制的删除操作
-- =============================================

-- 4.1 删除物种及其关联数据的存储过程
DELIMITER $$
CREATE PROCEDURE DeleteSpeciesWithRelatedData(
    IN p_species_id INT
)
BEGIN
    DECLARE gene_count INT;
    
    -- 检查物种是否存在
    SELECT COUNT(*) INTO gene_count FROM Species WHERE species_id = p_species_id;
    
    IF gene_count = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Species ID not found.';
    ELSE
        START TRANSACTION;
        
        -- 删除该物种相关的实验数据
        DELETE FROM Experimental_Data 
        WHERE gene_id IN (SELECT gene_id FROM Genes WHERE species_id = p_species_id);
        
        -- 删除该物种基因与文献的关联
        DELETE FROM Gene_Publications 
        WHERE gene_id IN (SELECT gene_id FROM Genes WHERE species_id = p_species_id);
        
        -- 删除该物种相关的蛋白质
        DELETE FROM Proteins 
        WHERE gene_id IN (SELECT gene_id FROM Genes WHERE species_id = p_species_id);
        
        -- 删除该物种的基因
        DELETE FROM Genes WHERE species_id = p_species_id;
        
        -- 最后删除物种本身
        DELETE FROM Species WHERE species_id = p_species_id;
        
        COMMIT;
        
        SELECT 'Species and all related data deleted successfully' AS result;
    END IF;
END$$
DELIMITER ; 