drop table if exists alpha_alphas;
drop table if exists alpha;

create table if not exists alpha (
	id varchar2(30),
	name varchar2(255),
	constraint alpha_pk primary key (id)
);

create table if not exists alpha_alphas (
	id integer generated always as identity,
        alpha1_id varchar2(30),
        alpha2_id varchar2(30),
	constraint alpha_alphas_pk primary key (id),
	constraint alpha1_fk foreign key (alpha1_id) references alpha(id),
	constraint alpha2_fk foreign key (alpha2_id) references alpha(id)
);


create or replace trigger alpha_insert_trg before insert on alpha
for each row
begin
	if :new.id is null then
		:new.id := f_get_object_id();
	end if;
end;
/

-- create a basic grand-father - father - son
delete from alpha;
insert into alpha (id, name) values ('64733ea40a7246d67092d34e','father');
insert into alpha (id, name) values ('64733eb60a7246d67092d351','son');
insert into alpha (id, name) values ('64733ec30a7246d67092d354','grand-father');
insert into alpha_alphas (alpha1_id, alpha2_id) values ('64733ea40a7246d67092d34e','64733eb60a7246d67092d351');
insert into alpha_alphas (alpha1_id, alpha2_id) values ('64733ec30a7246d67092d354','64733ea40a7246d67092d34e');
commit;


-- I'd love to have something like
-- db.alpha.find('name':'grand-father')
-- { 'name': 'grand-father', 'children' : [ { 'name' : 'father'} ] }

create or replace json relational duality view alphas as
  select json {
    '_id'  : f.id,
    'name' : f.name,
    'children': [
      select json {
        'id' : edge.id,
        unnest (
          select json {
            'son_id' : son.id,
            'son_name' : son.name
          } from alpha son with noinsert update nodelete 
          where son.id = edge.alpha2_id
          )
	}
      from alpha_alphas edge with insert update nodelete
      where edge.alpha1_id = f.id 
    ]
  }
  from alpha f with insert update delete;

      
declare
col soda_collection_t;
begin
    col := dbms_soda.create_dualv_collection('alphas', 'ALPHAS');
end;
/
