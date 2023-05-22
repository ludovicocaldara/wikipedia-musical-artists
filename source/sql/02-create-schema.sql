connect bands/Bands##123@localhost:1521/FREEPDB1

exec ords.enable_schema;
commit;


create table artists (
  id               integer generated by default on null as identity,
  name             varchar2(255) not null unique,
  link             varchar2(255),
  type             varchar2(20),
  details          json,
  discovered       boolean default false,
  discover_time    integer not null,
  constraint artists_type_ck check (type in ('person','group_or_band')),
  constraint artists_pk primary key(id)
);


create table genres (
  id               integer generated by default on null as identity,
  name             varchar2(255) not null unique,
  constraint genres_pk primary key(id)
);


create table artist_genres (
  id               integer generated by default on null as identity,
  genre_id         integer ,
  artist_id        integer ,
  constraint artist_genres_artists_fk foreign key (artist_id) references artists(id),
  constraint artist_genres_genres_fk foreign key (genre_id) references genres(id),
  constraint artist_genres_pk primary key(id)
);


create table labels (
  id               integer generated by default on null as identity,
  name             varchar2(255) not null unique,
  constraint labels_pk primary key(id)
);

create table artist_labels (
  id               integer generated by default on null as identity,
  label_id         integer ,
  artist_id        integer ,
  constraint artist_labels_artists_fk foreign key (artist_id) references artists(id),
  constraint artist_labels_labels_fk foreign key (label_id) references labels(id),
  constraint artist_labels_pk primary key(id)
);


create table band_members (
  id               integer generated by default on null as identity,
  band_id          integer,
  member_id        integer,
  constraint band_members_band_fk foreign key (band_id) references artists(id),
  constraint band_members_member_fk foreign key (member_id) references artists(id),
  constraint band_members_pk primary key(id)
);

create table associated_acts (
  id               integer generated by default on null as identity,
  artist1_id         integer,
  artist2_id         integer,
  constraint associated_acts_artist1_fk foreign key (artist1_id) references artists(id),
  constraint associated_acts_artist2_fk foreign key (artist2_id) references artists(id),
  constraint associated_acts_pk primary key(id)
);


create table band_spinoffs (
  id               integer generated by default on null as identity,
  band_id          integer,
  spinoff_id       integer,
  constraint band_spinoffs_band_fk foreign key (band_id) references artists(id),
  constraint band_spinoffs_spinoff_fk foreign key (spinoff_id) references artists(id),
  constraint band_spinoffs_pk primary key(id)
);

