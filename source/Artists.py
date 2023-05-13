import wptools 
import mwparserfromhell
import xmltodict
import json
import re


class MusicalArtist:
  ####################################################
  def __init__(self, name):
    self.name = name
    self._discover()
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
      # scan the infoboxes
      if template.name.startswith("Infobox"):
        if template.name.strip() == "Infobox musical artist":
          self.is_artist = True
          self.infoboxes.append(template)
          print ("Infobox musical artist detected")
          break

        if template.name.strip() == "Infobox person":
          print ("Infobox person detected")
          self.infoboxes.append(template)
  
          # here we are sure it's a person already
          self.is_person = True

          # template alone string returns the actual wikitext. That's cool!
          person_templates = mwparserfromhell.parse(template).filter_templates()

          # Repeating the loop to finr person_templates.
          # A recursion would be much nicer here, but I'll dig just one level, so "meh".
          for person_template in person_templates:
            if person_template.name.strip() == "Infobox musical artist":
              self.is_artist = True
              self.infoboxes.append(person_template)
              print ("Nested Infobox musical artist detected")
              break

          break

    # print the found infoboxes just for debug
    #for infobox in self.infoboxes:
    #  print ("======= INFOBOX ========")
    #  print (infobox)
    
    # some variable cleanup
    del page, template, templates
    if 'person_templates' in dir():
      del person_templates
    if 'person_template' in dir():
      del person_template

    # if this is not an artist, let's raise a nice exception
    if not self.is_artist:
      raise Exception("Not a musical artist")


    return




  ####################################################
  def _parse(self):

    # self.doc will contain the data of the JSON document
    self.doc = {}

    # background        = person

    # _params contain the parameter which I translate 1:1 as a JSON property
    common_params = [
      'name',
      'wikipedia_link',
      'origin',
      'website',
      ]

    # _specials contain special parameter which I might translate to list(dict()) or something different
    common_specials = [
      'image',  # -> into image json
      'image_upright',  # -> into image json
      'image_size',  # -> into image json
      'landscape',  # -> into image json
      'alt',  # -> into image json
      'caption',  # -> into image json
      'years_active', # -> list
      'alias', # -> list
      'genre', # -> list
      'label',  #-> list
      'associated_acts', # -> list
      ]


    person_params = [
      'honorific_prefix',
      'honorific_suffix',
      'native_name',
      'native_name_lang',
      'birth_name',
      'birth_date',
      'birth_place',
      'death_date',
      'death_place',
      ]

    person_specials = [
      'occupation',
      'instrument',
      'current_member_of',
      'past_member_of',

    ]

    band_params = [
     # they are all specials
    ]

    band_specials = [
      'spinoffs',
      'spinoff_of',
      'current_members',
      'past_members',
    ]

    # here we don't know if person or band, unless detected with the infobox name during discover()
    if not self.is_person:
      for infobox in self.infoboxes:
        if infobox.name.strip() == 'Infobox musical artist':
          try:
            self.artist_type = infobox.get('background').value.strip()
            if self.artist_type == "person":
              self.is_person = "person"
          except:
            raise Exception('Cannot determine if group or person')
          break
    else:
      self.artist_type = "person"

    # if we are here without exception, we know if person or band
    # depending on it, I load the list of relevant parameters
    if self.artist_type == 'person':
      relevant_params = common_params + person_params
      relevant_specials = common_specials + person_specials
    elif self.artist_type == 'group_or_band':
      relevant_params = common_params + band_params
      relevant_specials = common_specials + band_specials
    else:
      raise Exception('Invalid artist type: '+ self.artist_type)

    # here I loop all the parameters and I add them to the doc
    for infobox in self.infoboxes:
      for param in infobox.params:
        if param.name.strip() in relevant_params:
          print ("normal parameter: " + param.name.strip())
          self.doc[param.name.strip()] = self._lint_value(param.value.strip())
        if param.name.strip() in relevant_specials:
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
  # take a parameter to split as a list and put it in a new list
  # the "key" parameter is the dict key for the new list
  def _split_list (self, param, key):
    if not key in self.doc:
      self.doc[key] = list()

    value = param.value.strip()
    value = self._lint_value(value)
    print ("trying splitting "+ value)
    # we can have HList, FlatList or comma-separated
    templates = mwparserfromhell.parse(value).filter_templates()
    if len(templates) == 0:
      print ("detected type comma")
      splitted_list = self._split_string(value)
      for item in splitted_list:
        self.doc[key].append({param.name.strip(): item})

    else:
      for template in templates:

        if template.name == 'flatlist':
          print ("detected type flatlist")
          for item in template.params:
            print ("item --- " + param.name.strip() + ":" + item.value.strip())
            splitted_list = self._split_string(item.value.strip())
            for item in splitted_list:
              self.doc[key].append({param.name.strip(): item})

            #self.doc[key].append({param.name.strip(): self._lint_value(item.value.strip())})

        elif template.name == 'Hlist':
          print ("detected type Hlist")
          for item in template.params:
            print ("item --- " + param.name.strip() + ":" + item.value.strip())
            self.doc[key].append({param.name.strip(): self._lint_value(item.value.strip())})


    #self.doc[key].append({param.name.strip(): self._lint_value(param.value.strip())})






  ####################################################
  # these params require special treatment
  def _special_param(self, param):
    # image-related parameters
    if param.name.strip() in ['image', 'image_upright', 'image_size', 'landscape', 'alt', 'caption' ] :
      if not 'image' in self.doc:
        self.doc['image'] = dict()

      self.doc['image'][param.name.strip()] = self._lint_value(param.value.strip())
    elif param.name.strip() == 'label':
      self._split_list(param, 'labels')
    elif param.name.strip() == 'alias':
      self._split_list(param, 'aliases')
    elif param.name.strip() == 'genre':
      self._split_list(param, 'genres')
    elif param.name.strip() == 'associated_acts':
      self._split_list(param, 'associated_acts')
    elif param.name.strip() == 'occupation':
      self._split_list(param, 'occupations')
    elif param.name.strip() == 'instrument':
      self._split_list(param, 'instruments')
    elif param.name.strip() == 'current_member_of':
      self._split_list(param, 'current_member_of')
    elif param.name.strip() == 'past_member_of':
      self._split_list(param, 'past_member_of')
    elif param.name.strip() == 'spinoffs':
      self._split_list(param, 'spinoffs')
    elif param.name.strip() == 'current_members':
      self._split_list(param, 'current_members')
    elif param.name.strip() == 'past_members':
      self._split_list(param, 'past_members')
      

#    elif
#      'years_active', # -> list

      'spinoff_of',
