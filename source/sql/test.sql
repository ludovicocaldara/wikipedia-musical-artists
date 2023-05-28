drop table if exists alpha_beta;
drop table if exists alpha;
drop table if exists beta;

create table if not exists alpha (
	id varchar2(30),
	name varchar2(255),
	constraint alpha_pk primary key (id)
);

create table if not exists beta (
	id varchar2(30),
	name varchar2(255),
	constraint beta_pk primary key (id)
);

create table if not exists alpha_beta (
	id integer generated always as identity,
        alpha_id varchar2(30),
        beta_id varchar2(30),
	constraint alpha_beta_pk primary key (id),
	constraint alpha_fk foreign key (alpha_id) references alpha(id),
	constraint beta_fk foreign key (beta_id) references beta(id)
);


create or replace trigger beta_insert_trg before insert on beta
for each row
begin
	insert into beta (id, name) values (nlv(:new.id,get_object_id()), :new.name);
end;
/

create or replace json relational duality view alphas as
  alpha @insert @update @delete
  {
    _id     : id
    name    : name
    betas   : alpha_beta @insert @update @delete @nocheck
      [
        {
	 id : id
         beta @noinsert @noupdate @nodelete @unnest @nocheck
          {
	   nested_beta_id : id
           name : name
          }
        }
      ]
};

create or replace json relational duality view betas as
  beta @insert @update @delete
  {
    _id     : id
    name    : name
    alphas   : alpha_beta @insert @update @delete
      [
        {
	id: id
        alpha @noinsert @noupdate @nodelete @unnest
        {
	  nested_alpha_id : id
          name : name
        }
        }
      ]
};


declare
col soda_collection_t;
begin
    col := dbms_soda.create_dualv_collection('alphas', 'ALPHAS');
end;
/

declare
col soda_collection_t;
begin
    col := dbms_soda.create_dualv_collection('betas', 'BETAS');
end;
/
