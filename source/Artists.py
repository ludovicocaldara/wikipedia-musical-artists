import wptools 
import mwparserfromhell
import xmltodict
import json
import re
import logging


class MusicalArtist:
  ####################################################
  def __init__(self, name):
    self.name = name

    FORMAT = '%(asctime)s - %(levelname)-8s - '+ self.name +' - %(funcName)-15s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)

    self._discover()
    self._person_or_band()
    self._parse()



  ####################################################
  # get the content from the Wikipedia Page
  def _discover(self):

    # initialize the page using self.name
    page = wptools.page(self.name)

    # we are interested in the wikitext only. We'll use mwparserfromhell for the actual parsing.
    # WPTools offers a convenient way to get the Infobox, but it has several problems:
    #  - it messes up with nested templates (some artists like Dave Grohl have a generic person template with nested templates)
    #  - we cannot get the template name, which is fundamental to understand if we are crawling a good page
    page.get_parse('wikitext')

    # get the raw wiki text (str) to use with mwparserfromhell
    wt = page.data['wikitext']

    # we are interested in templates directly, no need for the actual text.
    # tempaltes is a list containing the various templates, each with name and params
    templates = mwparserfromhell.parse(wt).filter_templates()


    # We start with the assuption that the page is not an artist, then we'll validate it with the infobox information
    self.is_artist = False

    # is_person will be true for pages where the main infobox is person (like Dave Grohl)
    # not to be confused with the background that can be person or group_or_band
    self.is_person = False

    # initialize the infobox list
    self.infoboxes = list()

    # Here get the infobox type. 
    # We are interested in infoboxes "Infobox person" and "Inbofox musical artist".
    # If "Infobox person", then we need to dig until we get "Infobox musical artist", and use both.
    for template in templates:

      template_name = self._lint_value(template.name.strip())

      # scan the infoboxes
      if template_name.startswith("Infobox"):

        logging.debug('Looping infobox template: %s', template_name, extra={"artist":self.name})

        if template_name == "Infobox musical artist":
          logging.info('Found relevant template: %s', template_name, extra={"artist":self.name})
          logging.info('Discovering an artist (is_artist=True)', extra={"artist":self.name})
          self.is_artist = True
          self.infoboxes.append(template)

          break

        if template_name == "Infobox person":
          logging.info('Found relevant template: %s', template_name, extra={"artist":self.name})

          logging.debug('Appending the template to the list of relevant templates', extra={"artist":self.name})
          self.infoboxes.append(template)
  
          logging.info('We are discovering a person (is_person=True)', extra={"artist":self.name})
          self.is_person = True

          logging.debug('Infobox musical artist not found yet. Digging one morel level.', extra={"artist":self.name})
          # template alone string returns the actual wikitext. That's cool!
          person_templates = mwparserfromhell.parse(template).filter_templates()

          # Repeating the loop to finr person_templates.
          # A recursion would be much nicer here, but I'll dig just one level, so "meh".
          for person_template in person_templates:

            person_template_name = self._lint_value(person_template.name.strip())
            logging.debug('Looping infobox template: %s', person_template_name, extra={"artist":self.name})

            if person_template_name == "Infobox musical artist":
              logging.info('Found relevant template: %s', person_template_name, extra={"artist":self.name})

              logging.info('Discovering an artist (is_artist=True)', extra={"artist":self.name})
              self.is_artist = True
              self.infoboxes.append(person_template)
              break

          break


    # print the found infoboxes just for debug
    #for infobox in self.infoboxes:
    #  print ("======= INFOBOX ========")
    #  print (infobox)
    
    # some variable cleanup, I must improve variable cleaning
    del page, template, templates
    if 'person_templates' in dir():
      del person_templates
    if 'person_template' in dir():
      del person_template

    # if this is not an artist, let's raise an exception
    if not self.is_artist:
      raise Exception("The page does not contain a musical artist infobox")


    return


  ####################################################
  # According to Wikipedia's rules, Infobox musical artist requires a parameter "background" containing either "person" or "group_or_band"
  # However, for not having a relational model with constraints, there's a price to pay. It's a mess!
  # Some artists don't have "background". Some do, but the value is invalid.
  # So another way to tell them apart is to look for known properties specific to persons or bands.
  # That's why I put this in a different function.
  def _person_or_band(self):
    # here we don't know if person or band, unless detected with the infobox name during discover()
    if not self.is_person:

      logging.debug('Do not know if person or band yet, digging the Infoboxes to discover more', extra={"artist":self.name})
      artist_type_found = False

      for infobox in self.infoboxes:
        logging.debug('Looping infobox %s', infobox.name.strip(), extra={"artist":self.name})
        if self._lint_value(infobox.name.strip()) == 'Infobox musical artist':

          # According to Wikipedia, Infobox musical artist requires a parameter "background" containing either "person" or "group_or_band"
          # However, not all pages contain this. So the second rationale we are looking for is if the Infobox contains either one of {"current_member_of" , "past_member_of", "current_members", "past_members"}
          # If none of the above is there, it's not critical to skip this page, as we are looking for connections, not artist general information.
          try:
            artist_type = infobox.get('background').value.strip().lower()
            logging.debug('Got %s while getting the artist infobox background', artist_type, extra={"artist":self.name})
            if artist_type in ["person","group_or_band"]:
              logging.info('Artist type found in the background property! It\'s %s', artist_type, extra={"artist":self.name})
              self.artist_type = artist_type
              artist_type_found = True
              del artist_type
              break
          except:
            logging.debug('Could not get the artist infobox background.', extra={"artist":self.name})

          # looking for any band params here
          band_params = [ 'current_members', 'past_members', 'spinoffs', 'spinoff_of' ]
          for param_to_find in band_params:
            try:
              foo = infobox.get(param_to_find)
              logging.info('Found parameter %s in the artist infobox background. Assuming group_or_band', param_to_find, extra={"artist":self.name})
              self.artist_type = "group_or_band"
              artist_type_found = True
              del foo, param_to_find
              break
            except:
              logging.debug('Could not get the parameter %s in the artist infobox', param_to_find, extra={"artist":self.name})

          if artist_type_found:
            break

          # looking for any person params here
          person_params = [ 'current_member_of', 'past_member_of', 'occupation', 'instrument' ]
          for param_to_find in person_params:
            try:
              foo = infobox.get(param_to_find)
              logging.info('Found parameter %s in the artist infobox background. Assuming person', param_to_find, extra={"artist":self.name})
              self.artist_type = "person"
              artist_type_found = True
              del foo, param_to_find
              break
            except:
              logging.debug('Could not get the parameter %s in the artist infobox', param_to_find, extra={"artist":self.name})

          if artist_type_found:
            break

    else:
      self.artist_type = "person"
      artist_type_found = True

    # If we haven't found anything here, we cannot really continue
    if not artist_type_found:
      raise Exception('Cannot determine if group or person')


  ####################################################
  def _parse(self):

    logging.debug('Starting parsing the infoboxes content into a dict for JSON creation', extra={"artist":self.name})

    # the artist type should be known here, or we should have raised an exception before entering this function
    assert self.artist_type in [ 'person', 'group_or_band' ]

    # self.doc will contain the data of the JSON document
    self.doc = {}

    # _params contain the parameter which I translate 1:1 as a JSON property
    common_params = [ 'name', 'wikipedia_link', 'origin', 'website', ]

    # _specials contain special parameter which I might translate to list(dict()) or something different
    common_specials = [
      'image',  'image_upright', 'image_size', 'landscape', 'alt', 'caption',  # -> into image json
      'years_active', 'alias', 'genre', 'label', 'associated_acts', # -> list
      ]

    person_params = [ 'honorific_prefix', 'honorific_suffix', 'native_name', 'native_name_lang', 'birth_name', 'birth_date', 'birth_place', 'death_date', 'death_place', ]

    person_specials = [ 'occupation', 'instrument', 'current_member_of', 'past_member_of', ]

    band_params = [] # they are all specials

    band_specials = [ 'spinoffs', 'spinoff_of', 'current_members', 'past_members', ]


    # if we are here without exception, we know if person or band
    # depending on it, I load the list of relevant parameters
    if self.artist_type == 'person':
      relevant_params = common_params + person_params
      relevant_specials = common_specials + person_specials
    elif self.artist_type == 'group_or_band':
      relevant_params = common_params + band_params
      relevant_specials = common_specials + band_specials

    # here I loop all the parameters and I add them to the doc
    for infobox in self.infoboxes:

      infobox_name = self._lint_value(infobox.name.strip())
      logging.debug('Parsing all parameters in infobox: %s', infobox_name, extra={"artist":self.name})

      for param in infobox.params:

        param_name = self._lint_value(param.name.strip())
        logging.debug('Parsing the parameter: %s', param_name, extra={"artist":self.name})

        if param_name in relevant_params:
          logging.info('Found relevant regular parameter: %s', param_name, extra={"artist":self.name})
          self.doc[param_name] = self._lint_value(param.value.strip())

        if param_name in relevant_specials:
          logging.info('Found relevant special parameter: %s', param_name, extra={"artist":self.name})
          # I treat any special parameters in a dedicated function
          self._special_param(param)

    print(json.dumps(self.doc, indent=4))


  ####################################################
  # remote spaces, <ref> tags, and HTML comments
  def _lint_value(self, value):

    # remove ref tags
    value = re.sub(r'<ref\b[^>]*\/?>.*?<\/ref>', '', value, flags=re.DOTALL)

    ## remove self-closing tags
    #value = re.sub(r'<[^>]+\/>', '', value)

    # remove HTML comments
    value = re.sub("(<!--.*?-->)", "", value, flags=re.DOTALL)

    # return stripped
    return value.strip()


  
  ####################################################
  # split a flatlist or comma list into items
  def _split_string (self, string):
      separators = r'<br\/>|<br \/>\n|[\n,]'
      return ( re.split(separators, string))

  ####################################################
  # take a musical artist infobox parameter to split as a list and put it in a new list.
  # returns a new list to be used by the calling function.
  # it's more than a string split, as it has to take into account several listing possibilities of wikipedia.
  # Again, the template doc says it should be hlist, flatlist, or comma separated, but there are too many exceptions
  # like <br/>, or templates like unbullet lists, etc. So I try to cover as much as possible in this function.
  def _split_list (self, param):
    ret_list = list()

    value = param.value.strip()
    value = self._lint_value(value)
    print ("trying splitting "+ value)

    param_name = self._lint_value(param.name.strip())

    # we get the templates from within the property value: we can have HList, FlatList, others, or no templates (comma-separated)
    logging.debug('Looking for templates to split in: %s' , value,  extra={"artist":self.name})
    templates = mwparserfromhell.parse(value).filter_templates()

    if len(templates) == 0:
      logging.debug('No templates detected. Splitting %s using comma-ish separations', param_name,  extra={"artist":self.name})
      return self._split_string(value)

    else:
      for template in templates:
        template_name = self._lint_value(template.name.strip())
        logging.debug('Found template: %s', template_name,  extra={"artist":self.name})

        if template_name.lower() == 'flatlist':
          for item in template.params:
            logging.debug('Splitting %s flatlist item: %s', param_name, item.value.strip(),  extra={"artist":self.name})
            ret_list.append(self._split_string(item.value.strip()))
          return ret_list


        elif template_name.lower() in [ 'hlist', 'ubl','unbullet list']:

          for item in template.params:
            logging.debug('Splitted %s %s item: %s', param_name, template_name, item.value.strip(),  extra={"artist":self.name})

            ret_list.append(self._lint_value(item.value.strip()))
          return ret_list
        else:
          logging.debug('Unknown template for list: %s', template_name,  extra={"artist":self.name})


  ####################################################
  # Function to split name and link.
  # e.g.
  #        "[[Dan Gilroy (musician)|Dan Gilroy]]",  => {'name':'Dan Gilroy','link':'Dan Gilroy (musician)'}
  #        "[[Stephen Bray]]", => {'name':'Stephen Bray','link':'Stephen Bray'}
  #        "Paul Kauk", => {'name':'Paul Kauk','link':''}
  #
  # the idea is to keep the mw page for more robust discovery: collect the name and the link, discover using the link, try the name if the link is not there.
  # so if an artist is not discoverable, the link can be searched and updated manually
  def _split_name_link(self, mwlink):
    pass

  ####################################################
  # these params require special treatment
  def _special_param(self, param):
    # image-related parameters

    param_name = self._lint_value(param.name.strip())
    if param_name in ['image', 'image_upright', 'image_size', 'landscape', 'alt', 'caption' ] :
      logging.debug('Adding image property to the image dict: %s', param_name, extra={"artist":self.name})
      if not 'image' in self.doc:
        self.doc['image'] = dict()
      self.doc['image'][param_name] = self._lint_value(param.value.strip())

    elif param_name == 'label':
      self.doc['labels'] = list(self._split_list(param))
    elif param_name == 'alias':
      self.doc['aliases'] = list(self._split_list(param))
    elif param_name == 'genre':
      self.doc['genres'] = list(self._split_list(param))
    elif param_name == 'associated_acts':
      self.doc['associated_acts'] = list(self._split_list(param))
    elif param_name == 'occupation':
      self.doc['occupations'] = list(self._split_list(param))
    elif param_name == 'instrument':
      self.doc['instruments'] = list(self._split_list(param))
    elif param_name == 'current_member_of':
      self.doc['current_member_of'] = list(self._split_list(param))
    elif param_name == 'past_member_of':
      self.doc['past_member_of'] = list(self._split_list(param))
    elif param_name == 'spinoffs':
      self.doc['spinoffs'] = list(self._split_list(param))
    elif param_name == 'current_members':
      self.doc['current_members'] = list(self._split_list(param))
    elif param_name == 'past_members':
      self.doc['past_members'] = list(self._split_list(param))
      

#    elif
#      'years_active', # -> list

      'spinoff_of',
