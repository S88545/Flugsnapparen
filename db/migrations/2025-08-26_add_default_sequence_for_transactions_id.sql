/*
Migration: Ensure Transactions.id auto-generates via sequence default (if not IDENTITY)
Date: 2025-08-26
Purpose: Fix "Cannot insert the value NULL into column 'id'" on INSERT into dbo.Transactions when 'id' is not an IDENTITY column.
Safe and idempotent for SQL Server.
*/

-- Only proceed if 'id' is NOT an IDENTITY column
IF COLUMNPROPERTY(OBJECT_ID('dbo.Transactions'), 'id', 'IsIdentity') = 0
BEGIN
    -- 1) Create sequence if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM sys.sequences WHERE name = 'Transactions_id_seq' AND SCHEMA_NAME(schema_id) = 'dbo'
    )
    BEGIN
        EXEC('CREATE SEQUENCE dbo.Transactions_id_seq AS INT START WITH 1 INCREMENT BY 1 NO CACHE');
    END

    -- 2) Restart sequence to MAX(id)+1 (handles existing data)
    DECLARE @max_id INT = ISNULL((SELECT MAX(id) FROM dbo.Transactions), 0);
    DECLARE @restart_sql NVARCHAR(200) = N'ALTER SEQUENCE dbo.Transactions_id_seq RESTART WITH ' + CAST(@max_id + 1 AS NVARCHAR(20)) + N';';
    EXEC sp_executesql @restart_sql;

    -- 3) Add default constraint on Transactions.id if missing
    IF NOT EXISTS (
        SELECT 1
        FROM sys.default_constraints dc
        JOIN sys.columns c ON c.default_object_id = dc.object_id
        JOIN sys.objects o ON o.object_id = c.object_id
        WHERE o.name = 'Transactions' AND c.name = 'id'
    )
    BEGIN
        ALTER TABLE dbo.Transactions ADD CONSTRAINT DF_Transactions_id DEFAULT (NEXT VALUE FOR dbo.Transactions_id_seq) FOR id;
    END
END
GO
