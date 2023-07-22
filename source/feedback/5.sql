set echo on

insert into artist_short values ('{"_id":"' || f_get_object_id() || '", "link": "The Mighty Mighty Bosstones", "name": "The Mighty Mighty Bosstones"}');

select * from artists where name='The Mighty Mighty Bosstones';

rollback;

pause

insert into artist values ('{"_id":"' || f_get_object_id() || '", "link": "The Mighty Mighty Bosstones", "name": "The Mighty Mighty Bosstones"}');

select * from artists where name='The Mighty Mighty Bosstones';

rollback;
