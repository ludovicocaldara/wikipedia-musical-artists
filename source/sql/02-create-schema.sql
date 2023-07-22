exec ords.enable_schema;
commit;


create or replace function f_get_object_id return varchar2 is
begin
    return ltrim(to_char(mod(floor(
                (to_date(to_char(sys_extract_utc(systimestamp), 'YYYY-MM-DD"T"HH24:MI:SS'),'YYYY-MM-DD"T"HH24:MI:SS') - to_date('1970-01-01','YYYY-MM-DD'))*24*60*60
            ),power(2,32)),'xxxxxxxx'),' ') || lower(substr(rawtohex(sys_guid()),32-5) || substr(rawtohex(sys_guid()),13,4) || substr(rawtohex(sys_guid()),7,6) );
end;
/


drop table if exists spinoffs;
drop table if exists associated_acts;
drop table if exists members;
drop table if exists artist_labels;
drop table if exists labels;
drop table if exists artist_genres;
drop table if exists genres;
drop table if exists artists;

drop domain if exists artist_type;

create domain artist_type as varchar2(15) 
  constraint artist_type_chk check (artist_type in ('person','group_or_band'))
  order      artist_type;

create table artists (
  id               varchar2(30) not null ,
  name             varchar2(255) not null unique,
  link             varchar2(255),
  type             domain artist_type not null,
  discovered       boolean default false,
  error            varchar2(30),
  constraint artists_pk primary key(id)
);


/*
create or replace trigger artist_insert_trg before insert on artists for each row
begin
  if :new.id is null then
    :new.id := f_get_object_id();
  end if;
end;
/
*/

create table members (
  id               integer generated by default on null as identity,
  band_id          varchar2(30) not null,
  member_id        varchar2(30) not null,
  constraint members_band_fk foreign key (band_id) references artists(id),
  constraint members_member_fk foreign key (member_id) references artists(id),
  constraint members_pk primary key(id)
);


-- we don't consider anything below this comment for the simplest version

create table genres (
  id               varchar2(30) not null ,
  name             varchar2(255) not null unique,
  constraint genres_pk primary key(id)
);


create table artist_genres (
  id               integer generated by default on null as identity,
  genre_id         varchar2(30) not null ,
  artist_id        varchar2(30) not null ,
  constraint artist_genres_artists_fk foreign key (artist_id) references artists(id),
  constraint artist_genres_genres_fk foreign key (genre_id) references genres(id),
  constraint artist_genres_pk primary key(id)
);


create table labels (
  id               varchar2(30) not null ,
  name             varchar2(255) not null unique,
  constraint labels_pk primary key(id)
);

create table artist_labels (
  id               integer generated by default on null as identity,
  label_id         varchar2(30) not null ,
  artist_id        varchar2(30) not null ,
  constraint artist_labels_artists_fk foreign key (artist_id) references artists(id),
  constraint artist_labels_labels_fk foreign key (label_id) references labels(id),
  constraint artist_labels_pk primary key(id)
);


create table associated_acts (
  id               integer generated by default on null as identity,
  artist1_id         varchar2(30) not null,
  artist2_id         varchar2(30) not null,
  constraint associated_acts_artist1_fk foreign key (artist1_id) references artists(id),
  constraint associated_acts_artist2_fk foreign key (artist2_id) references artists(id),
  constraint associated_acts_pk primary key(id)
);


create table spinoffs (
  id               integer generated by default on null as identity,
  band_id          varchar2(30) not null,
  spinoff_id       varchar2(30) not null,
  constraint spinoffs_band_fk foreign key (band_id) references artists(id),
  constraint spinoffs_spinoff_fk foreign key (spinoff_id) references artists(id),
  constraint spinoffs_pk primary key(id)
);
