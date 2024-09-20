--Database Queries

--create new database
create database GenAI_Books_Project;

--create extension to store vectors
create extension vector;

--create books table, id as primary key
create table books(
id SERIAL primary key,
title varchar(500),
author varchar(200),
genre varchar(200),
year_published numeric,
summary text
);

-- create reviews table with id as primary key and book_id as foreign key
create table reviews(
id SERIAL primary key,
book_id integer references books (id),
user_id numeric,
review_text text,
rating numeric
)

--create normalized table to store the summary embedding with book_id as foreign key.
--Its used to provide similar records based on user preference
 create table books_summary_embeddings(
   id SERIAL primary key,
   book_id integer references books (id),
   embedding vector(384)
   );