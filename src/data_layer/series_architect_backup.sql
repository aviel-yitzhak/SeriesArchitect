--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

-- Started on 2026-02-08 10:01:40

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 224 (class 1259 OID 25513)
-- Name: genres; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.genres (
    genre_id integer NOT NULL,
    genre_name character varying(100) NOT NULL,
    main_category character varying(50) NOT NULL
);


ALTER TABLE public.genres OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 25533)
-- Name: keywords; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.keywords (
    keyword_id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.keywords OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 25355)
-- Name: personal_ratings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.personal_ratings (
    user_id integer NOT NULL,
    tmdb_id integer NOT NULL,
    rating integer DEFAULT 0,
    is_anchor boolean DEFAULT false,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT personal_ratings_rating_check CHECK ((rating = ANY (ARRAY['-1'::integer, 0, 1])))
);


ALTER TABLE public.personal_ratings OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 25389)
-- Name: recommendation_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recommendation_history (
    user_id integer NOT NULL,
    tmdb_id integer NOT NULL,
    status text,
    last_action_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT recommendation_history_status_check CHECK ((status = ANY (ARRAY['ignored'::text, 'watched'::text, 'pending'::text])))
);


ALTER TABLE public.recommendation_history OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 25420)
-- Name: series; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.series (
    tmdb_id integer NOT NULL,
    title_he character varying(255),
    overview text,
    popularity double precision,
    genre_ids text,
    poster_path character varying(255),
    original_language character varying(10),
    origin_country character varying(100),
    status character varying(50),
    adult boolean,
    first_air_date date,
    last_air_date date,
    number_of_seasons integer,
    number_of_episodes integer,
    content_rating character varying(10),
    title_en character varying(255)
);


ALTER TABLE public.series OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 25427)
-- Name: series_availability; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.series_availability (
    tmdb_id integer NOT NULL,
    provider_id integer NOT NULL,
    country_code character varying(2) DEFAULT 'IL'::character varying
);


ALTER TABLE public.series_availability OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 25518)
-- Name: series_genres; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.series_genres (
    tmdb_id integer NOT NULL,
    genre_id integer NOT NULL
);


ALTER TABLE public.series_genres OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 25538)
-- Name: series_keywords; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.series_keywords (
    tmdb_id integer NOT NULL,
    keyword_id integer NOT NULL
);


ALTER TABLE public.series_keywords OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 25348)
-- Name: streaming_providers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.streaming_providers (
    provider_id integer NOT NULL,
    provider_name text NOT NULL,
    logo_path text
);


ALTER TABLE public.streaming_providers OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 25332)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    username character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 25331)
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- TOC entry 4919 (class 0 OID 0)
-- Dependencies: 217
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- TOC entry 4731 (class 2604 OID 25335)
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- TOC entry 4755 (class 2606 OID 25517)
-- Name: genres genres_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_pkey PRIMARY KEY (genre_id);


--
-- TOC entry 4759 (class 2606 OID 25537)
-- Name: keywords keywords_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.keywords
    ADD CONSTRAINT keywords_pkey PRIMARY KEY (keyword_id);


--
-- TOC entry 4747 (class 2606 OID 25362)
-- Name: personal_ratings personal_ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personal_ratings
    ADD CONSTRAINT personal_ratings_pkey PRIMARY KEY (user_id, tmdb_id);


--
-- TOC entry 4749 (class 2606 OID 25397)
-- Name: recommendation_history recommendation_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recommendation_history
    ADD CONSTRAINT recommendation_history_pkey PRIMARY KEY (user_id, tmdb_id);


--
-- TOC entry 4753 (class 2606 OID 25432)
-- Name: series_availability series_availability_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.series_availability
    ADD CONSTRAINT series_availability_pkey PRIMARY KEY (tmdb_id, provider_id);


--
-- TOC entry 4757 (class 2606 OID 25522)
-- Name: series_genres series_genres_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.series_genres
    ADD CONSTRAINT series_genres_pkey PRIMARY KEY (tmdb_id, genre_id);


--
-- TOC entry 4761 (class 2606 OID 25542)
-- Name: series_keywords series_keywords_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.series_keywords
    ADD CONSTRAINT series_keywords_pkey PRIMARY KEY (tmdb_id, keyword_id);


--
-- TOC entry 4751 (class 2606 OID 25426)
-- Name: series series_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.series
    ADD CONSTRAINT series_pkey PRIMARY KEY (tmdb_id);


--
-- TOC entry 4745 (class 2606 OID 25354)
-- Name: streaming_providers streaming_providers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.streaming_providers
    ADD CONSTRAINT streaming_providers_pkey PRIMARY KEY (provider_id);


--
-- TOC entry 4741 (class 2606 OID 25338)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- TOC entry 4743 (class 2606 OID 25340)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 4762 (class 2606 OID 25398)
-- Name: recommendation_history recommendation_history_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recommendation_history
    ADD CONSTRAINT recommendation_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 4763 (class 2606 OID 25438)
-- Name: series_availability series_availability_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.series_availability
    ADD CONSTRAINT series_availability_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.streaming_providers(provider_id);


--
-- TOC entry 4764 (class 2606 OID 25433)
-- Name: series_availability series_availability_tmdb_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.series_availability
    ADD CONSTRAINT series_availability_tmdb_id_fkey FOREIGN KEY (tmdb_id) REFERENCES public.series(tmdb_id);


--
-- TOC entry 4765 (class 2606 OID 25528)
-- Name: series_genres series_genres_genre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.series_genres
    ADD CONSTRAINT series_genres_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.genres(genre_id) ON DELETE CASCADE;


--
-- TOC entry 4766 (class 2606 OID 25523)
-- Name: series_genres series_genres_tmdb_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.series_genres
    ADD CONSTRAINT series_genres_tmdb_id_fkey FOREIGN KEY (tmdb_id) REFERENCES public.series(tmdb_id) ON DELETE CASCADE;


--
-- TOC entry 4767 (class 2606 OID 25548)
-- Name: series_keywords series_keywords_keyword_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.series_keywords
    ADD CONSTRAINT series_keywords_keyword_id_fkey FOREIGN KEY (keyword_id) REFERENCES public.keywords(keyword_id) ON DELETE CASCADE;


--
-- TOC entry 4768 (class 2606 OID 25543)
-- Name: series_keywords series_keywords_tmdb_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.series_keywords
    ADD CONSTRAINT series_keywords_tmdb_id_fkey FOREIGN KEY (tmdb_id) REFERENCES public.series(tmdb_id) ON DELETE CASCADE;


-- Completed on 2026-02-08 10:01:41

--
-- PostgreSQL database dump complete
--

