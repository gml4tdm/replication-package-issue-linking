--
-- PostgreSQL database dump
--

-- Dumped from database version 17.1 (Debian 17.1-1.pgdg120+1)
-- Dumped by pg_dump version 17.1 (Debian 17.1-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: model_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.model_type AS ENUM (
    'classifier',
    'input-embedding'
);


ALTER TYPE public.model_type OWNER TO postgres;

--
-- Name: repo_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.repo_type AS ENUM (
    'jira'
);


ALTER TYPE public.repo_type OWNER TO postgres;

--
-- Name: tag_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tag_type AS ENUM (
    'author',
    'system',
    'custom'
);


ALTER TYPE public.tag_type OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: annotator_comment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.annotator_comment (
    id integer NOT NULL,
    issue_id integer NOT NULL,
    user_id integer NOT NULL,
    body text NOT NULL,
    timestamp_utc timestamp without time zone NOT NULL
);


ALTER TABLE public.annotator_comment OWNER TO postgres;

--
-- Name: annotator_comment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.annotator_comment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.annotator_comment_id_seq OWNER TO postgres;

--
-- Name: annotator_comment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.annotator_comment_id_seq OWNED BY public.annotator_comment.id;


--
-- Name: assigned_tag; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.assigned_tag (
    issue_id integer NOT NULL,
    tag_id integer NOT NULL
);


ALTER TABLE public.assigned_tag OWNER TO postgres;

--
-- Name: commit; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.commit (
    id integer NOT NULL,
    project_id integer NOT NULL,
    sha character varying(64) NOT NULL,
    sequence_number integer NOT NULL,
    timestamp_utc timestamp without time zone NOT NULL,
    message text NOT NULL,
    is_merge boolean NOT NULL,
    analysis_seq_nr integer NOT NULL
);


ALTER TABLE public.commit OWNER TO postgres;

--
-- Name: commit_file_modification; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.commit_file_modification (
    commit_id integer NOT NULL,
    action_type character varying(16) NOT NULL,
    old_path text,
    new_path text
);


ALTER TABLE public.commit_file_modification OWNER TO postgres;

--
-- Name: commit_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.commit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.commit_id_seq OWNER TO postgres;

--
-- Name: commit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.commit_id_seq OWNED BY public.commit.id;


--
-- Name: commit_issue_link_raw; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.commit_issue_link_raw (
    commit_id integer NOT NULL,
    issue_id integer NOT NULL
);


ALTER TABLE public.commit_issue_link_raw OWNER TO postgres;

--
-- Name: commit_issue_link_refined; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.commit_issue_link_refined (
    issue_id integer NOT NULL,
    commit_id integer NOT NULL,
    sequence_nr integer NOT NULL,
    diff_point integer
);


ALTER TABLE public.commit_issue_link_refined OWNER TO postgres;

--
-- Name: commit_parents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.commit_parents (
    commit_id integer NOT NULL,
    parent_id integer NOT NULL,
    is_main boolean NOT NULL
);


ALTER TABLE public.commit_parents OWNER TO postgres;

--
-- Name: issue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.issue (
    id integer NOT NULL,
    jira_id character varying(64) NOT NULL,
    key character varying(64) NOT NULL,
    project_id integer NOT NULL,
    summary text NOT NULL,
    description text NOT NULL,
    issue_type character varying(64),
    resolution character varying(64),
    date_resolved timestamp without time zone,
    date_created timestamp without time zone,
    date_updated timestamp without time zone,
    date_archived timestamp without time zone,
    status character varying(64),
    status_category_change_date timestamp without time zone,
    parent_id integer,
    priority character varying(64),
    environment text,
    watches integer,
    votes integer
);


ALTER TABLE public.issue OWNER TO postgres;

--
-- Name: issue_affected_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.issue_affected_versions (
    issue_id integer NOT NULL,
    version text NOT NULL,
    description text
);


ALTER TABLE public.issue_affected_versions OWNER TO postgres;

--
-- Name: issue_comment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.issue_comment (
    id integer NOT NULL,
    issue_id integer NOT NULL,
    sequence_number integer NOT NULL,
    date_created timestamp without time zone NOT NULL,
    date_updated timestamp without time zone NOT NULL,
    body text
);


ALTER TABLE public.issue_comment OWNER TO postgres;

--
-- Name: issue_comment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.issue_comment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.issue_comment_id_seq OWNER TO postgres;

--
-- Name: issue_comment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.issue_comment_id_seq OWNED BY public.issue_comment.id;


--
-- Name: issue_components; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.issue_components (
    issue_id integer NOT NULL,
    component text NOT NULL,
    description text
);


ALTER TABLE public.issue_components OWNER TO postgres;

--
-- Name: issue_fix_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.issue_fix_versions (
    issue_id integer NOT NULL,
    version text NOT NULL,
    description text
);


ALTER TABLE public.issue_fix_versions OWNER TO postgres;

--
-- Name: issue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.issue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.issue_id_seq OWNER TO postgres;

--
-- Name: issue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.issue_id_seq OWNED BY public.issue.id;


--
-- Name: issue_labels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.issue_labels (
    issue_id integer NOT NULL,
    label text NOT NULL
);


ALTER TABLE public.issue_labels OWNER TO postgres;

--
-- Name: issue_repo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.issue_repo (
    id integer NOT NULL,
    name text NOT NULL,
    url text,
    requires_authentication boolean NOT NULL,
    last_downloaded_utc timestamp without time zone,
    query_wait_time_in_minutes double precision NOT NULL,
    type public.repo_type NOT NULL
);


ALTER TABLE public.issue_repo OWNER TO postgres;

--
-- Name: issue_repo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.issue_repo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.issue_repo_id_seq OWNER TO postgres;

--
-- Name: issue_repo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.issue_repo_id_seq OWNED BY public.issue_repo.id;


--
-- Name: issue_subtask; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.issue_subtask (
    parent_issue integer NOT NULL,
    child_issue integer NOT NULL
);


ALTER TABLE public.issue_subtask OWNER TO postgres;

--
-- Name: issue_time_tracking; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.issue_time_tracking (
    tt_original_estimate_seconds bigint,
    tt_remaining_estimate text,
    tt_original_estimate text,
    tt_remaining_estimate_seconds bigint,
    tt_time_spent_seconds bigint,
    tt_time_spent text,
    aggregate_time_original_estimate bigint,
    aggregate_time_estimate bigint,
    time_original_estimate bigint,
    aggregate_time_spent bigint,
    time_estimate bigint,
    time_spent bigint,
    work_ratio bigint,
    issue_id integer NOT NULL
);


ALTER TABLE public.issue_time_tracking OWNER TO postgres;

--
-- Name: issue_to_issue_link; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.issue_to_issue_link (
    id integer NOT NULL,
    lhs_issue integer NOT NULL,
    rhs_issue integer NOT NULL,
    link_type character varying(64) NOT NULL,
    link_name_lhs_to_rhs character varying(64) NOT NULL,
    link_name_rhs_to_lhs character varying(64) NOT NULL
);


ALTER TABLE public.issue_to_issue_link OWNER TO postgres;

--
-- Name: issue_to_issue_link_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.issue_to_issue_link_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.issue_to_issue_link_id_seq OWNER TO postgres;

--
-- Name: issue_to_issue_link_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.issue_to_issue_link_id_seq OWNED BY public.issue_to_issue_link.id;


--
-- Name: label; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.label (
    issue_id integer NOT NULL,
    category_id integer NOT NULL,
    flag boolean NOT NULL
);


ALTER TABLE public.label OWNER TO postgres;

--
-- Name: label_category; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.label_category (
    id integer NOT NULL,
    name character varying(32) NOT NULL,
    description text NOT NULL
);


ALTER TABLE public.label_category OWNER TO postgres;

--
-- Name: label_category_constraint; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.label_category_constraint (
    category_id integer NOT NULL,
    mutually_exclusive_with_id integer NOT NULL
);


ALTER TABLE public.label_category_constraint OWNER TO postgres;

--
-- Name: label_category_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.label_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.label_category_id_seq OWNER TO postgres;

--
-- Name: label_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.label_category_id_seq OWNED BY public.label_category.id;


--
-- Name: model; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.model (
    id integer NOT NULL,
    name text NOT NULL,
    description text NOT NULL,
    type public.model_type NOT NULL
);


ALTER TABLE public.model OWNER TO postgres;

--
-- Name: model_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.model_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.model_id_seq OWNER TO postgres;

--
-- Name: model_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.model_id_seq OWNED BY public.model.id;


--
-- Name: permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permission (
    user_id integer NOT NULL,
    may_annotate boolean NOT NULL,
    may_edit_models boolean NOT NULL,
    may_create_accounts boolean NOT NULL,
    may_compute_predictions boolean NOT NULL,
    may_edit_tags boolean NOT NULL,
    may_import_issues boolean NOT NULL,
    may_edit_label_categories boolean NOT NULL,
    may_assign_tags boolean NOT NULL,
    may_edit_files boolean NOT NULL
);


ALTER TABLE public.permission OWNER TO postgres;

--
-- Name: prediction; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prediction (
    model_run_id integer NOT NULL,
    issue_id integer NOT NULL,
    category_id integer NOT NULL,
    confidence double precision,
    flag boolean NOT NULL
);


ALTER TABLE public.prediction OWNER TO postgres;

--
-- Name: project_category; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_category (
    repo_id integer NOT NULL,
    id integer NOT NULL,
    jira_id character varying(64) NOT NULL,
    description text NOT NULL,
    name character varying(64) NOT NULL
);


ALTER TABLE public.project_category OWNER TO postgres;

--
-- Name: projct_category_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.projct_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.projct_category_id_seq OWNER TO postgres;

--
-- Name: projct_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.projct_category_id_seq OWNED BY public.project_category.id;


--
-- Name: project; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project (
    id integer NOT NULL,
    repo_id integer NOT NULL,
    name text NOT NULL,
    key character varying(64) NOT NULL,
    project_type_key character varying(64),
    jira_id character varying(64),
    project_category_id integer
);


ALTER TABLE public.project OWNER TO postgres;

--
-- Name: project_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_id_seq OWNER TO postgres;

--
-- Name: project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_id_seq OWNED BY public.project.id;


--
-- Name: project_property; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_property (
    id integer NOT NULL,
    project_id integer NOT NULL,
    name text NOT NULL,
    value text NOT NULL
);


ALTER TABLE public.project_property OWNER TO postgres;

--
-- Name: project_property_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_property_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_property_id_seq OWNER TO postgres;

--
-- Name: project_property_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_property_id_seq OWNED BY public.project_property.id;


--
-- Name: repo_property; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.repo_property (
    id integer NOT NULL,
    repo_id integer NOT NULL,
    name text NOT NULL,
    value text NOT NULL
);


ALTER TABLE public.repo_property OWNER TO postgres;

--
-- Name: repo_property_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.repo_property_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.repo_property_id_seq OWNER TO postgres;

--
-- Name: repo_property_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.repo_property_id_seq OWNED BY public.repo_property.id;


--
-- Name: system_user_set; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_user_set (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    password_hash character varying(128) NOT NULL
);


ALTER TABLE public.system_user_set OWNER TO postgres;

--
-- Name: system_user_set_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_user_set_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_user_set_id_seq OWNER TO postgres;

--
-- Name: system_user_set_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_user_set_id_seq OWNED BY public.system_user_set.id;


--
-- Name: tag; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tag (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text NOT NULL,
    type public.tag_type NOT NULL
);


ALTER TABLE public.tag OWNER TO postgres;

--
-- Name: tag_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tag_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tag_id_seq OWNER TO postgres;

--
-- Name: tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tag_id_seq OWNED BY public.tag.id;


--
-- Name: training_run; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.training_run (
    id integer NOT NULL,
    model_id integer NOT NULL,
    timestamp_utc timestamp without time zone NOT NULL,
    description text NOT NULL
);


ALTER TABLE public.training_run OWNER TO postgres;

--
-- Name: training_run_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.training_run_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.training_run_id_seq OWNER TO postgres;

--
-- Name: training_run_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.training_run_id_seq OWNED BY public.training_run.id;


--
-- Name: user_label; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_label (
    issue_id integer NOT NULL,
    category_id integer NOT NULL,
    user_id integer NOT NULL,
    flag boolean NOT NULL
);


ALTER TABLE public.user_label OWNER TO postgres;

--
-- Name: annotator_comment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotator_comment ALTER COLUMN id SET DEFAULT nextval('public.annotator_comment_id_seq'::regclass);


--
-- Name: commit id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit ALTER COLUMN id SET DEFAULT nextval('public.commit_id_seq'::regclass);


--
-- Name: issue id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue ALTER COLUMN id SET DEFAULT nextval('public.issue_id_seq'::regclass);


--
-- Name: issue_comment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_comment ALTER COLUMN id SET DEFAULT nextval('public.issue_comment_id_seq'::regclass);


--
-- Name: issue_repo id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_repo ALTER COLUMN id SET DEFAULT nextval('public.issue_repo_id_seq'::regclass);


--
-- Name: issue_to_issue_link id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_to_issue_link ALTER COLUMN id SET DEFAULT nextval('public.issue_to_issue_link_id_seq'::regclass);


--
-- Name: label_category id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.label_category ALTER COLUMN id SET DEFAULT nextval('public.label_category_id_seq'::regclass);


--
-- Name: model id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model ALTER COLUMN id SET DEFAULT nextval('public.model_id_seq'::regclass);


--
-- Name: project id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project ALTER COLUMN id SET DEFAULT nextval('public.project_id_seq'::regclass);


--
-- Name: project_category id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_category ALTER COLUMN id SET DEFAULT nextval('public.projct_category_id_seq'::regclass);


--
-- Name: project_property id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_property ALTER COLUMN id SET DEFAULT nextval('public.project_property_id_seq'::regclass);


--
-- Name: repo_property id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repo_property ALTER COLUMN id SET DEFAULT nextval('public.repo_property_id_seq'::regclass);


--
-- Name: system_user_set id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_user_set ALTER COLUMN id SET DEFAULT nextval('public.system_user_set_id_seq'::regclass);


--
-- Name: tag id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tag ALTER COLUMN id SET DEFAULT nextval('public.tag_id_seq'::regclass);


--
-- Name: training_run id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.training_run ALTER COLUMN id SET DEFAULT nextval('public.training_run_id_seq'::regclass);


--
-- Name: annotator_comment annotator_comment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotator_comment
    ADD CONSTRAINT annotator_comment_pkey PRIMARY KEY (id);


--
-- Name: assigned_tag assigned_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assigned_tag
    ADD CONSTRAINT assigned_tag_pkey PRIMARY KEY (issue_id, tag_id);


--
-- Name: commit_issue_link_raw commit_issue_link_raw_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit_issue_link_raw
    ADD CONSTRAINT commit_issue_link_raw_pkey PRIMARY KEY (commit_id, issue_id);


--
-- Name: commit_issue_link_refined commit_issue_link_refined_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit_issue_link_refined
    ADD CONSTRAINT commit_issue_link_refined_pkey PRIMARY KEY (issue_id, commit_id);


--
-- Name: commit_parents commit_parents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit_parents
    ADD CONSTRAINT commit_parents_pkey PRIMARY KEY (commit_id, parent_id);


--
-- Name: commit commit_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit
    ADD CONSTRAINT commit_pkey PRIMARY KEY (id);


--
-- Name: issue_affected_versions issue_affected_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_affected_versions
    ADD CONSTRAINT issue_affected_versions_pkey PRIMARY KEY (issue_id, version);


--
-- Name: issue_comment issue_comment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_comment
    ADD CONSTRAINT issue_comment_pkey PRIMARY KEY (id);


--
-- Name: issue_components issue_components_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_components
    ADD CONSTRAINT issue_components_pkey PRIMARY KEY (issue_id, component);


--
-- Name: issue_fix_versions issue_fix_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_fix_versions
    ADD CONSTRAINT issue_fix_versions_pkey PRIMARY KEY (issue_id, version);


--
-- Name: issue_labels issue_labels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_labels
    ADD CONSTRAINT issue_labels_pkey PRIMARY KEY (issue_id, label);


--
-- Name: issue issue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue
    ADD CONSTRAINT issue_pkey PRIMARY KEY (id);


--
-- Name: issue_repo issue_repo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_repo
    ADD CONSTRAINT issue_repo_pkey PRIMARY KEY (id);


--
-- Name: issue_subtask issue_subtask_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_subtask
    ADD CONSTRAINT issue_subtask_pkey PRIMARY KEY (parent_issue, child_issue);


--
-- Name: issue_time_tracking issue_time_tracking_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_time_tracking
    ADD CONSTRAINT issue_time_tracking_pkey PRIMARY KEY (issue_id);


--
-- Name: issue_to_issue_link issue_to_issue_link_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_to_issue_link
    ADD CONSTRAINT issue_to_issue_link_pkey PRIMARY KEY (id);


--
-- Name: label_category_constraint label_category_constraint_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.label_category_constraint
    ADD CONSTRAINT label_category_constraint_pkey PRIMARY KEY (category_id, mutually_exclusive_with_id);


--
-- Name: label_category label_category_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.label_category
    ADD CONSTRAINT label_category_name_key UNIQUE (name);


--
-- Name: label_category label_category_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.label_category
    ADD CONSTRAINT label_category_pkey PRIMARY KEY (id);


--
-- Name: label label_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.label
    ADD CONSTRAINT label_pkey PRIMARY KEY (issue_id, category_id);


--
-- Name: model model_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model
    ADD CONSTRAINT model_pkey PRIMARY KEY (id);


--
-- Name: permission permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_pkey PRIMARY KEY (user_id);


--
-- Name: prediction prediction_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction
    ADD CONSTRAINT prediction_pkey PRIMARY KEY (model_run_id, issue_id, category_id);


--
-- Name: project_category projct_category_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_category
    ADD CONSTRAINT projct_category_pkey PRIMARY KEY (id);


--
-- Name: project project_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_pkey PRIMARY KEY (id);


--
-- Name: project_property project_property_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_property
    ADD CONSTRAINT project_property_pkey PRIMARY KEY (id);


--
-- Name: repo_property repo_property_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repo_property
    ADD CONSTRAINT repo_property_pkey PRIMARY KEY (id);


--
-- Name: system_user_set system_user_set_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_user_set
    ADD CONSTRAINT system_user_set_pkey PRIMARY KEY (id);


--
-- Name: system_user_set system_user_set_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_user_set
    ADD CONSTRAINT system_user_set_username_key UNIQUE (username);


--
-- Name: tag tag_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_name_key UNIQUE (name);


--
-- Name: tag tag_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_pkey PRIMARY KEY (id);


--
-- Name: training_run training_run_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.training_run
    ADD CONSTRAINT training_run_pkey PRIMARY KEY (id);


--
-- Name: user_label user_label_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_label
    ADD CONSTRAINT user_label_pkey PRIMARY KEY (issue_id, category_id, user_id);


--
-- Name: jira_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX jira_id_idx ON public.issue USING btree (jira_id);


--
-- Name: key_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX key_idx ON public.issue USING btree (key);


--
-- Name: label_category_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX label_category_name ON public.label_category USING btree (name);


--
-- Name: tag_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tag_name ON public.tag USING btree (name);


--
-- Name: annotator_comment annotator_comment_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotator_comment
    ADD CONSTRAINT annotator_comment_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: annotator_comment annotator_comment_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annotator_comment
    ADD CONSTRAINT annotator_comment_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.system_user_set(id) ON DELETE CASCADE;


--
-- Name: assigned_tag assigned_tag_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assigned_tag
    ADD CONSTRAINT assigned_tag_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: assigned_tag assigned_tag_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assigned_tag
    ADD CONSTRAINT assigned_tag_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tag(id) ON DELETE CASCADE;


--
-- Name: commit_file_modification commit_file_modification_commit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit_file_modification
    ADD CONSTRAINT commit_file_modification_commit_id_fkey FOREIGN KEY (commit_id) REFERENCES public.commit(id) ON DELETE CASCADE;


--
-- Name: commit_issue_link_raw commit_issue_link_raw_commit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit_issue_link_raw
    ADD CONSTRAINT commit_issue_link_raw_commit_id_fkey FOREIGN KEY (commit_id) REFERENCES public.commit(id) ON DELETE CASCADE;


--
-- Name: commit_issue_link_raw commit_issue_link_raw_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit_issue_link_raw
    ADD CONSTRAINT commit_issue_link_raw_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: commit_issue_link_refined commit_issue_link_refined_commit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit_issue_link_refined
    ADD CONSTRAINT commit_issue_link_refined_commit_id_fkey FOREIGN KEY (commit_id) REFERENCES public.commit(id) ON DELETE CASCADE;


--
-- Name: commit_issue_link_refined commit_issue_link_refined_diff_point_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit_issue_link_refined
    ADD CONSTRAINT commit_issue_link_refined_diff_point_fkey FOREIGN KEY (diff_point) REFERENCES public.commit(id) ON DELETE CASCADE;


--
-- Name: commit_issue_link_refined commit_issue_link_refined_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit_issue_link_refined
    ADD CONSTRAINT commit_issue_link_refined_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: commit_parents commit_parents_commit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit_parents
    ADD CONSTRAINT commit_parents_commit_id_fkey FOREIGN KEY (commit_id) REFERENCES public.commit(id) ON DELETE CASCADE;


--
-- Name: commit_parents commit_parents_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit_parents
    ADD CONSTRAINT commit_parents_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.commit(id) ON DELETE CASCADE;


--
-- Name: commit commit_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit
    ADD CONSTRAINT commit_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.project(id) ON DELETE CASCADE;


--
-- Name: issue_affected_versions issue_affected_versions_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_affected_versions
    ADD CONSTRAINT issue_affected_versions_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: issue_comment issue_comment_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_comment
    ADD CONSTRAINT issue_comment_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: issue_components issue_components_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_components
    ADD CONSTRAINT issue_components_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: issue_fix_versions issue_fix_versions_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_fix_versions
    ADD CONSTRAINT issue_fix_versions_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: issue_labels issue_labels_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_labels
    ADD CONSTRAINT issue_labels_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: issue issue_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue
    ADD CONSTRAINT issue_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: issue issue_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue
    ADD CONSTRAINT issue_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.project(id) ON DELETE CASCADE;


--
-- Name: issue_subtask issue_subtask_child_issue_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_subtask
    ADD CONSTRAINT issue_subtask_child_issue_fkey FOREIGN KEY (child_issue) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: issue_subtask issue_subtask_parent_issue_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_subtask
    ADD CONSTRAINT issue_subtask_parent_issue_fkey FOREIGN KEY (parent_issue) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: issue_time_tracking issue_time_tracking_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_time_tracking
    ADD CONSTRAINT issue_time_tracking_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: issue_to_issue_link issue_to_issue_link_lhs_issue_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_to_issue_link
    ADD CONSTRAINT issue_to_issue_link_lhs_issue_fkey FOREIGN KEY (lhs_issue) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: issue_to_issue_link issue_to_issue_link_rhs_issue_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue_to_issue_link
    ADD CONSTRAINT issue_to_issue_link_rhs_issue_fkey FOREIGN KEY (rhs_issue) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: label_category_constraint label_category_constraint_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.label_category_constraint
    ADD CONSTRAINT label_category_constraint_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.label_category(id) ON DELETE CASCADE;


--
-- Name: label_category_constraint label_category_constraint_mutually_exclusive_with_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.label_category_constraint
    ADD CONSTRAINT label_category_constraint_mutually_exclusive_with_id_fkey FOREIGN KEY (mutually_exclusive_with_id) REFERENCES public.label_category(id) ON DELETE CASCADE;


--
-- Name: label label_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.label
    ADD CONSTRAINT label_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.label_category(id) ON DELETE CASCADE;


--
-- Name: label label_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.label
    ADD CONSTRAINT label_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: permission permission_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.system_user_set(id) ON DELETE CASCADE;


--
-- Name: prediction prediction_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction
    ADD CONSTRAINT prediction_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.label_category(id) ON DELETE CASCADE;


--
-- Name: prediction prediction_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction
    ADD CONSTRAINT prediction_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: prediction prediction_model_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction
    ADD CONSTRAINT prediction_model_run_id_fkey FOREIGN KEY (model_run_id) REFERENCES public.training_run(id) ON DELETE CASCADE;


--
-- Name: project_category projct_category_repo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_category
    ADD CONSTRAINT projct_category_repo_id_fkey FOREIGN KEY (repo_id) REFERENCES public.issue_repo(id) ON DELETE CASCADE;


--
-- Name: project project_project_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_project_category_id_fkey FOREIGN KEY (project_category_id) REFERENCES public.project_category(id) ON DELETE CASCADE;


--
-- Name: project_property project_property_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_property
    ADD CONSTRAINT project_property_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.project(id) ON DELETE CASCADE;


--
-- Name: project project_repo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_repo_id_fkey FOREIGN KEY (repo_id) REFERENCES public.issue_repo(id) ON DELETE CASCADE;


--
-- Name: repo_property repo_property_repo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repo_property
    ADD CONSTRAINT repo_property_repo_id_fkey FOREIGN KEY (repo_id) REFERENCES public.issue_repo(id) ON DELETE CASCADE;


--
-- Name: training_run training_run_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.training_run
    ADD CONSTRAINT training_run_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.model(id) ON DELETE CASCADE;


--
-- Name: user_label user_label_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_label
    ADD CONSTRAINT user_label_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.label_category(id) ON DELETE CASCADE;


--
-- Name: user_label user_label_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_label
    ADD CONSTRAINT user_label_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES public.issue(id) ON DELETE CASCADE;


--
-- Name: user_label user_label_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_label
    ADD CONSTRAINT user_label_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.system_user_set(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

