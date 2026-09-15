-- Comparacion estratificada exploratoria: no controla todos los confundidores.
SELECT ContractLabel, SupportLabel, COUNT(*) AS Customers, SUM(ChurnFlag) AS Churned,
       1.0*SUM(ChurnFlag)/COUNT(*) AS ChurnRate
FROM customers WHERE InternetService <> 'No'
GROUP BY ContractLabel, SupportLabel ORDER BY MIN(ContractOrder), SupportLabel;
