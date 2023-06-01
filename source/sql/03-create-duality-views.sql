create or replace json relational duality view band_nopast as
  artists @insert @update @delete 
  {
    _id     : id
    name    : name
    link    : link
    type    : type
    details : details
    discovered : discovered
    genre   : artist_genres @insert @noupdate @delete @nocheck
      [
        {
	  artist_genres_id : id
          genres @noinsert @noupdate @nodelete @unnest @nocheck
          {
            id : id
            name : name
          }
	}
      ]
    label   : artist_labels @insert @noupdate @delete  @nocheck
      [
        {
	  artist_labels_id : id
          labels @noinsert @noupdate @nodelete @unnest  @nocheck
          {
            id : id
            name : name
          }
	}
      ]
    current_member_of : band_members @insert @noupdate @delete @link(to: "MEMBER_ID") 
      [
        {
	  current_member_id : id
          artists @noinsert @noupdate @nodelete @unnest @link(from: "BAND_ID") 
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
    current_members : band_members @insert @noupdate @delete @link(to: "BAND_ID") 
      [
        {
	  current_members_id : id
          artists @noinsert @noupdate @nodelete @unnest @link(from: "MEMBER_ID") 
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
    spinoff_of : band_spinoffs @insert @noupdate @delete @link(to: "SPINOFF_ID") 
      [
        {
	  band_spinoff_id : id
          artists @noinsert @noupdate @nodelete @unnest @link(from: "BAND_ID") 
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
    spinoffs : band_spinoffs @insert @noupdate @delete @link(to: "BAND_ID") 
      [
        {
	  band_spinoffs_id : id
          artists @noinsert @noupdate @nodelete @unnest @link(from: "SPINOFF_ID") 
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
    associated_acts : associated_acts @insert @noupdate @delete @link(to: "ARTIST1_ID") 
      [
        {
	  associated_acts_id : id
          artists @noinsert @noupdate @nodelete @unnest @link(from: "ARTIST2_ID") 
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
create or replace json relational duality view band as
  artists @insert @update @delete 
  {
    _id     : id
    name    : name
    link    : link
    type    : type
    details : details
    discovered : discovered
    genre   : artist_genres @insert @noupdate @delete @nocheck
      [
        {
	  artist_genres_id : id
          genres @noinsert @noupdate @nodelete @unnest @nocheck
          {
            id : id
            name : name
          }
	}
      ]
    label   : artist_labels @insert @noupdate @delete  @nocheck
      [
        {
	  artist_labels_id : id
          labels @noinsert @noupdate @nodelete @unnest  @nocheck
          {
            id : id
            name : name
          }
	}
      ]
    current_member_of : band_members @insert @noupdate @delete @link(to: "MEMBER_ID") 
      [
        {
	  current_member_id : id
          artists @noinsert @noupdate @nodelete @unnest @link(from: "BAND_ID") 
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
    past_member_of : band_members @insert @noupdate @delete @link(to: "MEMBER_ID") 
      [
        {
	  past_member_id : id
          artists @noinsert @noupdate @nodelete @unnest @link(from: "BAND_ID") 
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
    current_members : band_members @insert @noupdate @delete @link(to: "BAND_ID") 
      [
        {
	  current_members_id : id
          artists @noinsert @noupdate @nodelete @unnest @link(from: "MEMBER_ID") 
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
    past_members : band_members @insert @noupdate @delete @link(to: "BAND_ID") 
      [
        {
	  past_members_id : id
          artists @noinsert @noupdate @nodelete @unnest @link(from: "MEMBER_ID") 
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
    spinoff_of : band_spinoffs @insert @noupdate @delete @link(to: "SPINOFF_ID") 
      [
        {
	  band_spinoff_id : id
          artists @noinsert @noupdate @nodelete @unnest @link(from: "BAND_ID") 
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
    spinoffs : band_spinoffs @insert @noupdate @delete @link(to: "BAND_ID") 
      [
        {
	  band_spinoffs_id : id
          artists @noinsert @noupdate @nodelete @unnest @link(from: "SPINOFF_ID") 
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
    associated_acts : associated_acts @insert @noupdate @delete @link(to: "ARTIST1_ID") 
      [
        {
	  associated_acts_id : id
          artists @noinsert @noupdate @nodelete @unnest @link(from: "ARTIST2_ID") 
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



-- we use this to query the non-discovered artists and to get existing relations without details 
create or replace json relational duality view band_short as
  artists @noinsert @noupdate @nodelete
  {
    _id     : id
    name    : name
    link    : link
    type    : type
    details : details
    discovered : discovered
  };


declare
col soda_collection_t;
begin
    col := dbms_soda.create_dualv_collection('genre', 'GENRE');
    col := dbms_soda.create_dualv_collection('band', 'BAND');
    col := dbms_soda.create_dualv_collection('label', 'LABEL');
    col := dbms_soda.create_dualv_collection('band_short', 'BAND_SHORT');
end;
/

