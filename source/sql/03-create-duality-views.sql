create or replace json relational duality view artist as
  artists @insert @update @delete 
  {
    _id     : id
    name    : name
    link    : link
    discovered : discovered
    member_of : members @insert @update @delete @link(to: "MEMBER_ID") 
      [
        {
	  belonging_band_id : id
          artists @noinsert @update @nodelete @unnest @link(from: "BAND_ID") 
          {
            id : id
            name : name
            link : link
            discovered : discovered
          }
	}
      ]
    members : members @insert @update @delete @link(to: "BAND_ID") 
      [
        {
	  members_id : id
          artists @noinsert @update @nodelete @unnest @link(from: "MEMBER_ID") 
          {
            id : id
            name : name
            link : link
            discovered : discovered
          }
	}
      ]
  };


create or replace json relational duality view artist_short as
  artists @insert @update @delete
  {
    _id     : id
    name    : name
    link    : link
    discovered : discovered
  };


declare
col soda_collection_t;
begin
    col := dbms_soda.create_dualv_collection('artist', 'ARTIST');
    col := dbms_soda.create_dualv_collection('artist_short', 'ARTIST_SHORT');
end;
/

