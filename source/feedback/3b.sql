create or replace json relational duality view feedback3 as
  artists @insert @update @delete
  {
    _id     : id
    name    : name
    link    : link
    discovered : discovered
    error   : error
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
            error   : error
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
            error   : error
          }
        }
      ]
  };
