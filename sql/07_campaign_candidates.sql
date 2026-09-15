-- Los umbrales exploratorios 100/50 se configuran en config/scenarios.json.
-- Solo clientes NO abandonados. No usa genero, edad, parejas o dependientes.
SELECT c.customerID, c.SegmentID, s.SegmentName, s.PriorityOrder,
       c.tenure, c.ContractLabel, c.InternetLabel, c.SupportLabel,
       c.PaymentLabel, c.MonthlyCharges, s.Action
FROM customers c JOIN segments s USING (SegmentID)
WHERE c.ChurnFlag = 0 AND s.PilotEligible = 1
ORDER BY s.PriorityOrder, c.customerID;
