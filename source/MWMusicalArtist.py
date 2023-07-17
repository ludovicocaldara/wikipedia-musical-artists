import wptools 
import mwparserfromhell
import xmltodict
import json
import re
import logging

class NoMusicalInfoboxException(Exception):
  pass

class RedirectException(Exception):
  pass


#############################################
# The MWMusicalArtist class gets the content of a given MediaWiki Page
# Parses the content to find Infoboxes, and tries to find content relative to Musical Artists
# The resulting self.doc contains the dictionary that can easily be transformed to JSON.
#
# e.g. 
# ret = MWMusicalArtist.MWMusicalArtist('Kyuss').getDict()
#


class MWMusicalArtist:
  ####################################################
  def __init__(self, name):
    self.link = name

    FORMAT = '%(asctime)s - %(levelname)-8s - '+ self.link +' - %(funcName)-15s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    self._discover()


  ####################################################
  # get the content from the Wikipedia Page
  def _discover(self):

    # initialize the page using self.link
    page = wptools.page(self.link)


    page.get_parse('wikitext')
    wt = page.data['wikitext']

    if self.link != page.data['title']:
      raise RedirectException("The page has been redirected")

    infoboxes = self._find_infoboxes(wt)
    params = dict()
    for infobox in infoboxes:
      params.update(self._parse_infobox(infobox))

    self.doc = dict()
    for key, value in params.items():
      logging.debug('starting parsing parameter: {%s : %s}', key, value, extra={"artist":self.link})
      parsed_param = self._parse_param({'name': key, 'value': value})
      logging.debug('ended parsing parameter: %s', parsed_param, extra={"artist":self.link})
      if parsed_param:
        self.doc[key] = parsed_param

    logging.info('Setting artist as discovered', extra={"artist":self.link})
    self.doc['link'] = self.link
    # yep... that happens (e.g. Kris Novoselic)
    if 'name' not in self.doc:
      self.doc['name'] = self.link
    self.doc['discovered'] = True
    logging.debug('Discovered dict: %s', self.doc, extra={"artist":self.link})




  ##################################################
  # given a text in input, return the list of infoboxes
  def _find_infoboxes(self, text):

    # we aim to find an artist (and eventually a person infobox)
    self.is_artist = False

    # initialize the infobox list
    infoboxes = list()

    templates = mwparserfromhell.parse(text).filter_templates()

    for template in templates:
      template_name = self._lint_value(template.name.strip())
      template_value = self._lint_value(template.strip())

      # scan the infoboxes
      if template_name.startswith("Infobox"):
        logging.debug('Found infobox template: %s', template_name, extra={"artist":self.link})
        infoboxes.append(template)

        if template_name in [ "Infobox musical artist", "Infobox musician"]:
          logging.info('We are discovering an artist (is_artist=True)', extra={"artist":self.link})
          self.is_artist = True


    # if this is not an artist, let's raise an exception
    if not self.is_artist:
      raise NoMusicalInfoboxException("The page does not contain a musical artist infobox")

    return infoboxes



  ####################################################
  # given an infobox in input, return a dict() with the discovered parameters
  def _parse_infobox(self, infobox):

    params = {}

    infobox_name = self._lint_value(infobox.name.strip())
    logging.debug('Parsing all parameters in infobox: %s', infobox_name, extra={"artist":self.link})

    # here I loop all the params from the infobox
    for param in infobox.params:
      param_name = self._lint_value(param.name.strip())
      param_value = self._lint_value(param.value.strip())

      if not self._need_to_skip(param_name):
        params[param_name] = param_value

    return params



  ######################################
  # given a parameter in input, it returns if the parameter must be splitted (True or False)
  def _need_to_skip(self, param_name):
    if param_name in ['embed', 'module']:
      return True
    else:
      return False


  ######################################
  # given a parameter in input, it returns if the parameter must be splitted (True or False)
  def _need_to_split(self, param):
    if param['name'] in ['label', 'alias', 'genre', 'associated_acts', 'occupation', 'instrument', 'instruments', 'current_member_of', 'past_member_of', 'spinoffs', 'current_members', 'past_members',]:
      return True
    else:
      return False



  ######################################
  # given a parameter in input (dict of name and value), returns the correct values
  def _parse_param(self, param):

    if param['value'] == '':
        return False

    if self._need_to_split(param):
      ret = list()
      splitted_list = list(self._split_list(param))
      logging.debug('Splitted list result: (len:%d) %s', len(splitted_list), splitted_list, extra={"artist":self.link})
      for item in splitted_list:
        ret.append(self._parse_item_for_link(item))
      return ret

    else:
      if param['value'] is not None and param['value'] and param['value']!= '':
        return param['value']
      else:
        return False



  #####################################
  # given a text , it find the first link occurrence and get its text, then return a dict
  # to be used only with items coming from a list, or there might be many links!
  # if there is a link, it returns {"link":link, "name":text}
  #          otherwise, it returns {"name":text}
  def _parse_item_for_link(self, text):

        logging.debug('Looking for MW links in: %s', text, extra={"artist":self.link})
        links = mwparserfromhell.parse(text).filter_wikilinks()
        if len(links) == 0:
          logging.debug('no links in %s', text, extra={"artist":self.link})
          return {'name':text.strip()}
        else:
          logging.debug('link found in: %s', links[0], extra={"artist":self.link})
          if not links[0].text:
            links[0].text = links[0].title
          # assume just one link, or we are doomed :-/
          return {'link':links[0].title.strip(), 'name':links[0].text.strip()}



  ####################################################
  # take a musical artist infobox parameter to split as a list and put it in a new list.
  # returns a new list to be used by the calling function.
  # it's more than a string split, as it has to take into account several listing possibilities of wikipedia.
  # Again, the template doc says it should be hlist, flatlist, or comma separated, but there are too many exceptions
  # like <br/>, or templates like unbullet lists, etc. So I try to cover as much as possible in this function.
  def _split_list (self, param):
    ret_list = list()

    value = param['value']
    param_name = param['name']

    # we get the templates from within the property value: we can have HList, FlatList, others, or no templates (comma-separated)
    logging.debug('Looking for templates to split in: %s' , value,  extra={"artist":self.link})
    templates = mwparserfromhell.parse(value).filter_templates()

    if len(templates) == 0:
      logging.debug('No templates detected. Splitting %s using comma-ish separations', param_name,  extra={"artist":self.link})
      return self._split_string(value)

    else:
      for template in templates:
        template_name = self._lint_value(template.name.strip())
        logging.debug('Found template: %s', template_name,  extra={"artist":self.link})

        if template_name.lower() in ['flatlist', 'plainlist']:
          for item in template.params:
            logging.debug('Splitting %s flatlist item: %s', param_name, item.value.strip(),  extra={"artist":self.link})
            ret_list = self._split_string(item.value.strip())
          return ret_list


        elif template_name.lower() in [ 'hlist', 'ubl','unbullet list', 'unbulleted list']:

          for item in template.params:
            logging.debug('Splitted %s %s item: %s', param_name, template_name, item.value.strip(),  extra={"artist":self.link})

            ret_list.append(self._lint_value(item.value.strip()))
          return ret_list
        else:
          logging.debug('Unknown template for list: %s, treating as comma separated', template_name,  extra={"artist":self.link})
          return self._split_string(value)



  ####################################################
  # remove spaces, <ref> tags, and HTML comments
  def _lint_value(self, value):
    # remove ref tags
    value = re.sub(r'<ref\b[^>]*\/?>.*?<\/ref>', '', value, flags=re.DOTALL)
    # remove self-closing ref tags
    value = re.sub(r"<ref\s+[^>]*\s*/>", "", value)
    ## remove self-closing tags
    #value = re.sub(r'<[^>]+\/>', '', value)
    # remove HTML comments
    value = re.sub("(<!--.*?-->)", "", value, flags=re.DOTALL)
    # return stripped
    return value.strip()


  
  ####################################################
  # split a flatlist or comma list into items
  def _split_string (self, string):
      separators = r'<br\/>|<br \/>|\n|, |,|\u2022'

      # Flatlists often use "^\* " as line heading, so better filter it out here with a lambda
      return list(filter(None, map(lambda item: item.lstrip("* "), re.split(separators, string))))



  ####################################################
  # return a JSON string of the dict ready to print
  def getJson(self):
    return json.dumps(self.doc, indent=4)


  ####################################################
  # return the dict of the band
  def getDict(self):
    return self.doc
