-- Active: 1774943208283@@127.0.0.1@3306@health_system
create database if not exists health_system;
use health_system;
create table if not exists user(
    email varchar(50) not null,
    pswd varchar(20) not null,
    user_type enum('usr','admin') not null default 'usr',
    user_state enum('active','ban') not null default 'active',
    gender enum('male','female') default null,
    age int unsigned default null,
    height decimal(5,2) unsigned default null,
    weight decimal(5,2) unsigned default null,
    fpg decimal(5,2) unsigned default null,
    ogtt decimal(5,2) unsigned default null,
    hba1c decimal(5,2) unsigned default null,
    primary key(email)
);
create table if not exists history(
    id int auto_increment,
    email varchar(50) not null,
    conversation_time timestamp not null,
    question varchar(500) not null,
    answer varchar(8192) not null,
    primary key(id),
    index index_email(email)
);
create table if not exists message(
    id int auto_increment,
    email varchar(50) not null,
    admin varchar(50) not null,
    send_time timestamp not null,
    content varchar(512) not null,
    is_read tinyint(1) unsigned not null default 0,
    primary key(id),
    index index_email(email)
);