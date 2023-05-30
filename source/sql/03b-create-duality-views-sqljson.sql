-- to finish, not done!
create or replace json relational duality view band as
  select json {
    '_id'        : band.id,
    'name'       : band.name,
    'type'       : band.type,
    'details'    : band.details,
    'link'       : band.link,
    'discovered' : band.discovered,
    'genre' : [
      select json {
        'artist_genres_id' : artist_genres.id,
        unnest (
	  select json {
	    'id'   : genres.id,
	    'name' : genres.name
	  }
	  from genres with noinsert update nodelete nocheck
	  where genres.id = artist_genres.genre_id
	)
      }
      from artist_genres with insert update delete nocheck
      where artist_genres.artist_id = band.id
    ],
    'label' : [
      select json {
        'artist_labels_id' : artist_labels.id,
        unnest (
	  select json {
	    'id'   : labels.id,
	    'name' : labels.name
	  }
	  from labels with noinsert update nodelete nocheck
	  where labels.id = artist_labels.label_id
	)
      }
      from artist_labels with insert update delete nocheck
      where artist_labels.artist_id = band.id
    ],
    'band_members' : [
      select json {
        'band_member_id' : band_members.id,
        unnest (
	  select json {
	    'id'   : member.id,
	    'name' : member.name
	  }
	  from artists member with noinsert update nodelete nocheck
	  where member.id = band_members.member_id
	)
      }
      from band_members with insert update delete nocheck
      where band_members.band_id = band.id
    ]
  }
  from artists band with insert update delete;

