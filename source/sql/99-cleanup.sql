ALTER SESSION SET recyclebin = OFF;

drop function if exists f_get_object_id;

declare
num number;
begin
  num:= dbms_soda.drop_collection ('GENRE');
  num:= dbms_soda.drop_collection ('LABEL');
  num:= dbms_soda.drop_collection ('ARTIST');
  num:= dbms_soda.drop_collection ('ARTIST_SHORT');
  num:= dbms_soda.drop_collection ('ARTIST_CRAWLING');
end;
/
commit;


drop view if exists recommendations;
drop view if exists artist;
drop view if exists artist_crawling;
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
drop table if exists artists_crawling;
drop table if exists artists;

drop domain if exists artist_background;

drop property graph band_graph;


purge recyclebin;
