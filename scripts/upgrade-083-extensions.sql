\set ON_ERROR_STOP on
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname='pg_search') THEN
        ALTER EXTENSION pg_search UPDATE;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname='vector') THEN
        ALTER EXTENSION vector UPDATE;
    END IF;
END $$;
SELECT extname,extversion FROM pg_extension WHERE extname IN ('pg_search','vector');
