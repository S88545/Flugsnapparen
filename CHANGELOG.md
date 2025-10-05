# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- DB migration to ensure Transactions.id auto-generates when not IDENTITY: db/migrations/2025-08-26_add_default_sequence_for_transactions_id.sql
	- Creates dbo.Transactions_id_seq and DEFAULT constraint if missing.
	- Fixes "Cannot insert the value NULL into column 'id'" when inserting transactions.

## [0.7.0] - 2025-08-24
### Added
- Accounting period year (period_year) for Transactions, allowing a transaction date (e.g., 2024-12-30) to belong to accounting year 2025.
- Transaction add/edit forms updated to input period_year; defaults to selected value or the transaction date’s year.
- Transaction list: filter by period_year, year mode selector (period vs date), CSV export includes period_year.
- Reports (summary, KPI, Lgh/Medlem) now use accounting year by default via coalesce(period_year, year(transaction_date)).
- Prognosis: year lists and generation logic constrained by accounting year; hybrid generation respects period_year.
- Dashboard: current-year metrics and expense chart use accounting year.

### Migration
- db/migrations/2025-08-24_add_period_year_to_transactions.sql (idempotent): adds column + index. Optional backfill commented.

### Notes
- Existing data can be backfilled with period_year = YEAR(transaction_date) if desired.

