-- "Data" is the table as downloaded from UNESCO's Institute for Statistics
-- "naturalearth2" is a table from naturalearth/amazonaws that includes 
-- a geometry column with polygons for each country

SELECT * FROM DATA;;

SELECT DISTINCT indicatorId FROM DATA;

SELECT * FROM naturalearth2;

CREATE TABLE ne_country_names AS
SELECT NAME FROM naturalearth2;

SELECT * FROM ne_country_names;

DROP TABLE IF EXISTS home_lang_in_school;

CREATE TABLE school_lang AS
SELECT
    indicatorId,
    geoUnit,
    year,
    value,
    qualifier,
    magnitude,
    CAST(NULL AS CHAR(100)) AS country_name
FROM data;

DROP TABLE IF EXISTS school_lang_bckp;

CREATE TABLE school_lang_bkp AS
SELECT * FROM school_lang;

ALTER TABLE school_lang
MODIFY COLUMN country_name VARCHAR(100);

UPDATE school_lang
SET country_name = CASE geoUnit
    WHEN 'ALB' THEN 'Albania'
    WHEN 'ARE' THEN 'United Arab Emirates'
    WHEN 'ARG' THEN 'Argentina'
    WHEN 'ARM' THEN 'Armenia'
    WHEN 'AUS' THEN 'Australia'
    WHEN 'AUT' THEN 'Austria'
    WHEN 'AZE' THEN 'Azerbaijan'
    WHEN 'BDI' THEN 'Burundi'
    WHEN 'BEL' THEN 'Belgium'
    WHEN 'BEN' THEN 'Benin'
    WHEN 'BFA' THEN 'Burkina Faso'
    WHEN 'BGD' THEN 'Bangladesh'
    WHEN 'BGR' THEN 'Bulgaria'
    WHEN 'BHR' THEN 'Bahrain'
    WHEN 'BIH' THEN 'Bosnia and Herz.'
    WHEN 'BLR' THEN 'Belarus'
    WHEN 'BRA' THEN 'Brazil'
    WHEN 'BRN' THEN 'Brunei'
    WHEN 'BWA' THEN 'Botswana'
    WHEN 'CAF' THEN 'Central African Rep.'
    WHEN 'CAN' THEN 'Canada'
    WHEN 'CHE' THEN 'Switzerland'
    WHEN 'CHL' THEN 'Chile'
    WHEN 'CIV' THEN 'Côte d''Ivoire'
    WHEN 'CMR' THEN 'Cameroon'
    WHEN 'COD' THEN 'Dem. Rep. Congo'
    WHEN 'COG' THEN 'Congo'
    WHEN 'COL' THEN 'Colombia'
    WHEN 'CRI' THEN 'Costa Rica'
    WHEN 'CUB' THEN 'Cuba'
    WHEN 'CYP' THEN 'Cyprus'
    WHEN 'CZE' THEN 'Czechia'
    WHEN 'DEU' THEN 'Germany'
    WHEN 'DNK' THEN 'Denmark'
    WHEN 'DOM' THEN 'Dominican Rep.'
    WHEN 'DZA' THEN 'Algeria'
    WHEN 'ECU' THEN 'Ecuador'
    WHEN 'EGY' THEN 'Egypt'
    WHEN 'ESP' THEN 'Spain'
    WHEN 'EST' THEN 'Estonia'
    WHEN 'FIN' THEN 'Finland'
    WHEN 'FJI' THEN 'Fiji'
    WHEN 'FRA' THEN 'France'
    WHEN 'GAB' THEN 'Gabon'
    WHEN 'GBR' THEN 'United Kingdom'
    WHEN 'GEO' THEN 'Georgia'
    WHEN 'GHA' THEN 'Ghana'
    WHEN 'GIN' THEN 'Guinea'
    WHEN 'GMB' THEN 'Gambia'
    WHEN 'GNB' THEN 'Guinea-Bissau'
    WHEN 'GRC' THEN 'Greece'
    WHEN 'GTM' THEN 'Guatemala'
    WHEN 'GUY' THEN 'Guyana'
    WHEN 'HKG' THEN 'Hong Kong'
    WHEN 'HND' THEN 'Honduras'
    WHEN 'HRV' THEN 'Croatia'
    WHEN 'HUN' THEN 'Hungary'
    WHEN 'IDN' THEN 'Indonesia'
    WHEN 'IRL' THEN 'Ireland'
    WHEN 'IRN' THEN 'Iran'
    WHEN 'ISL' THEN 'Iceland'
    WHEN 'ISR' THEN 'Israel'
    WHEN 'ITA' THEN 'Italy'
    WHEN 'JAM' THEN 'Jamaica'
    WHEN 'JOR' THEN 'Jordan'
    WHEN 'JPN' THEN 'Japan'
    WHEN 'KAZ' THEN 'Kazakhstan'
    WHEN 'KGZ' THEN 'Kyrgyzstan'
    WHEN 'KHM' THEN 'Cambodia'
    WHEN 'KIR' THEN 'Kiribati'
    WHEN 'KOR' THEN 'South Korea'
    WHEN 'KWT' THEN 'Kuwait'
    WHEN 'LAO' THEN 'Laos'
    WHEN 'LBN' THEN 'Lebanon'
    WHEN 'LIE' THEN 'Liechtenstein'
    WHEN 'LSO' THEN 'Lesotho'
    WHEN 'LTU' THEN 'Lithuania'
    WHEN 'LUX' THEN 'Luxembourg'
    WHEN 'LVA' THEN 'Latvia'
    WHEN 'MAC' THEN 'Macao'
    WHEN 'MAR' THEN 'Morocco'
    WHEN 'MDA' THEN 'Moldova'
    WHEN 'MDG' THEN 'Madagascar'
    WHEN 'MEX' THEN 'Mexico'
    WHEN 'MKD' THEN 'North Macedonia'
    WHEN 'MLT' THEN 'Malta'
    WHEN 'MMR' THEN 'Myanmar'
    WHEN 'MNE' THEN 'Montenegro'
    WHEN 'MNG' THEN 'Mongolia'
    WHEN 'MWI' THEN 'Malawi'
    WHEN 'MYS' THEN 'Malaysia'
    WHEN 'NER' THEN 'Niger'
    WHEN 'NGA' THEN 'Nigeria'
    WHEN 'NIC' THEN 'Nicaragua'
    WHEN 'NLD' THEN 'Netherlands'
    WHEN 'NOR' THEN 'Norway'
    WHEN 'NPL' THEN 'Nepal'
    WHEN 'NZL' THEN 'New Zealand'
    WHEN 'OMN' THEN 'Oman'
    WHEN 'PAN' THEN 'Panama'
    WHEN 'PER' THEN 'Peru'
    WHEN 'PHL' THEN 'Philippines'
    WHEN 'POL' THEN 'Poland'
    WHEN 'PRT' THEN 'Portugal'
    WHEN 'PRY' THEN 'Paraguay'
    WHEN 'PSE' THEN 'Palestine'
    WHEN 'QAT' THEN 'Qatar'
    WHEN 'ROU' THEN 'Romania'
    WHEN 'RUS' THEN 'Russia'
    WHEN 'SAU' THEN 'Saudi Arabia'
    WHEN 'SEN' THEN 'Senegal'
    WHEN 'SGP' THEN 'Singapore'
    WHEN 'SLE' THEN 'Sierra Leone'
    WHEN 'SLV' THEN 'El Salvador'
    WHEN 'SRB' THEN 'Serbia'
    WHEN 'STP' THEN 'São Tomé and Principe'
    WHEN 'SUR' THEN 'Suriname'
    WHEN 'SVK' THEN 'Slovakia'
    WHEN 'SVN' THEN 'Slovenia'
    WHEN 'SWE' THEN 'Sweden'
    WHEN 'TCA' THEN 'Turks and Caicos Is.'
    WHEN 'TCD' THEN 'Chad'
    WHEN 'TGO' THEN 'Togo'
    WHEN 'THA' THEN 'Thailand'
    WHEN 'TON' THEN 'Tonga'
    WHEN 'TTO' THEN 'Trinidad and Tobago'
    WHEN 'TUN' THEN 'Tunisia'
    WHEN 'TUR' THEN 'Turkey'
    WHEN 'TUV' THEN 'Tuvalu'
    WHEN 'UKR' THEN 'Ukraine'
    WHEN 'URY' THEN 'Uruguay'
    WHEN 'USA' THEN 'United States of America'
    WHEN 'UZB' THEN 'Uzbekistan'
    WHEN 'VNM' THEN 'Vietnam'
    WHEN 'WSM' THEN 'Samoa'
    WHEN 'ZAF' THEN 'South Africa'
    ELSE NULL
