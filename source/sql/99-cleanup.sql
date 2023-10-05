ALTER SESSION SET recyclebin = OFF;

drop function if exists f_get_object_id;

declare
num number;
begin
  num:= dbms_soda.drop_collection ('genre');
  num:= dbms_soda.drop_collection ('label');
  num:= dbms_soda.drop_collection ('artist');
  num:= dbms_soda.drop_collection ('artist_short');
end;
/


drop view if exists artist;
drop view if exists artist_short;
drop view if exists genre;
drop view if exists label;
drop table if exists spinoffs;
drop table if exists associated_acts;
drop table if exists members;
drop table if exists artist_labels;
drop table if exists labels;
drop table if exists artist_genres;
drop table if exists genres;
drop table if exists artists;

drop domain if exists artist_type;

drop property graph band_graph;


purge recyclebin;
