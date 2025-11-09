-- Update the user_translation_stats view to include email
-- Run this in Supabase SQL Editor to add user_email column

DROP VIEW IF EXISTS user_translation_stats;

CREATE OR REPLACE VIEW user_translation_stats AS
SELECT
    t.user_id,
    u.email as user_email,
    COUNT(*) as total_translations,
    SUM(t.total_tokens) as total_tokens_used,
    SUM(t.cost_total_usd) as total_cost_usd,
    MAX(t.created_at) as last_translation_at
FROM translations t
LEFT JOIN auth.users u ON t.user_id = u.id
WHERE t.status = 'completed'
GROUP BY t.user_id, u.email;

-- Grant access to the view
GRANT SELECT ON user_translation_stats TO authenticated;

-- RLS for the view
ALTER VIEW user_translation_stats SET (security_invoker = true);
