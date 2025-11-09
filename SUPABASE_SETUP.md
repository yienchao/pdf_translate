# Supabase Integration Setup Guide

## What We Built

Your PDF Translation app now has:
1. **User Authentication** - Login system via Supabase Auth
2. **Database Tracking** - All translations logged to PostgreSQL
3. **Translation History** - Users can view their past translations and costs
4. **Local Testing Mode** - Works without Supabase for local development

## Files Created

### 1. `schema.sql`
Database schema for tracking translations:
- `translations` table with token usage, costs, and metadata
- Row Level Security (RLS) policies for data privacy
- `user_translation_stats` view for aggregate statistics

### 2. `supabase_client.py`
Helper class for Supabase operations:
- `sign_in()` - User authentication
- `log_translation()` - Log translation jobs
- `get_user_translations()` - Retrieve history
- `get_user_stats()` - Get aggregate stats

### 3. `auth.py`
Streamlit authentication components:
- `require_auth()` - Require login (or allow local mode)
- `login_page()` - Login UI
- `display_user_info()` - User info sidebar

### 4. Updated `app.py`
Integrated authentication and database logging:
- Authentication check on app start
- Database logging after each translation
- New "History" tab showing past translations

## Setup Steps

### Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Create a new project
3. Wait for database to initialize

### Step 2: Run Database Migration

1. In Supabase dashboard, go to **SQL Editor**
2. Copy the contents of `schema.sql`
3. Paste and run the SQL to create tables and policies

### Step 3: Create Test User

1. Go to **Authentication** > **Users** in Supabase dashboard
2. Click "Add user" > "Create new user"
3. Enter email and password
4. Confirm the user (check "Auto Confirm User" or click confirm in email)

### Step 4: Get API Credentials

1. Go to **Project Settings** > **API**
2. Copy:
   - **Project URL** (looks like `https://xxxxx.supabase.co`)
   - **anon public** key (long string starting with `eyJ...`)

### Step 5: Set Environment Variables

On Render, add these environment variables:
```
ANTHROPIC_API_KEY=your-anthropic-api-key
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhb...your-anon-key
```

### Step 6: Test Locally (Optional)

To test authentication locally:
```bash
set ANTHROPIC_API_KEY=your-key
set SUPABASE_URL=https://xxxxx.supabase.co
set SUPABASE_KEY=eyJhb...your-anon-key
streamlit run app.py
```

To test WITHOUT Supabase (local mode):
```bash
set ANTHROPIC_API_KEY=your-key
streamlit run app.py
```
(App will work without login if SUPABASE_URL/KEY not set)

## How It Works

### Authentication Flow
1. User opens app
2. If Supabase configured → Show login page
3. If Supabase NOT configured → Allow access (local mode)
4. After login → Show main app with user info

### Translation Logging Flow
1. User uploads PDF and translates
2. After successful translation:
   - If user logged in → Log to database
   - If not logged in → Skip logging
3. User can view history in "History" tab

### Database Tables

#### `translations` table
```sql
- id (UUID, primary key)
- user_id (UUID, foreign key to auth.users)
- original_filename (text)
- translated_filename (text)
- file_size_bytes (integer)
- input_tokens (integer)
- output_tokens (integer)
- total_tokens (generated)
- cost_input_usd (generated)
- cost_output_usd (generated)
- cost_total_usd (generated)
- status (text: processing, completed, failed)
- error_message (text, nullable)
- created_at (timestamptz)
- completed_at (timestamptz, nullable)
```

#### `user_translation_stats` view
```sql
- user_id (UUID)
- total_translations (count)
- total_tokens_used (sum)
- total_cost_usd (sum)
- last_translation_at (max timestamp)
```

## Row Level Security (RLS)

All tables have RLS enabled. Users can only:
- View their own translations
- Insert their own translations
- Update their own translations
- Delete their own translations

This ensures data privacy and security.

## Costs

Claude Haiku 4.5 pricing:
- Input: $0.80 per 1M tokens
- Output: $4.00 per 1M tokens

Costs are automatically calculated and stored in the database.

## Next Steps

1. Create Supabase project
2. Run `schema.sql` migration
3. Create test user
4. Add environment variables to Render
5. Deploy to Render
6. Test login and translation
7. Check History tab to see logged translations

## Troubleshooting

### App shows login page but shouldn't
- Check that `SUPABASE_URL` and `SUPABASE_KEY` are set correctly
- Verify the Supabase project is active

### Login fails
- Verify user exists in Supabase Auth dashboard
- Check that user is confirmed (not pending)
- Verify credentials are correct

### History tab shows no data
- Confirm you completed a translation after logging in
- Check Supabase database for `translations` table
- Verify RLS policies are set up correctly

### Database errors
- Confirm `schema.sql` was run successfully
- Check Supabase logs for SQL errors
- Verify user_id matches auth.users table

## Local Testing Without Supabase

The app is designed to work both WITH and WITHOUT Supabase:

**With Supabase:**
- Requires login
- Logs all translations to database
- Shows history and statistics

**Without Supabase (Local Mode):**
- No login required
- Translations work normally
- No database logging
- History tab shows info message

This makes it easy to develop locally without setting up Supabase first.
