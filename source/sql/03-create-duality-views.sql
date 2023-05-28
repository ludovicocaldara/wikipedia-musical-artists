create or replace json relational duality view band as
  artists @insert @update @delete
  {
    _id     : id
    name    : name
    type    : type
    details : details
    link    : link
    discovered : discovered
    genre   : artist_genres @insert @update @delete @nocheck
      [
        {
	  edge_id : id
          genres @noinsert @update @nodelete @nocheck @unnest
          {
            _id : id
            name : name
            link : link
          }
	}
      ]
    label   : artist_labels @insert @update @delete @nocheck
      [
        {
	  edge_id : id
          labels @insert @update @nodelete
          {
            _id : id
            name : name
            link : link
          }
	}
      ]
    current_members : band_members @insert @update @delete @nocheck
      [
        {
	  edge_id : id
          artists @insert @noupdate @nodelete
          {
            _id : id
            name : name
            link : link
          }
	}
      ]
    past_members : band_members @insert @update @delete @nocheck
      [
        {
	  edge_id : id
          artists @insert @noupdate @nodelete
          {
            _id : id
            name : name
            link : link
          }
	}
      ]
    spinoffs : band_spinoffs @insert @update @delete @nocheck
      [
        {
	  edge_id : id
          artists @insert @noupdate @nodelete
          {
            _id : id
            name : name
            link : link
          }
	}
      ]
    associated_acts : associated_acts @insert @update @delete @nocheck
      [
        {
	  edge_id : id
          artists @insert @noupdate @nodelete
          {
            _id : id
            name : name
            link : link
          }
	}
      ]
  };
    

declare
col soda_collection_t;
begin
    col := dbms_soda.create_dualv_collection('band', 'BAND');
end;
/