END;

SELECT DISTINCT magnitude  FROM school_lang;

ALTER TABLE home_lang
DROP COLUMN qualifier,
DROP COLUMN magnitude;

SELECT * FROM school_lang;

SELECT COUNT(DISTINCT country_name) FROM school_lang;



SELECT * FROM school_lang;

ALTER TABLE school_lang
ADD COLUMN taught_in_home_lang DECIMAL(5,1),
ADD COLUMN taught_in_foreign DECIMAL(5,1);

UPDATE school_lang
SET
    taught_in_home_lang = ROUND(value, 1),
    taught_in_foreign = ROUND(100 - value, 1);
    
UPDATE school_lang
SET indicatorId = CASE indicatorId
    WHEN 'FHLANGILP.G2T3' THEN 'early grades'
    WHEN 'FHLANGILP.PRIMARY' THEN 'end of prim'
    WHEN 'FHLANGILP.LOWERSEC' THEN 'lower sec'
    ELSE indicatorId
END;

DROP TABLE IF EXISTS school_language;

CREATE TABLE school_language AS
SELECT
    h.country_name AS country,
    h.indicatorId AS level,
    h.year,
    h.taught_in_home_lang AS taught_in_home_lang,
    h.taught_in_foreign AS taught_in_foreign
FROM school_lang h
JOIN (
    SELECT
        country_name,
        indicatorId,
        MAX(year) AS max_year
    FROM school_lang
    WHERE country_name IS NOT NULL
      AND indicatorId IS NOT NULL
    GROUP BY country_name, indicatorId
) latest
    ON h.country_name = latest.country_name
   AND h.indicatorId = latest.indicatorId
   AND h.year = latest.max_year;
   
SELECT * FROM school_language;

DROP TABLE IF EXISTS school_lang_geo;

CREATE TABLE school_lang_geo AS
SELECT s.*, n.geometry_wkt, n.name
FROM school_language s
LEFT JOIN naturalearth2 n
ON s.country = n.name
UNION ALL 
SELECT s.*, n.geometry_wkt, n.name
FROM school_language s
RIGHT JOIN naturalearth2 n
ON s.country = n.name;

SELECT country, `LEVEL`, max(year) 
from school_lang_geo
GROUP BY country, `level`
ORDER BY max(YEAR) asc;

SELECT DISTINCT geometry_wkt FROM school_lang_geo
WHERE country = 'Kazakhstan';

SELECT DISTINCT country
FROM school_language 
WHERE `level`  = 'early grades';  