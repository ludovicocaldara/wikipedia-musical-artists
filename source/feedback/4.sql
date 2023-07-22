set echo on

drop view if exists alphas;
drop table if exists alpha_alphas;
drop table if exists alpha;

create table alpha (
        id varchar2(30),
        name varchar2(255),
        constraint alpha_pk primary key (id)
);

create table alpha_alphas (
        id integer generated always as identity,
        alpha1_id varchar2(30),
        alpha2_id varchar2(30),
        constraint alpha_alphas_pk primary key (id),
        constraint alpha1_fk foreign key (alpha1_id) references alpha(id),
        constraint alpha2_fk foreign key (alpha2_id) references alpha(id)
);


create or replace json relational duality view alphas as
  alpha @insert @update @delete
  {
    _id     : id
    name    : name
    children   : alpha_alphas @insert @update @delete @link(to: "ALPHA1_ID")
      [
        {
         id : id
         alpha @noinsert @noupdate @nodelete @unnest @link(from: "ALPHA2_ID")
          {
           nested_alpha_id : id
           name : name
          }
        }
      ]
};

insert into alphas values (
'{
    _id: "64733ea40a7246d67092d34e",
    name: "father",
    children: [
	  { id: 23,
	    nested_alpha_id: "64733eb60a7246d67092d351",
		name: "son"
	  }
	 ]
}'
);


pause

create or replace json relational duality view alphas as
  alpha @insert @update @delete
  {
    _id     : id
    name    : name
    children   : alpha_alphas @insert @update @delete @link(to: "ALPHA1_ID")
      [
        {
         id : id
         alpha @insert @noupdate @nodelete @unnest @link(from: "ALPHA2_ID")
          {
           nested_alpha_id : id
           name : name
          }
        }
      ]
};
