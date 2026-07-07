SELECT * FROM `wide_2026.csv` wc
LIMIT 10;

SELECT * FROM wide26;

------------------------------

-- 0) Start fresh
DROP TABLE IF EXISTS `wide26`;
CREATE TABLE `wide26` LIKE `wide_2026.csv`;

-- 1) Change all *_m columns to DECIMAL(7,2) in wide26
SET SESSION group_concat_max_len = 1000000;

SELECT GROUP_CONCAT(
         CONCAT('MODIFY COLUMN `', COLUMN_NAME, '` DECIMAL(7,2) NULL')
         ORDER BY ORDINAL_POSITION
         SEPARATOR ', '
       )
INTO @alter_cols
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'wide26'
  AND COLUMN_NAME LIKE '%\\_m' ESCAPE '\\';

SET @sql_alter = CONCAT('ALTER TABLE `wide26` ', @alter_cols);
PREPARE s1 FROM @sql_alter;
EXECUTE s1;
DEALLOCATE PREPARE s1;

SELECT GROUP_CONCAT(
         CASE
           WHEN COLUMN_NAME LIKE '%\\_m' ESCAPE '\\' THEN
             CONCAT(
               'CASE ',
               'WHEN NULLIF(TRIM(`', COLUMN_NAME, '`), '''') IS NULL THEN NULL ',
               'WHEN CAST(NULLIF(TRIM(`', COLUMN_NAME, '`), '''') AS DECIMAL(16,6)) <= 1 ',
               'THEN ROUND(CAST(NULLIF(TRIM(`', COLUMN_NAME, '`), '''') AS DECIMAL(16,6)) * 100, 2) ',
               'ELSE ROUND(CAST(NULLIF(TRIM(`', COLUMN_NAME, '`), '''') AS DECIMAL(16,6)), 2) ',
               'END AS `', COLUMN_NAME, '`'
             )
           ELSE CONCAT('`', COLUMN_NAME, '`')
         END
         ORDER BY ORDINAL_POSITION
         SEPARATOR ', '
       )
INTO @select_list
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'wide_2026.csv';

SET @sql_insert = CONCAT(
  'INSERT INTO `wide26` SELECT ',
  @select_list,
  ' FROM `wide_2026.csv`'
);

PREPARE s FROM @sql_insert;
EXECUTE s;
DEALLOCATE PREPARE s;

SELECT count(DISTINCT country) FROM wide26;
WHERE `primary` = 137379;

SELECT survey, COUNT(rlevel1_m), count(rlevel2_m), count(rlevel3_m),
count(rlevel4_m), COUNT(slevel1_m), count(slevel2_m), count(slevel3_m),
count(slevel4_m), COUNT(mlevel1_m), count(mlevel2_m), count(mlevel3_m),
count(mlevel4_m) 
FROM wide26
GROUP BY survey; 

SELECT level, COUNT(rlevel1_m), count(rlevel2_m), count(rlevel3_m),
count(rlevel4_m), COUNT(slevel1_m), count(slevel2_m), count(slevel3_m),
count(slevel4_m), COUNT(mlevel1_m), count(mlevel2_m), count(mlevel3_m),
count(mlevel4_m) 
FROM wide26
GROUP BY level;

SELECT avg(rlevel1_m) + avg(rlevel2_m) + avg(rlevel3_m) +
avg(rlevel4_m) / 4 AS avg_r
FROM wide26
WHERE country = 'Togo'
AND `language` = 'Yes'; 

SELECT * FROM wide26 WHERE country = 'Togo';

SELECT * FROM wide26;
LIMIT 400;

SELECT AVG(slevel1_m), AVG(slevel2_m), AVG(slevel3_m), AVG(slevel4_m)
FROM wide26
WHERE country = 'Australia'
AND survey ='TIMSS'
AND YEAR = 2015
AND LEVEL = 'early grades'
AND `language` = 'Yes';

SELECT DISTINCT country FROM wide26;

UPDATE wide26 
SET country = CASE country
    WHEN "CΓ΄te d'Ivoire" THEN "Côte d'Ivoire"
    WHEN 'Viet Nam' THEN 'Vietnam'
    WHEN 'Syrian A. R.' THEN 'Syria'
    WHEN 'Trinidad/Tobago' THEN 'Trinidad and Tobago'
    WHEN 'Rep. Moldova' THEN 'Moldova'
    WHEN 'Rep. of Korea' THEN 'South Korea'
    WHEN 'Iran, Isl. Rep.' THEN 'Iran'
    WHEN 'Brunei Daruss.' THEN 'Brunei'
    WHEN 'Bosnia/Herzeg.' THEN 'Bosnia and Herzegovina'
    WHEN 'Dominican Rep.' THEN 'Dominican Republic'
    WHEN 'Russian Fed.' THEN 'Russia'
    ELSE country -- keeps everything else unchanged
