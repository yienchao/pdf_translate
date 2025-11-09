-- Add email column to translations table
-- This stores the user's email directly in the table for easier querying

-- Add the email column
ALTER TABLE translations
ADD COLUMN IF NOT EXISTS user_email TEXT;

-- Populate existing rows with email from auth.users
UPDATE translations t
SET user_email = u.email
FROM auth.users u
WHERE t.user_id = u.id
  AND t.user_email IS NULL;

-- Create an index on email for faster searches
CREATE INDEX IF NOT EXISTS idx_translations_user_email ON translations(user_email);

-- Optional: Create a trigger to auto-populate email when inserting new rows
-- This ensures email is always set when a translation is created
CREATE OR REPLACE FUNCTION set_user_email()
RETURNS TRIGGER AS $$
BEGIN
    -- Get the email from auth.users and set it
    SELECT email INTO NEW.user_email
    FROM auth.users
    WHERE id = NEW.user_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger that runs before insert
DROP TRIGGER IF EXISTS trigger_set_user_email ON translations;
CREATE TRIGGER trigger_set_user_email
    BEFORE INSERT ON translations
    FOR EACH ROW
    EXECUTE FUNCTION set_user_email();
