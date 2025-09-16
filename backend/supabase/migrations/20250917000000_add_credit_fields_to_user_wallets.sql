-- Add credit fields to user_wallets table
-- Generated: 2025-09-17

-- Add credit fields to user_wallets table for AI agent usage tracking
ALTER TABLE user_wallets
ADD COLUMN IF NOT EXISTS mentor_points NUMERIC NOT NULL DEFAULT 0 CHECK (mentor_points >= 0),
ADD COLUMN IF NOT EXISTS learning_points NUMERIC NOT NULL DEFAULT 0 CHECK (learning_points >= 0),
ADD COLUMN IF NOT EXISTS reputation_points NUMERIC NOT NULL DEFAULT 0 CHECK (reputation_points >= 0);

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_user_wallets_user_id ON user_wallets(user_id);

-- Add comment to the table
COMMENT ON TABLE user_wallets IS 'User wallets for storing various types of credits and balances';
COMMENT ON COLUMN user_wallets.balance IS 'General wallet balance for transactions';
COMMENT ON COLUMN user_wallets.mentor_points IS 'Points earned from mentoring activities';
COMMENT ON COLUMN user_wallets.learning_points IS 'Points for learning activities and AI usage';
COMMENT ON COLUMN user_wallets.reputation_points IS 'Points based on user reputation and contributions';
