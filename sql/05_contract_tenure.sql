SELECT ContractLabel, TenureBand, COUNT(*) AS Customers, SUM(ChurnFlag) AS Churned,
       1.0*SUM(ChurnFlag)/COUNT(*) AS ChurnRate,
       CASE WHEN COUNT(*) < 100 THEN 'Base pequena: lectura exploratoria' ELSE 'Base >= 100' END AS SampleNote
FROM customers GROUP BY ContractLabel, TenureBand
ORDER BY MIN(ContractOrder), MIN(TenureBandOrder);