END;

UPDATE wide26
SET country = CASE country
    WHEN 'CΓ΄te d''Ivoire' THEN 'Côte d''Ivoire'
    WHEN 'Viet Nam' THEN 'Vietnam'
    WHEN 'Syrian A. R.' THEN 'Syria'
    WHEN 'Trinidad/Tobago' THEN 'Trinidad and Tobago'
    WHEN 'Rep. Moldova' THEN 'Moldova'
    WHEN 'Rep. of Korea' THEN 'South Korea'
    WHEN 'Iran, Isl. Rep.' THEN 'Iran'
    WHEN 'Brunei Daruss.' THEN 'Brunei'
    WHEN 'Bosnia/Herzeg.' THEN 'Bosnia and Herzegovina'
    WHEN 'Dominican Rep.' THEN 'Dominican Republic'
    WHEN 'Russian Fed.' THEN 'Russia'
    ELSE country
END;

DROP TABLE IF EXISTS wide;

CREATE TABLE wide AS
SELECT
    country,
    level,
    income_group,
    survey,
    sex,
    location,
    wealth,
    language,
    ROUND(AVG(CAST(NULLIF(TRIM(rlevel1_m), '') AS DECIMAL(10,4))), 2) AS rlevel1,
	ROUND(AVG(CAST(NULLIF(TRIM(mlevel1_m), '') AS DECIMAL(10,4))), 2) AS mlevel1,
    ROUND(AVG(CAST(NULLIF(TRIM(slevel1_m), '') AS DECIMAL(10,4))), 2) AS slevel1,
    ROUND(AVG(CAST(NULLIF(TRIM(rlevel2_m), '') AS DECIMAL(10,4))), 2) AS rlevel2,
    ROUND(AVG(CAST(NULLIF(TRIM(mlevel2_m), '') AS DECIMAL(10,4))), 2) AS mlevel2,
    ROUND(AVG(CAST(NULLIF(TRIM(slevel2_m), '') AS DECIMAL(10,4))), 2) AS slevel2,
    ROUND(AVG(CAST(NULLIF(TRIM(rlevel3_m), '') AS DECIMAL(10,4))), 2) AS rlevel3,
    ROUND(AVG(CAST(NULLIF(TRIM(mlevel3_m), '') AS DECIMAL(10,4))), 2) AS mlevel3,
    ROUND(AVG(CAST(NULLIF(TRIM(slevel3_m), '') AS DECIMAL(10,4))), 2) AS slevel3,
    ROUND(AVG(CAST(NULLIF(TRIM(rlevel4_m), '') AS DECIMAL(10,4))), 2) AS rlevel4,
    ROUND(AVG(CAST(NULLIF(TRIM(mlevel4_m), '') AS DECIMAL(10,4))), 2) AS mlevel4,
    ROUND(AVG(CAST(NULLIF(TRIM(slevel4_m), '') AS DECIMAL(10,4))), 2) AS slevel4
FROM wide26
GROUP BY
    country,
    level,
    income_group,
    survey,
    sex,
    location,
    wealth,
    language;
    
DROP TABLE IF EXISTS wide_simple;

CREATE TABLE wide_simple AS
SELECT
    language,
    level,
    ROUND(AVG(CAST(NULLIF(TRIM(rlevel1_m), '') AS DECIMAL(10,4))), 2) AS rlevel1,
	ROUND(AVG(CAST(NULLIF(TRIM(mlevel1_m), '') AS DECIMAL(10,4))), 2) AS mlevel1,
    ROUND(AVG(CAST(NULLIF(TRIM(slevel1_m), '') AS DECIMAL(10,4))), 2) AS slevel1,
    ROUND(AVG(CAST(NULLIF(TRIM(rlevel2_m), '') AS DECIMAL(10,4))), 2) AS rlevel2,
    ROUND(AVG(CAST(NULLIF(TRIM(mlevel2_m), '') AS DECIMAL(10,4))), 2) AS mlevel2,
    ROUND(AVG(CAST(NULLIF(TRIM(slevel2_m), '') AS DECIMAL(10,4))), 2) AS slevel2,
    ROUND(AVG(CAST(NULLIF(TRIM(rlevel3_m), '') AS DECIMAL(10,4))), 2) AS rlevel3,
    ROUND(AVG(CAST(NULLIF(TRIM(mlevel3_m), '') AS DECIMAL(10,4))), 2) AS mlevel3,
    ROUND(AVG(CAST(NULLIF(TRIM(slevel3_m), '') AS DECIMAL(10,4))), 2) AS slevel3,
    ROUND(AVG(CAST(NULLIF(TRIM(rlevel4_m), '') AS DECIMAL(10,4))), 2) AS rlevel4,
    ROUND(AVG(CAST(NULLIF(TRIM(mlevel4_m), '') AS DECIMAL(10,4))), 2) AS mlevel4,
    ROUND(AVG(CAST(NULLIF(TRIM(slevel4_m), '') AS DECIMAL(10,4))), 2) AS slevel4
