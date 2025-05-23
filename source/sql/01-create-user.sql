create user bands identified by Welcome##123 default tablespace users;

grant connect, resource , soda_app, create domain, create mle  to bands;
grant execute on javascript to bands;

alter user bands quota unlimited on users;
grant graph_developer to bands;
alter user bands grant connect through graph$proxy_user;

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

