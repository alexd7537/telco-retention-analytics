-- Contexto descriptivo; NO se usa para seleccionar ni excluir clientes del piloto.
WITH groups AS (
  SELECT 'Genero' AS Factor, gender AS Category, ChurnFlag FROM customers
  UNION ALL SELECT 'SeniorCitizen', CAST(SeniorCitizen AS TEXT), ChurnFlag FROM customers
  UNION ALL SELECT 'Pareja', Partner, ChurnFlag FROM customers
  UNION ALL SELECT 'Dependientes', Dependents, ChurnFlag FROM customers
)
SELECT Factor, Category, COUNT(*) AS Customers, SUM(ChurnFlag) AS Churned,
       1.0*SUM(ChurnFlag)/COUNT(*) AS ChurnRate
FROM groups GROUP BY Factor, Category ORDER BY Factor, Category;
