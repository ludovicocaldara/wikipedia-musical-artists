"""
The mw_musical_artist class gets the content of a given MediaWiki Page
Parses the content to find Infoboxes, and tries to find content relative to Musical Artists
The resulting self.doc contains the dictionary that can easily be transformed to JSON.

e.g. 
ret = mw_musical_artist.mw_musical_artist('Kyuss').get_dict()"""
import json
import re
import logging
import requests
import mwparserfromhell

class NoMusicalInfoboxException(Exception):
    """ Exception to raise if no Musical Artist Infobox is found """

class RedirectException(Exception):
    """ Exception to raise if the Wikipedia page has been redirected """



class MWMusicalArtist:
    """ The mw_musical_artist class gets the content of a given MediaWiki Page
     Parses the content to find Infoboxes, and tries to find content relative to Musical Artists
     The resulting self.doc contains the dictionary that can easily be transformed to JSON.
    
     e.g.
     ret = mw_musical_artist.MWMusicalArtist('Kyuss').get_dict() """

    def __init__(self, name):
        """ The initialization does nothing but calling the _discover function"""
        self.link = name
        self.title = name # let's assume this until we get it
        self.is_artist = False

        log_format = ('%(asctime)s - %(levelname)-8s - ' +
                      self.link +' - %(funcName)-15s - %(message)s')
        logging.basicConfig(format=log_format, level=logging.ERROR)
        self._discover()


    def _get_wikitext(self):
        """
        Get the content from the Wikipedia Page pointed by self.link.
        We use requests and the MediaWiki API instead of wptools:
        the elapsed time goes down from 800ms to 300ms.

        Sets the title of the page in self.title.

        Returns: the wikitext for the page as a string.
        """
        url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "titles": self.link,
            "format": "json",
            "prop": "revisions",
            "rvprop": "content"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        pages = data["query"]["pages"]
        self.title = next(iter(pages.values()))["title"]
        return next(iter(pages.values()))["revisions"][0]["*"]



    def _discover(self):
        """ Get the content from the Wikipedia Page pointed by self.link"""

        # get the wikitext from the page using self.link
        wt = self._get_wikitext()

        # Redirections are a big issue with Wikipedia. The name of the page can
        # be different from the link, which exposes all possible issues
        # when inserting the data into the database (duplicates, etc.)
        # So we rather raise an exception here.
        if self.link != self.title:
            raise RedirectException("The page has been redirected")

        # We get the infoboxes from the page (see _find_infoboxes() for details)
        # infoboxes is an array of infobox templates already parsed
        # for actual musical artist.
        infoboxes = self._find_infoboxes(wt)


        # Now we parse the infoboxes and put each parameter in a single dictionary
        # which will be our glorious JSON one day.
        params = dict()
        for infobox in infoboxes:
            params.update(self._parse_infobox(infobox))

        # We try to further parse the parameters to normalize them
        # ( remove garbage, convert wikipedia lists to arrays, etc.)
        # If parsing is successful, we add it to the final dict()
        # (self.doc).
        self.doc = dict()
        for key, value in params.items():
            logging.debug('starting parsing parameter: {%s : %s}',
                           key, value, extra={"artist":self.link})
            parsed_param = self._parse_param({'name': key, 'value': value})
            logging.debug('ended parsing parameter: %s',
                          parsed_param, extra={"artist":self.link})
            if parsed_param:
                self.doc[key] = parsed_param

        # As the original link isn't part of the data, we add it here
        logging.debug('Setting artist as discovered', extra={"artist":self.link})
        self.doc['link'] = self.link

        # Compensating bad data here: there might be an Infobox without
        # the name of the artist. In that case, we just use the link.
        # yep... that happens (e.g. Kris Novoselic)
        if 'name' not in self.doc:
            self.doc['name'] = self.link


    def _find_infoboxes(self, text):
        """ 
        The function takes mediawiki text in input,
        and tries to find Infoboxes of an artist (and eventually a person infobox).
        Musical Artists are supposed to contain an infobox of type 
        "Musical Artist". The problem is that data on Wikipedia is s**t
        and it might not be the case. In that case, we just let it go.

        Why not WPTools? WPTools parse the main infobox, but that's not recrsive.
        Sadly, Infoboxes can contain other Infoboxes via the "module" parameter.
        This is the case with many popular artists (e.g. Dave Grohl).
        So we need to recursively search for Infoboxes and, if Musical Artist,
        also take into account the child or parent infoboxes.

        Returns: an array of infoboxes 
        """

        # initialize the infobox list
        infoboxes = list()

        # parse the mediawiki text to find ALL infoboxes
        templates = mwparserfromhell.parse(text).filter_templates()

        for template in templates:
            template_name = self._lint_value(template.name.strip())

            # Start looking for the good infobox
            if template_name.startswith("Infobox"):
                logging.debug('Found infobox template: %s',
                               template_name, extra={"artist":self.link})
                infoboxes.append(template)

                # Some pages incorrectly use "musician" instead of "musical artist"
                if template_name in [ "Infobox musical artist", "Infobox musician"]:
                    logging.debug('We are discovering an artist (is_artist=True)',
                                  extra={"artist":self.link})

                    # we mark it as an artist here, so we know it's an actual artist
                    # and in another loop we can take into account also
                    # other relevant infoboxes, such as "Person"
                    self.is_artist = True

                    # issue#5: If we find a Musical Artist Infobox,
                    # cut now and avoid problems with multiple artist infoboxes
                    break


        # if this is not an artist, let's raise an exception
        if not self.is_artist:
            raise NoMusicalInfoboxException("The page does not contain a musical artist infobox")

        return infoboxes



    def _parse_infobox(self, infobox):
        """
        Given an infobox in input, loops the properties and 
        lints them through the _lint_value() method.

        Returns: a dict() with the discovered properties.
        """

        params = {}

        infobox_name = self._lint_value(infobox.name.strip())
        logging.debug('Parsing all parameters in infobox: %s',
                      infobox_name, extra={"artist":self.link})

        # here I loop all the params from the infobox
        for param in infobox.params:
            param_name = self._lint_value(param.name.strip())
            param_value = self._lint_value(param.value.strip())

            if not self._need_to_skip(param_name):
                params[param_name] = param_value

        return params



    def _need_to_skip(self, param_name):
        """
          Given a parameter in input, it returns if the parameter
          must be skipped (True or False).
          Some parameters are only functional to Wikipedia metadata
          and don't provide anything to the artist's data.

          Returns: True or False
        """
        if param_name in ['embed', 'module']:
            return True
        else:
            return False


    def _need_to_split(self, param):
        """ 
        Given a parameter in input, it returns if the parameter
        must be splitted (True or False).
        These are typically parameters that contain lists.

        Returns: True or False
        """

        if param['name'] in ['label', 'alias', 'genre', 'associated_acts', 'occupation',
                             'instrument', 'instruments', 'current_member_of',
                             'past_member_of', 'spinoffs', 'spinoff_of',
                             'current_members', 'past_members',]:
            return True
        else:
            return False



    def _parse_param(self, param):
        """
        Given a parameter in input (dict of name and value), returns the correct values.

        Returns:
            * a string if the value is not empty and not a list
            * an array of strings if the value is a list to be splitted
            * False if the value is empty
        """

        if param['value'] == '':
            return False

        if self._need_to_split(param):
            ret = list()
            splitted_list = list(self._split_list(param))
            logging.debug('Splitted list result: (len:%d) %s',
                          len(splitted_list), splitted_list, extra={"artist":self.link})
            for item in splitted_list:
                ret.append(self._parse_item_for_link(item))
            return ret

        else:
            if param['value'] is not None and param['value'] and param['value']!= '':
                return param['value']
            else:
                return False



    def _parse_item_for_link(self, text):
        """ Given a text,
        it finds the first link occurrence and gets its text,
        then return a dict with link (eventually) and name.
        This function is to be used only with items coming from a list,
        or there might be many links!

        Returns:
            * if there is a link, {"link":link, "name":text}
            * otherwise, it returns {"name":text}
        """
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

    def _split_list (self, param):
        """
        Take a musical artist infobox parameter to split as a list and put it in a new list.
        It's more than a string split, as it has to take into account several
        listing possibilities of wikipedia.
        The musical artist infobox template doc says it should be one of:
            * hlist
            * flatlist
            * comma separated
        But there are too many exceptions like:
            * string separated by <br/>
            * mediawiki templates like unbullet lists
            * etc.
        Here I try to cover as many cases as possible.

        Returns: a new list to be used by the calling function.
        """
        ret_list = list()

        value = param['value']
        param_name = param['name']

        # we get the templates from within the property value:
        # we can have HList, FlatList, others, or no templates (comma-separated)
        logging.debug('Looking for templates to split in: %s' ,
                      value, extra={"artist":self.link})
        templates = mwparserfromhell.parse(value).filter_templates()

        if len(templates) == 0:
            logging.debug('No templates detected. Splitting %s using comma-ish separations',
                          param_name, extra={"artist":self.link})
            return self._split_string(value)

        else:
            for template in templates:
                template_name = self._lint_value(template.name.strip())
                logging.debug('Found template: %s', template_name, extra={"artist":self.link})

                if template_name.lower() in ['flatlist', 'plainlist']:
                    for item in template.params:
                        logging.debug('Splitting %s flatlist item: %s',
                                      param_name, item.value.strip(), extra={"artist":self.link})
                        ret_list = self._split_string(item.value.strip())
                    return ret_list


                elif template_name.lower() in [ 'hlist', 'ubl','unbullet list',
                                               'unbulleted list', 'collapsible list']:

                    for item in template.params:
                        logging.debug('Splitted %s %s item: %s',
                                      param_name, template_name, item.value.strip(),
                                      extra={"artist":self.link})

                        if item.value.strip():
                            ret_list.append(self._lint_value(item.value.strip()))
                    return ret_list
                else:
                    logging.debug('Unknown template for list: %s, treating as comma separated',
                                  template_name,    extra={"artist":self.link})
                    return self._split_string(value)



    def _lint_value(self, value):
        """ remove spaces, <ref> tags, and HTML comments"""
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



    def _split_string (self, string):
        """ split a flatlist or comma list into items"""
        separators = r'<br\/>|<br \/>|\n|, |,|\u2022'

        # Flatlists often use "^\* " as line heading, so better filter it out here with a lambda
        return list(filter(None, map(lambda item: item.lstrip("* "), re.split(separators, string))))



    def get_json(self):
        """ return a JSON string of the dict ready to print"""
        return json.dumps(self.doc, indent=4)


    def get_dict(self):
        """ return the dict of the band"""
        return self.doc
