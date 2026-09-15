-- Tasa observada en esta muestra, NO una serie temporal ni prediccion mensual.
SELECT COUNT(*) AS Customers, SUM(ChurnFlag) AS Churned,
       SUM(1-ChurnFlag) AS Active,
       1.0*SUM(ChurnFlag)/NULLIF(COUNT(*),0) AS ChurnRate,
       SUM(CASE WHEN ChurnFlag=1 THEN MonthlyChargesCents ELSE 0 END)/100.0 AS MonthlyChargesChurned,
       SUM(CASE WHEN ChurnFlag=0 THEN MonthlyChargesCents ELSE 0 END)/100.0 AS MonthlyChargesActive,
       AVG(MonthlyCharges) AS AverageMonthlyCharges,
       AVG(tenure) AS AverageTenure,
       SUM(TotalChargesMissing) AS MissingTotalCharges
FROM customers;
