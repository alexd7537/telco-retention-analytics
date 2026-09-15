SELECT ChargeBand, ChurnLabel, COUNT(*) AS Customers,
       AVG(MonthlyCharges) AS AverageMonthlyCharges,
       MIN(MonthlyCharges) AS MinMonthlyCharges, MAX(MonthlyCharges) AS MaxMonthlyCharges
FROM customers GROUP BY ChargeBand, ChurnLabel
ORDER BY MIN(ChargeBandOrder), ChurnLabel;
