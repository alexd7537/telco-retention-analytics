-- Seis segmentos EXCLUYENTES: cada cliente cuenta exactamente una vez.
SELECT SegmentID, COUNT(*) AS Customers, SUM(ChurnFlag) AS Churned,
       SUM(1-ChurnFlag) AS Active,
       1.0*SUM(ChurnFlag)/COUNT(*) AS ChurnRate,
       SUM(CASE WHEN ChurnFlag=1 THEN MonthlyChargesCents ELSE 0 END)/100.0 AS MonthlyChargesChurned,
       SUM(CASE WHEN ChurnFlag=0 THEN MonthlyChargesCents ELSE 0 END)/100.0 AS MonthlyChargesActive,
       1.0*SUM(CASE WHEN ChurnFlag=0 THEN MonthlyChargesCents ELSE 0 END)/NULLIF(SUM(1-ChurnFlag),0)/100 AS AvgMonthlyChargesActive
FROM customers GROUP BY SegmentID ORDER BY SegmentID;
