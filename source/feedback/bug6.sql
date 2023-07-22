set echo on
drop view if exists feedback6;
drop table if exists beta;

create table beta (
  id               varchar2(30) not null ,
  name             varchar2(255) not null unique,
  default_column   boolean default false,
  constraint beta_pk primary key(id)
);


create or replace json relational duality view feedback6 as
  beta @insert @update @delete
  {
    _id     : id
    name    : name
    default_column : default_column
  };
  

begin

  insert into feedback6 values ('
    {
       "_id" : "test",
       "name": "son"
    }
  ');


  update feedback6 set data = ' 
    {
       "_id" : "test",
       "name": "son"
    }
  ' where json_value(data, '$._id') = 'test';
  
end;
/

