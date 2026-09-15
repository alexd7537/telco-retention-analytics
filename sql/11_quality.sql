SELECT 'Duplicados de ID' AS CheckName, COUNT(*) - COUNT(DISTINCT customerID) AS Observed FROM customers
UNION ALL SELECT 'TotalCharges nulo', SUM(TotalChargesMissing) FROM customers
UNION ALL SELECT 'TotalCharges nulo con tenure distinto de 0', COUNT(*) FROM customers WHERE TotalCharges IS NULL AND tenure <> 0
UNION ALL SELECT 'Cargos mensuales negativos', COUNT(*) FROM customers WHERE MonthlyCharges < 0
UNION ALL SELECT 'Tenure cero', COUNT(*) FROM customers WHERE tenure = 0;
