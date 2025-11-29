-- Add missing job_card_number column to maintenance_jobs table
ALTER TABLE maintenance_jobs ADD COLUMN job_card_number VARCHAR(50);

-- Update existing rows with default job card numbers
UPDATE maintenance_jobs SET job_card_number = 'JC-' || LPAD(id::text, 6, '0') WHERE job_card_number IS NULL;

-- Make the column NOT NULL after updating existing rows
ALTER TABLE maintenance_jobs ALTER COLUMN job_card_number SET NOT NULL;

-- Add unique constraint
ALTER TABLE maintenance_jobs ADD CONSTRAINT unique_job_card_number UNIQUE (job_card_number);