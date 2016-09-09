# coding=utf-8
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup
from google.appengine.api import urlfetch, memcache
from google.appengine.ext import db
import re


class Material(db.Model):
    text = db.TextProperty()


def get_material(name):
    key = db.Key.from_path('Material', str(name))
    material = db.get(key)
    if material is None:
        material = Material(key_name=str(name))
        material.put()
    return material


def update_material(material, devo):
    material.text = devo
    material.put()


# still a java programmer at heart HAHA
class Utmost_Devo_POJO:
    def __init(self):
        # date object storing date for
        self.date = None
        self.heading = None
        self.verse_reference = None
        self.bible_in_a_year = None
        self.verse_concise = None
        self.verse_full = None
        self.post = None

        # write get and set

        # link to get full verse
        self.link_to_full_verse_bgw = None
        self.link_to_full_verse_yv = None

    def format_to_message(self, version_abbv):
        def if_concise_is_full():
            return '…'.decode('utf-8') in self.verse_concise

        # devotion = dynamic_header
        devotion = ' QT - _' + self.date + '_\n\n*'
        devotion += self.heading + '*\n'

        if if_concise_is_full():
            devotion += "_" + self.verse_concise + '_\n\n'
        else:
            devotion += "\n"

        devotion += (
            '\xF0\x9F\x93\x99	*Scripture ('.decode("utf-8") + version_abbv + ')*\n\n'.decode("utf-8")
            + self.verse_full + '\n\n'
            + '	\xF0\x9F\x93\x9D *Reflection*'.decode("utf-8")
            + self.post + "\n"
            + '💪'.decode("utf-8") + ' *Bible in a Year*\n\n'
            + self.bible_in_a_year
        )
        return devotion

    def toString(self):
        # TODO rename
        returnz = ""

        if self.date is not None:
            returnz += self.date + "\n"

        if self.heading is not None:
            returnz += self.heading + "\n"

        if self.verse_reference is not None:
            returnz += self.verse_reference + "\n"

        if self.bible_in_a_year is not None:
            returnz += self.bible_in_a_year + "\n"

        if self.verse_concise is not None:
            returnz += self.verse_concise + "\n"

        if self.verse_full is not None:
            returnz += self.verse_full + "\n"

        return returnz

    def is_utmost_parse_success(self):
        return (self.date is not None
                and self.heading is not None
                and self.verse_reference is not None
                and self.bible_in_a_year is not None
                and self.verse_concise is not None
                and self.post is not None)


