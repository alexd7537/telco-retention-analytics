-- No se mezclan 'No' y 'No internet service'. Cada factor tiene su propio denominador.
WITH factors AS (
  SELECT 'Internet' AS Factor, InternetLabel AS Category, ChurnFlag, MonthlyChargesCents FROM customers
  UNION ALL SELECT 'Soporte (solo internet)', SupportLabel, ChurnFlag, MonthlyChargesCents FROM customers WHERE InternetService <> 'No'
  UNION ALL SELECT 'Seguridad (solo internet)', OnlineSecurity, ChurnFlag, MonthlyChargesCents FROM customers WHERE InternetService <> 'No'
  UNION ALL SELECT 'Metodo de pago', PaymentLabel, ChurnFlag, MonthlyChargesCents FROM customers
  UNION ALL SELECT 'Tipo de pago', PaymentType, ChurnFlag, MonthlyChargesCents FROM customers
  UNION ALL SELECT 'Factura digital', PaperlessBilling, ChurnFlag, MonthlyChargesCents FROM customers
  UNION ALL SELECT 'Servicios contratados', CAST(ServiceCount AS TEXT), ChurnFlag, MonthlyChargesCents FROM customers
)
SELECT Factor, Category, COUNT(*) AS Customers, SUM(ChurnFlag) AS Churned,
       1.0*SUM(ChurnFlag)/COUNT(*) AS ChurnRate,
       SUM(CASE WHEN ChurnFlag=1 THEN MonthlyChargesCents ELSE 0 END)/100.0 AS MonthlyChargesChurned
FROM factors GROUP BY Factor, Category ORDER BY Factor, ChurnRate DESC;
