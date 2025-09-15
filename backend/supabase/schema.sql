-- 由 snapshot_to_sql.py 自动生成
-- 来源: supabase/schema_snapshot.json
SET client_min_messages TO WARNING;
SET search_path TO public;

CREATE TABLE IF NOT EXISTS conversation_participants (
    id integer NOT NULL DEFAULT nextval('conversation_participants_id_seq'::regclass),
    conversation_id integer NOT NULL,
    user_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT conversation_participants_pkey PRIMARY KEY (id),
    CONSTRAINT conversation_participants_uniq_0 UNIQUE (conversation_id, user_id),
    CONSTRAINT conversation_participants_fk_0_conversation_id FOREIGN KEY (conversation_id) REFERENCES conversations (id),
    CONSTRAINT conversation_participants_fk_1_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS conversations (
    id integer NOT NULL DEFAULT nextval('conversations_id_seq'::regclass),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    last_message_id integer,
    CONSTRAINT conversations_pkey PRIMARY KEY (id),
    CONSTRAINT conversations_fk_0_last_message_id FOREIGN KEY (last_message_id) REFERENCES messages (id)
);

CREATE TABLE IF NOT EXISTS forum_likes (
    id integer NOT NULL DEFAULT nextval('forum_likes_id_seq'::regclass),
    user_id integer NOT NULL,
    post_id integer,
    reply_id integer,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT forum_likes_pkey PRIMARY KEY (id),
    CONSTRAINT forum_likes_uniq_0 UNIQUE (user_id, post_id, user_id, reply_id),
    CONSTRAINT forum_likes_fk_0_post_id FOREIGN KEY (post_id) REFERENCES forum_posts (id),
    CONSTRAINT forum_likes_fk_1_reply_id FOREIGN KEY (reply_id) REFERENCES forum_replies (id),
    CONSTRAINT forum_likes_fk_2_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS forum_posts (
    id integer NOT NULL DEFAULT nextval('forum_posts_id_seq'::regclass),
    title character varying NOT NULL,
    content text NOT NULL,
    author_id integer NOT NULL,
    category character varying NOT NULL,
    tags ARRAY DEFAULT '{}'::text[],
    replies_count integer DEFAULT 0,
    likes_count integer DEFAULT 0,
    views_count integer DEFAULT 0,
    is_pinned boolean DEFAULT false,
    is_hot boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    last_activity timestamp with time zone DEFAULT now(),
    is_anonymous boolean DEFAULT false,
    CONSTRAINT forum_posts_pkey PRIMARY KEY (id),
    CONSTRAINT forum_posts_fk_0_author_id FOREIGN KEY (author_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS forum_replies (
    id integer NOT NULL DEFAULT nextval('forum_replies_id_seq'::regclass),
    post_id integer NOT NULL,
    content text NOT NULL,
    author_id integer NOT NULL,
    parent_id integer,
    likes_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    parent_reply_id integer,
    CONSTRAINT forum_replies_pkey PRIMARY KEY (id),
    CONSTRAINT forum_replies_fk_0_author_id FOREIGN KEY (author_id) REFERENCES users (id),
    CONSTRAINT forum_replies_fk_1_parent_id FOREIGN KEY (parent_id) REFERENCES forum_replies (id),
    CONSTRAINT forum_replies_fk_2_parent_reply_id FOREIGN KEY (parent_reply_id) REFERENCES forum_replies (id),
    CONSTRAINT forum_replies_fk_3_post_id FOREIGN KEY (post_id) REFERENCES forum_posts (id)
);

CREATE TABLE IF NOT EXISTS forum_reply_likes (
    id integer NOT NULL DEFAULT nextval('forum_reply_likes_id_seq'::regclass),
    reply_id integer NOT NULL,
    user_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT forum_reply_likes_pkey PRIMARY KEY (id),
    CONSTRAINT forum_reply_likes_uniq_0 UNIQUE (reply_id, user_id),
    CONSTRAINT forum_reply_likes_fk_0_reply_id FOREIGN KEY (reply_id) REFERENCES forum_replies (id),
    CONSTRAINT forum_reply_likes_fk_1_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS friends (
    id integer NOT NULL DEFAULT nextval('friends_id_seq'::regclass),
    user_id integer,
    friend_id integer,
    status character varying DEFAULT 'pending'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT friends_pkey PRIMARY KEY (id),
    CONSTRAINT friends_uniq_0 UNIQUE (user_id, friend_id),
    CONSTRAINT friends_fk_0_friend_id FOREIGN KEY (friend_id) REFERENCES users (id),
    CONSTRAINT friends_fk_1_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS mentor_matches (
    id integer NOT NULL DEFAULT nextval('mentor_matches_id_seq'::regclass),
    mentor_id integer,
    mentee_id integer,
    skill_id integer,
    learning_need_id integer,
    mentor_skill_id integer,
    match_score numeric,
    match_algorithm character varying DEFAULT 'v1.0'::character varying,
    match_factors jsonb,
    status character varying DEFAULT 'suggested'::character varying,
    mentor_viewed_at timestamp without time zone,
    mentee_viewed_at timestamp without time zone,
    mentor_responded_at timestamp without time zone,
    mentee_responded_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp without time zone DEFAULT (CURRENT_TIMESTAMP + '7 days'::interval),
    CONSTRAINT mentor_matches_pkey PRIMARY KEY (id),
    CONSTRAINT mentor_matches_fk_0_learning_need_id FOREIGN KEY (learning_need_id) REFERENCES user_learning_needs (id),
    CONSTRAINT mentor_matches_fk_1_mentee_id FOREIGN KEY (mentee_id) REFERENCES users (id),
    CONSTRAINT mentor_matches_fk_2_mentor_id FOREIGN KEY (mentor_id) REFERENCES users (id),
    CONSTRAINT mentor_matches_fk_3_mentor_skill_id FOREIGN KEY (mentor_skill_id) REFERENCES user_skills (id),
    CONSTRAINT mentor_matches_fk_4_skill_id FOREIGN KEY (skill_id) REFERENCES skills (id)
);

CREATE TABLE IF NOT EXISTS mentorship_relationships (
    id integer NOT NULL DEFAULT nextval('mentorship_relationships_id_seq'::regclass),
    mentor_id integer,
    mentee_id integer,
    skill_id integer,
    match_id integer,
    title character varying NOT NULL,
    description text,
    learning_goals text,
    success_criteria text,
    start_date date DEFAULT CURRENT_DATE,
    estimated_end_date date,
    total_sessions_planned integer,
    session_duration_minutes integer DEFAULT 60,
    hourly_rate numeric,
    currency character varying DEFAULT 'CNY'::character varying,
    total_amount numeric,
    payment_schedule character varying DEFAULT 'per_session'::character varying,
    relationship_type character varying DEFAULT 'paid'::character varying,
    preferred_communication character varying,
    meeting_frequency character varying,
    timezone character varying,
    status character varying DEFAULT 'pending'::character varying,
    cancellation_reason text,
    sessions_completed integer DEFAULT 0,
    total_hours_spent numeric DEFAULT 0,
    last_session_at timestamp without time zone,
    next_session_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp without time zone,
    CONSTRAINT mentorship_relationships_pkey PRIMARY KEY (id),
    CONSTRAINT mentorship_relationships_fk_0_match_id FOREIGN KEY (match_id) REFERENCES mentor_matches (id),
    CONSTRAINT mentorship_relationships_fk_1_mentee_id FOREIGN KEY (mentee_id) REFERENCES users (id),
    CONSTRAINT mentorship_relationships_fk_2_mentor_id FOREIGN KEY (mentor_id) REFERENCES users (id),
    CONSTRAINT mentorship_relationships_fk_3_skill_id FOREIGN KEY (skill_id) REFERENCES skills (id)
);

CREATE TABLE IF NOT EXISTS mentorship_reviews (
    id integer NOT NULL DEFAULT nextval('mentorship_reviews_id_seq'::regclass),
    relationship_id integer,
    reviewer_id integer,
    reviewee_id integer,
    reviewer_role character varying NOT NULL,
    overall_rating integer NOT NULL,
    communication_rating integer,
    expertise_rating integer,
    timeliness_rating integer,
    value_rating integer,
    professionalism_rating integer,
    comment text,
    pros text,
    areas_for_improvement text,
    would_recommend boolean DEFAULT true,
    would_work_again boolean DEFAULT true,
    positive_tags ARRAY,
    negative_tags ARRAY,
    learning_objectives_met integer,
    skill_improvement integer,
    is_public boolean DEFAULT true,
    is_verified boolean DEFAULT false,
    verification_notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT mentorship_reviews_pkey PRIMARY KEY (id),
    CONSTRAINT mentorship_reviews_fk_0_relationship_id FOREIGN KEY (relationship_id) REFERENCES mentorship_relationships (id),
    CONSTRAINT mentorship_reviews_fk_1_reviewee_id FOREIGN KEY (reviewee_id) REFERENCES users (id),
    CONSTRAINT mentorship_reviews_fk_2_reviewer_id FOREIGN KEY (reviewer_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS mentorship_sessions (
    id integer NOT NULL DEFAULT nextval('mentorship_sessions_id_seq'::regclass),
    relationship_id integer,
    session_number integer NOT NULL,
    scheduled_at timestamp without time zone NOT NULL,
    actual_start_at timestamp without time zone,
    actual_end_at timestamp without time zone,
    duration_minutes integer,
    agenda text,
    mentor_notes text,
    mentee_notes text,
    key_topics ARRAY,
    homework_assigned text,
    resources_shared ARRAY,
    next_session_plan text,
    status character varying DEFAULT 'scheduled'::character varying,
    cancellation_reason text,
    rescheduled_from timestamp without time zone,
    mentor_satisfaction integer,
    mentee_satisfaction integer,
    mentor_feedback text,
    mentee_feedback text,
    progress_percentage integer DEFAULT 0,
    milestones_achieved ARRAY,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT mentorship_sessions_pkey PRIMARY KEY (id),
    CONSTRAINT mentorship_sessions_fk_0_relationship_id FOREIGN KEY (relationship_id) REFERENCES mentorship_relationships (id)
);

CREATE TABLE IF NOT EXISTS mentorship_transactions (
    id integer NOT NULL DEFAULT nextval('mentorship_transactions_id_seq'::regclass),
    relationship_id integer,
    session_id integer,
    transaction_type character varying NOT NULL,
    amount numeric NOT NULL,
    currency character varying DEFAULT 'CNY'::character varying,
    payment_method character varying,
    payment_status character varying DEFAULT 'pending'::character varying,
    external_transaction_id character varying,
    payment_gateway character varying,
    gateway_response jsonb,
    platform_fee_rate numeric DEFAULT 0.05,
    platform_fee_amount numeric DEFAULT 0,
    mentor_amount numeric,
    description text,
    reference_number character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    processed_at timestamp without time zone,
    confirmed_at timestamp without time zone,
    CONSTRAINT mentorship_transactions_pkey PRIMARY KEY (id),
    CONSTRAINT mentorship_transactions_uniq_0 UNIQUE (reference_number),
    CONSTRAINT mentorship_transactions_fk_0_relationship_id FOREIGN KEY (relationship_id) REFERENCES mentorship_relationships (id),
    CONSTRAINT mentorship_transactions_fk_1_session_id FOREIGN KEY (session_id) REFERENCES mentorship_sessions (id)
);

CREATE TABLE IF NOT EXISTS messages (
    id integer NOT NULL DEFAULT nextval('messages_id_seq'::regclass),
    sender_id integer,
    recipient_id integer,
    content text NOT NULL,
    message_type character varying DEFAULT 'text'::character varying,
    is_read boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    conversation_id character varying NOT NULL DEFAULT (gen_random_uuid())::character varying(50),
    status character varying DEFAULT 'sent'::character varying,
    read_at timestamp with time zone,
    CONSTRAINT messages_pkey PRIMARY KEY (id),
    CONSTRAINT messages_fk_0_recipient_id FOREIGN KEY (recipient_id) REFERENCES users (id),
    CONSTRAINT messages_fk_1_sender_id FOREIGN KEY (sender_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS orders (
    id integer NOT NULL DEFAULT nextval('orders_id_seq'::regclass),
    service_id integer,
    client_id integer,
    navigator_id integer,
    status character varying DEFAULT 'pending'::character varying,
    scheduled_at timestamp without time zone,
    total_price numeric,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT orders_pkey PRIMARY KEY (id),
    CONSTRAINT orders_fk_0_client_id FOREIGN KEY (client_id) REFERENCES users (id),
    CONSTRAINT orders_fk_1_navigator_id FOREIGN KEY (navigator_id) REFERENCES users (id),
    CONSTRAINT orders_fk_2_service_id FOREIGN KEY (service_id) REFERENCES services (id)
);

CREATE TABLE IF NOT EXISTS profiles (
    id integer NOT NULL DEFAULT nextval('profiles_id_seq'::regclass),
    user_id integer,
    full_name character varying,
    avatar_url text,
    bio text,
    phone character varying,
    location character varying,
    website character varying,
    birth_date date,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT profiles_pkey PRIMARY KEY (id),
    CONSTRAINT profiles_uniq_0 UNIQUE (user_id),
    CONSTRAINT profiles_fk_0_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id integer NOT NULL DEFAULT nextval('reviews_id_seq'::regclass),
    order_id integer,
    reviewer_id integer,
    rating integer,
    comment text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT reviews_pkey PRIMARY KEY (id),
    CONSTRAINT reviews_fk_0_order_id FOREIGN KEY (order_id) REFERENCES orders (id),
    CONSTRAINT reviews_fk_1_reviewer_id FOREIGN KEY (reviewer_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS services (
    id integer NOT NULL DEFAULT nextval('services_id_seq'::regclass),
    navigator_id integer,
    title character varying NOT NULL,
    description text,
    category character varying,
    price numeric,
    duration_hours integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT services_pkey PRIMARY KEY (id),
    CONSTRAINT services_fk_0_navigator_id FOREIGN KEY (navigator_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS skill_categories (
    id integer NOT NULL DEFAULT nextval('skill_categories_id_seq'::regclass),
    name character varying NOT NULL,
    name_en character varying,
    description text,
    icon_url character varying,
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT skill_categories_pkey PRIMARY KEY (id),
    CONSTRAINT skill_categories_uniq_0 UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS skills (
    id integer NOT NULL DEFAULT nextval('skills_id_seq'::regclass),
    category_id integer,
    name character varying NOT NULL,
    name_en character varying,
    description text,
    difficulty_level integer DEFAULT 1,
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT skills_pkey PRIMARY KEY (id),
    CONSTRAINT skills_fk_0_category_id FOREIGN KEY (category_id) REFERENCES skill_categories (id)
);

CREATE TABLE IF NOT EXISTS uploaded_files (
    id integer NOT NULL DEFAULT nextval('uploaded_files_id_seq'::regclass),
    file_id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id integer NOT NULL,
    filename character varying NOT NULL,
    original_filename character varying NOT NULL,
    file_path character varying NOT NULL,
    file_url character varying NOT NULL,
    file_size integer NOT NULL,
    content_type character varying NOT NULL,
    file_type character varying NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT uploaded_files_pkey PRIMARY KEY (id),
    CONSTRAINT uploaded_files_uniq_0 UNIQUE (file_id),
    CONSTRAINT uploaded_files_fk_0_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS user_availability (
    id integer NOT NULL DEFAULT nextval('user_availability_id_seq'::regclass),
    user_id integer,
    day_of_week integer NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    timezone character varying DEFAULT 'Asia/Shanghai'::character varying,
    availability_type character varying DEFAULT 'mentoring'::character varying,
    is_active boolean DEFAULT true,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_availability_pkey PRIMARY KEY (id),
    CONSTRAINT user_availability_fk_0_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS user_credit_logs (
    id integer NOT NULL DEFAULT nextval('user_credit_logs_id_seq'::regclass),
    user_id integer,
    credit_type character varying NOT NULL,
    amount integer NOT NULL,
    balance_after integer NOT NULL,
    reason character varying NOT NULL,
    reference_id integer,
    reference_type character varying,
    description text,
    expires_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_credit_logs_pkey PRIMARY KEY (id),
    CONSTRAINT user_credit_logs_fk_0_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS user_learning_needs (
    id integer NOT NULL DEFAULT nextval('user_learning_needs_id_seq'::regclass),
    user_id integer,
    skill_id integer,
    urgency_level integer DEFAULT 1,
    budget_min numeric,
    budget_max numeric,
    currency character varying DEFAULT 'CNY'::character varying,
    preferred_format character varying DEFAULT 'online'::character varying,
    preferred_duration character varying,
    description text,
    learning_goals text,
    current_level integer DEFAULT 1,
    target_level integer DEFAULT 2,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp without time zone DEFAULT (CURRENT_TIMESTAMP + '3 mons'::interval),
    CONSTRAINT user_learning_needs_pkey PRIMARY KEY (id),
    CONSTRAINT user_learning_needs_uniq_0 UNIQUE (user_id, skill_id),
    CONSTRAINT user_learning_needs_fk_0_skill_id FOREIGN KEY (skill_id) REFERENCES skills (id),
    CONSTRAINT user_learning_needs_fk_1_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS user_reputation_stats (
    id integer NOT NULL DEFAULT nextval('user_reputation_stats_id_seq'::regclass),
    user_id integer,
    mentor_rating_avg numeric DEFAULT 0,
    mentor_rating_count integer DEFAULT 0,
    mentor_relationships_total integer DEFAULT 0,
    mentor_relationships_completed integer DEFAULT 0,
    mentor_sessions_completed integer DEFAULT 0,
    mentor_hours_taught numeric DEFAULT 0,
    mentor_success_rate numeric DEFAULT 0,
    mentor_response_rate numeric DEFAULT 0,
    mentor_punctuality_rate numeric DEFAULT 0,
    mentee_rating_avg numeric DEFAULT 0,
    mentee_rating_count integer DEFAULT 0,
    mentee_relationships_total integer DEFAULT 0,
    mentee_relationships_completed integer DEFAULT 0,
    mentee_sessions_attended integer DEFAULT 0,
    mentee_hours_learned numeric DEFAULT 0,
    mentee_completion_rate numeric DEFAULT 0,
    mentee_attendance_rate numeric DEFAULT 0,
    reputation_score integer DEFAULT 0,
    trust_level character varying DEFAULT 'newcomer'::character varying,
    badges ARRAY,
    last_active_as_mentor timestamp without time zone,
    last_active_as_mentee timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_reputation_stats_pkey PRIMARY KEY (id),
    CONSTRAINT user_reputation_stats_uniq_0 UNIQUE (user_id),
    CONSTRAINT user_reputation_stats_fk_0_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS user_skills (
    id integer NOT NULL DEFAULT nextval('user_skills_id_seq'::regclass),
    user_id integer,
    skill_id integer,
    proficiency_level integer DEFAULT 1,
    years_experience integer DEFAULT 0,
    can_mentor boolean DEFAULT false,
    hourly_rate numeric,
    currency character varying DEFAULT 'CNY'::character varying,
    description text,
    verified boolean DEFAULT false,
    verified_at timestamp without time zone,
    verified_by integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_skills_pkey PRIMARY KEY (id),
    CONSTRAINT user_skills_uniq_0 UNIQUE (user_id, skill_id),
    CONSTRAINT user_skills_fk_0_skill_id FOREIGN KEY (skill_id) REFERENCES skills (id),
    CONSTRAINT user_skills_fk_1_user_id FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT user_skills_fk_2_verified_by FOREIGN KEY (verified_by) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS user_unavailable_periods (
    id integer NOT NULL DEFAULT nextval('user_unavailable_periods_id_seq'::regclass),
    user_id integer,
    start_date date NOT NULL,
    end_date date NOT NULL,
    start_time time without time zone,
    end_time time without time zone,
    reason character varying,
    description text,
    affects_mentoring boolean DEFAULT true,
    affects_learning boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_unavailable_periods_pkey PRIMARY KEY (id),
    CONSTRAINT user_unavailable_periods_fk_0_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS user_wallets (
    id integer NOT NULL DEFAULT nextval('user_wallets_id_seq'::regclass),
    user_id integer,
    balance numeric DEFAULT 0,
    frozen_balance numeric DEFAULT 0,
    currency character varying DEFAULT 'CNY'::character varying,
    mentor_points integer DEFAULT 0,
    learning_points integer DEFAULT 0,
    reputation_points integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_wallets_pkey PRIMARY KEY (id),
    CONSTRAINT user_wallets_uniq_0 UNIQUE (user_id),
    CONSTRAINT user_wallets_fk_0_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS users (
    id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
    username character varying NOT NULL,
    email character varying,
    password_hash character varying NOT NULL,
    role character varying DEFAULT 'user'::character varying,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    avatar_url character varying,
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_uniq_0 UNIQUE (username, email)
);

