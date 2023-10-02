DROP PROPERTY GRAPH BAND_GRAPH;
CREATE PROPERTY GRAPH BAND_GRAPH
    VERTEX TABLES (
        ARTISTS
        KEY (ID)
        PROPERTIES (ID, Name, Link, Discovered)
    )
    EDGE TABLES (
        MEMBERS
         KEY (ID)
         SOURCE KEY (band_id) REFERENCES ARTISTS(ID)
         DESTINATION KEY (member_id) REFERENCES ARTISTS(ID)
         LABEL member
         PROPERTIES (band_id, member_id),
        SPINOFFS
         KEY (ID)
         SOURCE KEY (band_id) REFERENCES ARTISTS(ID)
         DESTINATION KEY (spinoff_id) REFERENCES ARTISTS(ID)
         LABEL spinoff
         PROPERTIES (band_id, spinoff_id)
    )
;



-- top bands by number of members:
SELECT name, COUNT(1) AS num_members
       FROM graph_table ( BAND_GRAPH
        MATCH (src) - [IS MEMBERS] -> (dst)
        COLUMNS ( src.id AS id , src.name as name)
    ) GROUP BY  id, name ORDER BY num_members DESC
    FETCH FIRST 10 ROWS ONLY

col src_name for a30
col dest_name for a30

-- which artists are/were members of Kyuss
SELECT *
  FROM graph_table ( BAND_GRAPH
    MATCH (a where a.name='Kyuss') <- [m is member] -> (b)
    COLUMNS ( a.id AS src_id , a.name as src_name, b.id as dest_it, b.name as dest_name)
);

-- which bands are spinoffs of Kyuss
SELECT *
  FROM graph_table ( BAND_GRAPH
    MATCH (a where a.name='Kyuss') <- [m is spinoff] -> (b)
    COLUMNS ( a.id AS src_id , a.name as src_name, b.id as dest_it, b.name as dest_name)
);

-- which artists were members of snipoffs of Kyuss
SELECT kyuss, spinoff_name, spinoff_member
  FROM graph_table ( BAND_GRAPH
    MATCH (a where a.name='Kyuss') <- [m is spinoff] -> (s) <- [n is member] -> (b)
    COLUMNS ( a.id AS src_id , a.name as kyuss, s.name as spinoff_name, b.id as dest_it, b.name as spinoff_member)
  )
  order by spinoff_member;

-- what are the bands in which play the members of spinoffs of Kyuss
SELECT kyuss, spinoff_name, spinoff_member, band_name
  FROM graph_table ( BAND_GRAPH
    MATCH (a where a.name='Kyuss') <- [m is spinoff] -> (s) <- [n is member] -> (c) <- [o is member] -> (b)
    COLUMNS ( a.name as kyuss, s.name as spinoff_name, c.name as spinoff_member, b.name as band_name)
  )
  order by spinoff_member;


-- show the above in GRAPH visualization
SELECT *
 FROM GRAPH_TABLE ( BAND_GRAPH
  MATCH (k where k.name='Kyuss') <- [is_s is spinoff] -> (s) <- [is_m is member] -> (m) <- [is_b is member] -> (b)
  COLUMNS (VERTEX_ID(k) as kyuss, 
  EDGE_ID(is_s) as is_kyuss_spinoff, 
  VERTEX_ID(s) as spinoff, 
  EDGE_ID(is_m) as is_spinoff_member, 
  VERTEX_ID(m) as member, 
  EDGE_ID(is_b) as is_member_of,
  VERTEX_ID(b) as band)
) FETCH FIRST 300 ROW ONLY


-- like above, without last band
SELECT *
 FROM GRAPH_TABLE ( BAND_GRAPH
  MATCH (k where k.name='Kyuss') <- [is_s is spinoff] -> (s) <- [is_m is member] -> (m)
  COLUMNS (VERTEX_ID(k) as kyuss, 
  EDGE_ID(is_s) as is_kyuss_spinoff, 
  VERTEX_ID(s) as spinoff, 
  EDGE_ID(is_m) as is_spinoff_member, 
  VERTEX_ID(m) as member)
) FETCH FIRST 300 ROW ONLY
