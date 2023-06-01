drop table if exists edge;
drop table if exists node;

create table if not exists node (
	id varchar2(30),
	name varchar2(255),
	constraint node_pk primary key (id)
);

create table if not exists edge (
	id integer generated always as identity,
        node1_id varchar2(30),
        node2_id varchar2(30),
	constraint edge_pk primary key (id),
	constraint node1_fk foreign key (node1_id) references node(id),
	constraint node2_fk foreign key (node2_id) references node(id)
);


create or replace trigger node_insert_trg before insert on node
for each row
begin
	if :new.id is null then
		:new.id := f_get_object_id();
	end if;
end;
/

-- create a basic grand-father - father - son
delete from node;
insert into node (id, name) values ('64733ec30a7246d67092d354','grand-father');
insert into node (id, name) values ('64733ea40a7246d67092d34e','father');
insert into node (id, name) values ('64733eb60a7246d67092d351','son');
insert into edge (node1_id, node2_id) values ('64733ec30a7246d67092d354','64733ea40a7246d67092d34e');
insert into edge (node1_id, node2_id) values ('64733ea40a7246d67092d34e','64733eb60a7246d67092d351');
commit;

create or replace json relational duality view nodes as
  node @insert @update @delete
  {
    _id     : id
    name    : name
    children   : edge @insert @update @delete @link(to: "NODE1_ID")
      [
        {
         id : id
         node @noinsert @noupdate @nodelete @unnest @link(from: "NODE2_ID")
          {
           child_node_id : id
           name : name
          }
        }
      ]
    father   : edge @insert @update @delete @link(to: "NODE2_ID")
      [
        {
         id : id
         node @noinsert @noupdate @nodelete @unnest @link(from: "NODE1_ID")
          {
           parent : id
           name : name
          }
        }
      ]
};
      
declare
col soda_collection_t;
begin
    col := dbms_soda.create_dualv_collection('nodes', 'NODES');
end;
/
