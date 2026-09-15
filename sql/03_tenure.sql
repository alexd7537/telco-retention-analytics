SELECT TenureBand, COUNT(*) AS Customers, SUM(ChurnFlag) AS Churned,
       1.0*SUM(ChurnFlag)/COUNT(*) AS ChurnRate,
       SUM(CASE WHEN ChurnFlag=1 THEN MonthlyChargesCents ELSE 0 END)/100.0 AS MonthlyChargesChurned
FROM customers GROUP BY TenureBand ORDER BY MIN(TenureBandOrder);
