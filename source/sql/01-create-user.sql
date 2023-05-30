alter session set container=FREEPDB1;

create user bands identified by Bands##123;

grant connect, resource , soda_app to bands;

alter user bands quota unlimited on users;


BEGIN
 ords_admin.enable_schema(
  p_enabled => TRUE,
  p_schema => 'BANDS',
  p_url_mapping_type => 'BASE_PATH',
  p_url_mapping_pattern => 'bands',
  p_auto_rest_auth => TRUE
 );
 commit;
END;
/

connect bands/Bands##123@localhost:1521/FREEPDB1
exec ords.enable_schema;
commit;
