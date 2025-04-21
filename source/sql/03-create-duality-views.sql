create or replace json relational duality view artist as
  artists @insert @update @delete 
  {
    _id           : id
    name          : name
    link          : link
    background    : background
    extras        : extras
    member_of : members @insert @update @delete @link(to: ["MEMBER_ID"]) 
      [
        {
          belonging_band_id : id
          artists @noinsert @update @nodelete @unnest @link(from: ["BAND_ID"]) 
          {
            id         : id
            name       : name
            link       : link
            background : background
            extras     : extras
          }
        }
      ]
    members : members @insert @update @delete @link(to: ["BAND_ID"]) 
      [
        {
          members_id : id
          artists @noinsert @update @nodelete @unnest @link(from: ["MEMBER_ID"]) 
          {
            id         : id
            name       : name
            link       : link
            background : background
            extras     : extras
          }
        }
      ]
    spinoff_of : spinoffs @insert @update @delete @link(to: ["SPINOFF_ID"])
      [
        {
          spinoff_of_id : id
          artists @noinsert @update @nodelete @unnest @link(from: ["BAND_ID"])
          {
            id         : id
            name       : name
            link       : link
            background : background
            extras     : extras
          }
        }
      ]
    spinoffs : spinoffs @insert @update @delete @link(to: ["BAND_ID"])
      [
        {
          spinoffs_id : id
          artists @noinsert @update @nodelete @unnest @link(from: ["SPINOFF_ID"])
          {
            id         : id
            name       : name
            link       : link
            background : background
            extras     : extras
          }
        }
      ]
    genre   : artist_genres @insert @update @delete
      [
        {
          artist_genres_id : id
          genres @noinsert @update @nodelete @unnest
          {
            id   : id
            name : name
          }
        }
      ]
    label   : artist_labels @insert @update @delete
      [
        {
          artist_labels_id : id
          labels @noinsert @update @nodelete @unnest
          {
            id   : id
            name : name
          }
        }
      ]
    artists_crawling @insert @update @delete @unnest
      {
      id    : id
      discovered : discovered
      error : error
      }
  };


create or replace json relational duality view artist_short as
  artists @insert @update @delete @nocheck
  {
    _id           : id
    name          : name
    link          : link
    background    : background
    extras        : extras
  };

create or replace json relational duality view genre as
  genres @insert @update @delete @nocheck
  {
    _id     : id
    name    : name
  };

create or replace json relational duality view label as
  labels @insert @update @delete @nocheck
  {
    _id     : id
    name    : name
  };

create or replace json relational duality view artist_crawling as
  artists @noinsert @noupdate @nodelete
  {
    _id       : id
    name      : name
    link      : link
    artists_crawling @insert @update @nodelete @unnest
      {
      id    : id
      discovered : discovered
      error : error
      }
  };

declare
col soda_collection_t;
begin
    col := dbms_soda.create_dualv_collection('artist', 'ARTIST');
    col := dbms_soda.create_dualv_collection('artist_short', 'ARTIST_SHORT');
    col := dbms_soda.create_dualv_collection('genre', 'GENRE');
    col := dbms_soda.create_dualv_collection('label', 'LABEL');
    col := dbms_soda.create_dualv_collection('artist_crawling', 'ARTIST_CRAWLING');
end;
/

select * from table(DBMS_SODA.LIST_COLLECTION_NAMES ());
