create or replace json relational duality view band as
  artists @insert @update @delete
  {
    _id     : id
    name    : name
    link    : link
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
    current_member_of : members @insert @update @delete @link(to: "MEMBER_ID")
      [
        {
	  current_member_id : id
          artists @noinsert @update @nodelete @unnest @link(from: "BAND_ID")
          {
            id : id
            name : name
            link : link
            discovered : discovered
          }
	}
      ]
    past_member_of : members @insert @update @delete @link(to: "MEMBER_ID")
      [
        {
	  past_member_id : id
          artists @noinsert @update @nodelete @unnest @link(from: "BAND_ID")
          {
            id : id
            name : name
            link : link
            discovered : discovered
          }
	}
      ]
    current_members : members @insert @update @delete @link(to: "BAND_ID")
      [
        {
	  current_members_id : id
          artists @noinsert @update @nodelete @unnest @link(from: "MEMBER_ID")
          {
            id : id
            name : name
            link : link
            discovered : discovered
          }
	}
      ]
    past_members : members @insert @update @delete @link(to: "BAND_ID")
      [
        {
	  past_members_id : id
          artists @noinsert @update @nodelete @unnest @link(from: "MEMBER_ID")
          {
            id : id
            name : name
            link : link
            discovered : discovered
          }
	}
      ]
    spinoff_of : spinoffs @insert @update @delete @link(to: "SPINOFF_ID")
      [
        {
	  band_spinoff_id : id
          artists @noinsert @update @nodelete @unnest @link(from: "BAND_ID")
          {
            id : id
            name : name
            link : link
            discovered : discovered
          }
	}
      ]
    spinoffs : spinoffs @insert @update @delete @link(to: "BAND_ID")
      [
        {
	  spinoffs_id : id
          artists @noinsert @update @nodelete @unnest @link(from: "SPINOFF_ID")
          {
            id : id
            name : name
            link : link
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
            discovered : discovered
          }
	}
      ]
  };
