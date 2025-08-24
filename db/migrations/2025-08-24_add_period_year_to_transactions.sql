/*
Migration: Add period_year to Transactions
Date: 2025-08-24
Purpose: Allow mapping a transaction date (e.g., 2024-12-30) to accounting period year 2025.
Safe and idempotent for SQL Server.
*/

-- 1) Add column if it doesn't exist
IF COL_LENGTH('dbo.Transactions', 'period_year') IS NULL
BEGIN
    ALTER TABLE dbo.Transactions ADD period_year INT NULL;
END
GO

-- 2) Create index if it doesn't exist
IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes i
    WHERE i.name = 'IX_Transactions_period_year'
      AND i.object_id = OBJECT_ID('dbo.Transactions')
)
BEGIN
    CREATE INDEX IX_Transactions_period_year ON dbo.Transactions(period_year);
END
GO

-- 3) Optional backfill example (commented out):
-- UPDATE dbo.Transactions
-- SET period_year = YEAR(transaction_date)
-- WHERE period_year IS NULL;
-- GO
