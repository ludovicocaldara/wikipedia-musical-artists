set echo on
drop view if exists person;
drop table if exists part_art;

create table part_art (
  id               varchar2(30) not null ,
  name             varchar2(255) not null unique,
  type             varchar2(30) not null,
  constraint part_art_pk primary key(id)
)
 partition by list (type)
(
     partition group_or_band VALUES ('group_or_band'),
     partition person        VALUES ('person')
);


create or replace json relational duality view person as
  part_art:person @insert @update @delete
  {
    _id     : id
    name    : name
    type    : type
  };
