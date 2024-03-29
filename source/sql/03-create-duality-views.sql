create or replace json relational duality view artist as
  artists @insert @update @delete 
  {
    _id     : id
    name    : name
    link    : link
    type    : type
    extras  : extras
    discovered : discovered
    error   : error
    member_of : members @insert @update @delete @link(to: ["MEMBER_ID"]) 
      [
        {
          belonging_band_id : id
          artists @noinsert @update @nodelete @unnest @link(from: ["BAND_ID"]) 
          {
            id : id
            name : name
            link : link
            type : type
            extras  : extras
            discovered : discovered
            error   : error
          }
        }
      ]
    members : members @insert @update @delete @link(to: ["BAND_ID"]) 
      [
        {
          members_id : id
          artists @noinsert @update @nodelete @unnest @link(from: ["MEMBER_ID"]) 
          {
            id : id
            name : name
            link : link
            type : type
            extras  : extras
            discovered : discovered
            error   : error
          }
        }
      ]
    spinoff_of : spinoffs @insert @update @delete @link(to: ["SPINOFF_ID"])
      [
        {
          spinoff_of_id : id
          artists @noinsert @update @nodelete @unnest @link(from: ["BAND_ID"])
          {
            id : id
            name : name
            link : link
            type : type
            extras  : extras
            discovered : discovered
            error   : error
          }
        }
      ]
    spinoffs : spinoffs @insert @update @delete @link(to: ["BAND_ID"])
      [
        {
          spinoffs_id : id
          artists @noinsert @update @nodelete @unnest @link(from: ["SPINOFF_ID"])
          {
            id : id
            name : name
            link : link
            type : type
            extras  : extras
            discovered : discovered
            error   : error
          }
        }
      ]
    genre   : artist_genres @insert @update @delete
      [
        {
          artist_genres_id : id
          genres @noinsert @update @nodelete @unnest
          {
            id : id
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
            id : id
            name : name
          }
        }
      ]
  };


create or replace json relational duality view artist_short as
  artists @insert @update @delete @nocheck
  {
    _id     : id
    name    : name
    link    : link
    type    : type
    extras  : extras
    discovered : discovered
    error   : error
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

declare
col soda_collection_t;
begin
    col := dbms_soda.create_dualv_collection('artist', 'ARTIST');
    col := dbms_soda.create_dualv_collection('artist_short', 'ARTIST_SHORT');
    col := dbms_soda.create_dualv_collection('genre', 'GENRE');
    col := dbms_soda.create_dualv_collection('label', 'LABEL');
end;
/
