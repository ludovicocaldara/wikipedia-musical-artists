create or replace json relational duality view band as
  artists @insert @update @delete
  {
    _id     : id
    name    : name
    link    : link
    type    : type
    details : details
    discovered : discovered
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
    current_members : band_members @insert @update @delete @link(to: "BAND_ID")
      [
        {
	  current_members_id : id
          artists @noinsert @update @nodelete @unnest @link(from: "MEMBER_ID")
          {
            id : id
            name : name
            link : link
            type    : type
            details : details
            discovered : discovered
          }
	}
      ]
    past_members : band_members @insert @update @delete @link(to: "BAND_ID")
      [
        {
	  past_members_id : id
          artists @noinsert @update @nodelete @unnest @link(from: "MEMBER_ID")
          {
            id : id
            name : name
            link : link
            type    : type
            details : details
            discovered : discovered
          }
	}
      ]
    spinoffs : band_spinoffs @insert @update @delete @link(to: "BAND_ID")
      [
        {
	  band_spinoffs_id : id
          artists @noinsert @update @nodelete @unnest @link(from: "SPINOFF_ID")
          {
            id : id
            name : name
            link : link
            type    : type
            details : details
            discovered : discovered
          }
	}
      ]
    associated_acts : associated_acts @insert @update @delete @link(to: "ARTIST1_ID")
      [
        {
	  associated_acts_id : id
          artists @noinsert @update @nodelete @unnest @link(from: "ARTIST2_ID")
          {
            id : id
            name : name
            link : link
            type    : type
            details : details
            discovered : discovered
          }
	}
      ]
  };
    

create or replace json relational duality view genre as
  genres @insert @update @delete
  {
    _id : id
    name : name
  };

create or replace json relational duality view label as
  labels @insert @update @delete
  {
    _id : id
    name : name
  };

declare
col soda_collection_t;
begin
    col := dbms_soda.create_dualv_collection('genre', 'GENRE');
    col := dbms_soda.create_dualv_collection('band', 'BAND');
    col := dbms_soda.create_dualv_collection('label', 'LABEL');
end;
/