FROM wide26
GROUP BY LANGUAGE, level; 
   
SELECT DISTINCT category FROM wide26;

SELECT avg(rlevel1_m), avg(slevel2_m), avg(mlevel3_m)
FROM wide26 w
UNION ALL
SELECT avg(rlevel1_m), avg(slevel2_m), avg(mlevel3_m)
FROM wide26 w
WHERE `language` = 'Speaks Language At Home';


SELECT * FROM wide_simple;

SELECT DISTINCT(income_group) FROM wide;

SELECT
  SUM(CASE WHEN mlevel1_m = '' THEN 1 ELSE 0 END) AS mlevel1_m_blank,
  SUM(CASE WHEN rlevel1_m = '' THEN 1 ELSE 0 END) AS rlevel1_m_blank,
  SUM(CASE WHEN slevel1_m = '' THEN 1 ELSE 0 END) AS slevel1_m_blank,
  SUM(CASE WHEN mlevel2_m = '' THEN 1 ELSE 0 END) AS mlevel2_m_blank,
  SUM(CASE WHEN rlevel2_m = '' THEN 1 ELSE 0 END) AS rlevel2_m_blank,
  SUM(CASE WHEN slevel2_m = '' THEN 1 ELSE 0 END) AS slevel2_m_blank,
  SUM(CASE WHEN mlevel3_m = '' THEN 1 ELSE 0 END) AS mlevel3_m_blank,
  SUM(CASE WHEN rlevel3_m = '' THEN 1 ELSE 0 END) AS rlevel3_m_blank,
  SUM(CASE WHEN slevel3_m = '' THEN 1 ELSE 0 END) AS slevel3_m_blank,
  SUM(CASE WHEN mlevel4_m = '' THEN 1 ELSE 0 END) AS mlevel4_m_blank,
  SUM(CASE WHEN rlevel4_m = '' THEN 1 ELSE 0 END) AS rlevel4_m_blank,
  SUM(CASE WHEN slevel4_m = '' THEN 1 ELSE 0 END) AS slevel4_m_blank
FROM wide26;

UPDATE wide26
SET rlevel4_m = NULL 
WHERE rlevel4_m = 0;

SELECT LANGUAGE, count(language)
FROM wide
GROUP by language;

SELECT avg(rlevel1) from wide
WHERE rlevel1 IS NOT NULL
and rlevel1 NOT in ('', 0.00)
AND `language` = 'Yes'
AND `level` ='early grades'
UNION ALL
SELECT avg(rlevel1) from wide
WHERE rlevel1 IS NOT NULL
and rlevel1 NOT in ('', 0.00)
AND `language` = 'No'
AND `level` ='early grades'
UNION ALL 
SELECT avg(rlevel1) from wide
WHERE `language` = 'Yes'
AND `level` ='early grades'
UNION ALL
SELECT avg(rlevel1) from wide
WHERE language = 'No'
AND `level` ='early grades'
UNION ALL
SELECT rlevel1 from wide_simple
WHERE rlevel1 IS NOT NULL
and rlevel1 NOT in ('', 0.00)
AND `language` = 'Yes'
AND `level` ='early grades'
UNION ALL
SELECT rlevel1 from wide_simple
WHERE rlevel1 IS NOT NULL
and rlevel1 NOT in ('', 0.00)
AND `language` = 'No'
AND `level` ='early grades'
UNION ALL 
SELECT rlevel1 from wide_simple
WHERE `language` = 'Yes'
AND `level` ='early grades'
UNION ALL
SELECT rlevel1 from wide_simple
WHERE language = 'No'
AND `level` ='early grades';

SELECT * FROM wide_simple
WHERE LEVEL ='early grades';

SELECT * FROM wide_simple;

SELECT survey, count(survey)
FROM wide26
GROUP BY survey
ORDER BY count(survey) desc;

SELECT year, count(YEAR)
FROM wide26
GROUP BY `year` 
ORDER BY count(YEAR) desc;