class UtmostDevoSource(object):
    DEVO_BASE_URL = "http://jiachen.rocks/mytmpdir/jiachen.html"
    base_devo_url = "https://utmost.org/2004/{0}/{1}?calendar-redirect=true&post-type=post".format
    devo_object = None
    STORE_CACHE = True

    YESTERDAY = -1
    TODAY = 0
    TOMORROW = 1

    def strip_markdown(self, string):
        return string.replace('*', ' ').replace('_', ' ').replace('[', '\[')

    def get_devo(self, delta=0, version="esv"):

        today_date = datetime.utcnow() + timedelta(hours=8, days=delta)

        daynames = ['Yesterday\'s', 'Today\'s', 'Tomorrow\'s']
        devo_dynamic_header = '\xF0\x9F\x93\x85 '.decode("utf-8") + ' ' + daynames[delta + 1]

        memkey = today_date.strftime("%d-%m-{}".format(version))
        devo = memcache.get(memkey)

        if devo is not None:
            logging.info("memkey {} hit. Returning...".format(memkey))
            return devo_dynamic_header + devo

        material = get_material(memkey)

        if material.text is not None:
            logging.info("datastore {} hit. Returning...".format(memkey))
            memcache.set(memkey, material.text)
            return devo_dynamic_header + material.text

        # lazy init
        self.devo_object = Utmost_Devo_POJO()

        try:
            result = urlfetch.fetch(self.base_devo_url(today_date.month, today_date.day), follow_redirects=True,
                                    deadline=10)
        except Exception as e:
            logging.warning('Error fetching devo:\n' + str(e))
            return None

        parse_status = self.__parse_utmost_org(result.content, today_date)

        self.devo_object.link_to_full_verse_bgw = self.devo_object.link_to_full_verse_bgw.replace("31", version)
        self.devo_object.bible_in_a_year = self.devo_object.bible_in_a_year.replace("31", version)

        logging.debug("link_to_full_verse__bgw : {}".format(self.devo_object.link_to_full_verse_bgw))
        logging.debug("bible in a year : {}".format(self.devo_object.bible_in_a_year))

        if not parse_status:
            logging.warning('Error parseing devo:\n')

            if delta == self.YESTERDAY:
                return 'Sorry, yesterday\'s material is no longer available.'
            elif delta == self.TODAY:
                return 'Sorry, today\'s material is not available.'
            elif delta == self.TOMORROW:
                return 'Sorry, tomorrows\'s material is no longer available.'

        try:
            result = urlfetch.fetch(self.devo_object.link_to_full_verse_bgw, deadline=10)
        except Exception as e:
            logging.warning('Error fetching verse:\n' + str(e))
            return None

        self.devo_object.link_to_full_verse_yv = self.__get_youversion_link(verse_ref=self.devo_object.verse_reference,
                                                                            version=version)
        parse_status = self.__parse_biblegateway_com(result.content)

        logging.info("Parsing Success:: All content parsed successfuly.")
        final_devo = self.devo_object.format_to_message(version_abbv=version)

        # cache
        if self.STORE_CACHE:
            logging.debug("Storing devo in memcache & db {}".format(memkey))
            memcache.set(memkey, final_devo)
            update_material(material, final_devo)

        return devo_dynamic_header + final_devo

    def get_devo_old(self, delta=TODAY):
        pass

    def __parse_utmost_org(self, html, today_date):

        logging.debug("Starting to parse utmost.org::")
        try:
            soup = BeautifulSoup(html, 'lxml')

            date = today_date.strftime('%b %-d, %Y ({})').format(today_date.strftime('%a').upper())
            heading = soup.select_one('.entry-title').text.strip()
            verse_consise = soup.select_one('#key-verse-box > p').text
            demarc = verse_consise.index("—".decode("utf-8"))
            verse_consise = verse_consise[:demarc]
            verse_reference = soup.select_one('#key-verse-box > p > a').text
            post = self.strip_markdown(soup.select_one('.post-content').text.replace("\n", "\n\n"))
            link_to_verse = soup.select_one('#key-verse-box > p > a').get("href").strip()

            bible_in_a_year = soup.select_one('#bible-in-a-year-box > a').get("href").strip()
            bible_in_a_year_text = "[" + soup.select_one('#bible-in-a-year-box > a').text.replace("; ",
                                                                                                  "\n") + "](" + bible_in_a_year + ")"

            self.devo_object.date = date
            self.devo_object.heading = heading
            self.devo_object.verse_concise = verse_consise
            self.devo_object.verse_reference = verse_reference
            self.devo_object.post = post
            self.devo_object.bible_in_a_year = bible_in_a_year_text
            # IMPT - wont carry on without setting this
            self.devo_object.link_to_full_verse_bgw = link_to_verse

        except Exception as e:
            logging.warning('Error parsing utmost devo:\n' + str(e))
            return False

        finally:
            return True

    def __parse_biblegateway_com(self, html):
        # stole this code from @biblegatewaybot
        def strip_markdown(string):
            return string.replace('*', '\*').replace('_', '\_').replace('`', '\`').replace('[', '\[')

        EMPTY = "empty"

        def to_sup(text):
            sups = {u'0': u'\u2070',
                    u'1': u'\xb9',
                    u'2': u'\xb2',
                    u'3': u'\xb3',
                    u'4': u'\u2074',
                    u'5': u'\u2075',
                    u'6': u'\u2076',
                    u'7': u'\u2077',
                    u'8': u'\u2078',
                    u'9': u'\u2079',
                    u'-': u'\u207b'}
            return ''.join(sups.get(char, char) for char in text)

        start = html.find('<div class="passage-text">')
        if start == -1:
            return EMPTY
        end = html.find('<!--END .passage-text-->', start)
        passage_html = html[start:end]

        soup = BeautifulSoup(passage_html, 'lxml').select_one('.passage-text')

        WANTED = 'bg-bot-passage-text'
        UNWANTED = '.passage-display, .footnote, .footnotes, .crossrefs, .publisher-info-bottom'

        title = soup.select_one('.passage-display-bcv').text

        def getVerseHref():
            return self.devo_object.link_to_full_verse_yv if self.devo_object.link_to_full_verse_yv is not None else self.devo_object.link_to_full_verse_bgw

        header = '[' + strip_markdown(title.strip()) + '](' + getVerseHref() + ')'

        for tag in soup.select(UNWANTED):
            tag.decompose()

        for tag in soup.select('h1, h2, h3, h4, h5, h6'):
            tag['class'] = WANTED
            text = tag.text.strip()
            tag.string = '*' + strip_markdown(text) + '*'

        needed_stripping = False

        for tag in soup.select('p'):
            tag['class'] = WANTED
            bad_strings = tag(text=re.compile('(\*|\_|\`|\[)'))
            for bad_string in bad_strings:
                stripped_text = strip_markdown(unicode(bad_string))
                bad_string.replace_with(stripped_text)
                needed_stripping = True

        if needed_stripping:
            logging.info('Stripped markdown')

        for tag in soup.select('br'):
            tag.name = 'span'
            tag.string = '\n'

        for tag in soup.select('.chapternum'):
            num = tag.text.strip()
            tag.string = '*' + strip_markdown(num) + '*'

        for tag in soup.select('.versenum'):
            num = tag.text.strip()
            tag.string = to_sup(num)

        for tag in soup.select('.text'):
            tag.string = tag.text.rstrip()

        final_text = header + '\n'
        for tag in soup(class_=WANTED):
            final_text += tag.text.strip() + '\n\n'

        logging.debug('Finished BeautifulSoup processing')

        self.devo_object.verse_full = final_text.strip()
        return

    def __get_youversion_link(self, verse_ref, version):

        version_map = {
            "ESV": "59",
            "AMP": "8",
            "NLT": "116",
            "MSG": "97",
            "NKJV": "114"
        }

        URL = "https://www.bible.com/bible/{}/".format(version_map[version])

        def modify_verse_ref(ref):
            book_lookup = {
                'Genesis': 'gen',
                'Exodus': 'exo',
                'lev': 'Lev',
                'num': 'Num',
                'Deuteronomy': 'deu',
                'Joshua': 'jos',
                'Judges': 'jdg',
                'Ruth': 'rut',
                '1 Samuel': '1sa',
                '2 Samuel': '2sa',
                '1 Kings': '1ki',
                '2 Kings': '2ki',
                '1 Chronicles': '1ch',
                '2 Chronicles': '2ch',
                'Ezra': 'ezr',
                'Nehemiah': 'neh',
                'Esther': 'est',
                'Job': 'job',
                'Psalms': 'psa',
                'Proverbs': 'pro',
                'Ecclesiastes': 'ecc',
                'Song of Solomon': 'sng',
                'Isaiah': 'isa',
                'Jeremiah': 'jer',
                'Lamentations': 'lam',
                'Ezekiel': 'ezk',
                'Daniel': 'dan',
                'Hosea': 'hos',
                'Joel': 'jol',
                'Amos': 'amo',
                'Obadiah': 'oba',
                'Jonah': 'jon',
                'Micah': 'mic',
                'Nahum': 'nam',
                'Habakkuk': 'hab',
                'Zephaniah': 'zep',
                'Haggai': 'hag',
                'Zechariah': 'zec',
                'Malachi': 'mal',
                'Matthew': 'mat',
                'Mark': 'mrk',
                'Luke': 'luk',
                'John': 'jhn',
                'Acts': 'act',
                'Romans': 'rom',
                '1 Corinthians': '1co',
                '2 Corinthians': '2co',
                'Galatians': 'gal',
                'Ephesians': 'eph',
                'Philippians': 'php',
                'Colossians': 'col',
                '1 Thessalonians': '1th',
                '2 Thessalonians': '2th',
                '1 Timothy': '1ti',
                '2 Timothy': '2ti',
                'Titus': 'tit',
                'Philemon': 'phm',
                'Hebrews': 'heb',
                'James': 'jas',
                '1 Peter': '1pe',
                '2 Peter': '2pe',
                '1 John': '1jn.',
                '2 John': '2jn.',
                '3 John': '3jn.',
                'Jude': 'jud',
                'Revelation': 'rev'
            }
            for old_name, new_name in book_lookup.iteritems():
                if ref.startswith(old_name):
                    return ref.replace(old_name, new_name).replace(" ", ".").replace(":", ".")
            else:
                logging.debug("No book found : ERROR")
                return None

        URL += modify_verse_ref(verse_ref)
        logging.debug("youversion link : " + URL)
        return URL
