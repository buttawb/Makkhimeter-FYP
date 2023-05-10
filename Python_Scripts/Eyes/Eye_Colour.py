import cv2
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

from sklearn.metrics import mean_squared_error
import math
import re
import string
import struct


class color:

    def __init__(self):
        self.HEX_COLOR_RE = re.compile(r'^#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$')
        self.SUPPORTED_SPECIFICATIONS = (u'html4', u'css2', u'css21', u'css3')
        self.SPECIFICATION_ERROR_TEMPLATE = u"'%%s' is not a supported specification for color name lookups; \
    supported specifications are: %s." % (u', '.join(self.SUPPORTED_SPECIFICATIONS))
        self.HTML4_NAMES_TO_HEX = {
            u'aqua': u'#00ffff',
            u'black': u'#000000',
            u'blue': u'#0000ff',
            u'fuchsia': u'#ff00ff',
            u'green': u'#008000',
            u'gray': u'#808080',
            u'lime': u'#00ff00',
            u'maroon': u'#800000',
            u'navy': u'#000080',
            u'olive': u'#808000',
            u'purple': u'#800080',
            u'red': u'#ff0000',
            u'silver': u'#c0c0c0',
            u'teal': u'#008080',
            u'white': u'#ffffff',
            u'yellow': u'#ffff00',
        }
        self.HTML4_NAMES_TO_HEX = {
            u'aqua': u'#00ffff',
            u'black': u'#000000',
            u'blue': u'#0000ff',
            u'fuchsia': u'#ff00ff',
            u'green': u'#008000',
            u'gray': u'#808080',
            u'lime': u'#00ff00',
            u'maroon': u'#800000',
            u'navy': u'#000080',
            u'olive': u'#808000',
            u'purple': u'#800080',
            u'red': u'#ff0000',
            u'silver': u'#c0c0c0',
            u'teal': u'#008080',
            u'white': u'#ffffff',
            u'yellow': u'#ffff00',
        }
        self.CSS2_NAMES_TO_HEX = self.HTML4_NAMES_TO_HEX
        self.CSS21_NAMES_TO_HEX = dict(self.HTML4_NAMES_TO_HEX, orange=u'#ffa500')
        self.CSS3_NAMES_TO_HEX = {
            u'aliceblue': u'#f0f8ff',
            u'antiquewhite': u'#faebd7',
            u'aqua': u'#00ffff',
            u'aquamarine': u'#7fffd4',
            u'azure': u'#f0ffff',
            u'beige': u'#f5f5dc',
            u'bisque': u'#ffe4c4',
            u'black': u'#000000',
            u'blanchedalmond': u'#ffebcd',
            u'blue': u'#0000ff',
            u'blueviolet': u'#8a2be2',
            u'brown': u'#a52a2a',
            u'burlywood': u'#deb887',
            u'cadetblue': u'#5f9ea0',
            u'chartreuse': u'#7fff00',
            u'chocolate': u'#d2691e',
            u'coral': u'#ff7f50',
            u'cornflowerblue': u'#6495ed',
            u'cornsilk': u'#fff8dc',
            u'crimson': u'#dc143c',
            u'cyan': u'#00ffff',
            u'darkblue': u'#00008b',
            u'darkcyan': u'#008b8b',
            u'darkgoldenrod': u'#b8860b',
            u'darkgray': u'#a9a9a9',
            u'darkgrey': u'#a9a9a9',
            u'darkgreen': u'#006400',
            u'darkkhaki': u'#bdb76b',
            u'darkmagenta': u'#8b008b',
            u'darkolivegreen': u'#556b2f',
            u'darkorange': u'#ff8c00',
            u'darkorchid': u'#9932cc',
            u'darkred': u'#8b0000',
            u'darksalmon': u'#e9967a',
            u'darkseagreen': u'#8fbc8f',
            u'darkslateblue': u'#483d8b',
            u'darkslategray': u'#2f4f4f',
            u'darkslategrey': u'#2f4f4f',
            u'darkturquoise': u'#00ced1',
            u'darkviolet': u'#9400d3',
            u'deeppink': u'#ff1493',
            u'deepskyblue': u'#00bfff',
            u'dimgray': u'#696969',
            u'dimgrey': u'#696969',
            u'dodgerblue': u'#1e90ff',
            u'firebrick': u'#b22222',
            u'floralwhite': u'#fffaf0',
            u'forestgreen': u'#228b22',
            u'fuchsia': u'#ff00ff',
            u'gainsboro': u'#dcdcdc',
            u'ghostwhite': u'#f8f8ff',
            u'gold': u'#ffd700',
            u'goldenrod': u'#daa520',
            u'gray': u'#808080',
            u'grey': u'#808080',
            u'green': u'#008000',
            u'greenyellow': u'#adff2f',
            u'honeydew': u'#f0fff0',
            u'hotpink': u'#ff69b4',
            u'indianred': u'#cd5c5c',
            u'indigo': u'#4b0082',
            u'ivory': u'#fffff0',
            u'khaki': u'#f0e68c',
            u'lavender': u'#e6e6fa',
            u'lavenderblush': u'#fff0f5',
            u'lawngreen': u'#7cfc00',
            u'lemonchiffon': u'#fffacd',
            u'lightblue': u'#add8e6',
            u'lightcoral': u'#f08080',
            u'lightcyan': u'#e0ffff',
            u'lightgoldenrodyellow': u'#fafad2',
            u'lightgray': u'#d3d3d3',
            u'lightgrey': u'#d3d3d3',
            u'lightgreen': u'#90ee90',
            u'lightpink': u'#ffb6c1',
            u'lightsalmon': u'#ffa07a',
            u'lightseagreen': u'#20b2aa',
            u'lightskyblue': u'#87cefa',
            u'lightslategray': u'#778899',
            u'lightslategrey': u'#778899',
            u'albastru aquamarin, albastru': u'#b0c4de',
            u'lightyellow': u'#ffffe0',
            u'lime': u'#00ff00',
            u'limegreen': u'#32cd32',
            u'linen': u'#faf0e6',
            u'magenta': u'#ff00ff',
            u'maroon': u'#800000',
            u'mediumaquamarine': u'#66cdaa',
            u'mediumblue': u'#0000cd',
            u'mediumorchid': u'#ba55d3',
            u'mediumpurple': u'#9370db',
            u'mediumseagreen': u'#3cb371',
            u'mediumslateblue': u'#7b68ee',
            u'mediumspringgreen': u'#00fa9a',
            u'mediumturquoise': u'#48d1cc',
            u'mediumvioletred': u'#c71585',
            u'midnightblue': u'#191970',
            u'mintcream': u'#f5fffa',
            u'mistyrose': u'#ffe4e1',
            u'moccasin': u'#ffe4b5',
            u'navajowhite': u'#ffdead',
            u'nantucketsands': u'#b4a89d',
            u'navy': u'#000080',
            u'oldlace': u'#fdf5e6',
            u'olive': u'#808000',
            u'olivedrab': u'#6b8e23',
            u'orange': u'#ffa500',
            u'orangered': u'#ff4500',
            u'orchid': u'#da70d6',
            u'palegoldenrod': u'#eee8aa',
            u'palegreen': u'#98fb98',
            u'paleturquoise': u'#afeeee',
            u'palevioletred': u'#db7093',
            u'papayawhip': u'#ffefd5',
            u'peachpuff': u'#ffdab9',
            u'peru': u'#cd853f',
            u'pink': u'#ffc0cb',
            u'plum': u'#dda0dd',
            # u'pomegranate': u'#000000',
            u'powderblue': u'#b0e0e6',
            u'purple': u'#800080',
            u'red': u'#ff0000',
            u'rosybrown': u'#bc8f8f',
            u'royalblue': u'#4169e1',
            u'saddlebrown': u'#8b4513',
            u'salmon': u'#fa8072',
            u'sandybrown': u'#f4a460',
            u'seagreen': u'#2e8b57',
            u'seashell': u'#fff5ee',
            u'sienna': u'#a0522d',
            u'silver': u'#c0c0c0',
            u'skyblue': u'#87ceeb',
            u'slateblue': u'#6a5acd',
            u'slategray': u'#708090',
            u'slategrey': u'#708090',
            u'snow': u'#fffafa',
            u'springgreen': u'#00ff7f',
            u'sweetsparrow': u'#a79369',
            u'steelblue': u'#4682b4',
            u'tan': u'#d2b48c',
            u'teal': u'#008080',
            u'thistle': u'#d8bfd8',
            u'tomato': u'#ff6347',
            u'turquoise': u'#40e0d0',
            u'violet': u'#ee82ee',
            u'wheat': u'#f5deb3',
            u'white': u'#ffffff',
            u'whitesmoke': u'#f5f5f5',
            u'yellow': u'#ffff00',
            u'yellowgreen': u'#9acd32',
            u'paleBrown': u'#947651',
            u'appaloosaspots': u'#876d52',
            u'grullo': u'#ab9b84',
            u'hazymauve': u'#cac6d0',
            u'americansilver': u'#d0cfcd',
            u'philippineSilver': u'#b9b7b7',
            u'goldensummer': u'#826b45',
            u'feathergrey': u'#b7ae9c',
            u'hotcocoa': u'#816356',
            u'winecellar': u'#6f403c',
            u'Purplemuave': u'#9a8a94',
            u'Axis': u'#b8b6ca',
            u'Sndyrich': u'#a28e77',
            u'Beaver': u'#a18a69'

        }
        self.HTML4_HEX_TO_NAMES = self._reversedict(self.HTML4_NAMES_TO_HEX)

        self.CSS2_HEX_TO_NAMES = self.HTML4_HEX_TO_NAMES

        self.CSS21_HEX_TO_NAMES = self._reversedict(self.CSS21_NAMES_TO_HEX)

        self.CSS3_HEX_TO_NAMES = self._reversedict(self.CSS3_NAMES_TO_HEX)

    # Python 2's unichr() is Python 3's chr().
    try:
        unichr
    except NameError:
        unichr = chr

    # Python 2's unicode is Python 3's str.
    try:
        unicode
    except NameError:
        unicode = str

    def _reversedict(self, d):
        """
        Internal helper for generating reverse mappings; given a
        dictionary, returns a new dictionary with keys and values swapped.
        """
        return dict(zip(d.values(), d.keys()))

    # Mappings of color names to normalized hexadecimal color values.
    #################################################################

    # The HTML 4 named colors.
    #
    # The canonical source for these color definitions is the HTML 4
    # specification:
    #
    # http://www.w3.org/TR/html401/types.html#h-6.5
    #
    # The file tests/definitions.py in the source distribution of this
    # module downloads a copy of the HTML 4 standard and parses out the
    # color names to ensure the values below are correct.

    # CSS 2 used the same list as HTML 4.

    # CSS 2.1 added orange.

    # Mappings of normalized hexadecimal color values to color names.
    #################################################################

    # Aliases of the above mappings, for backwards compatibility.
    #################################################################

    # Normalization functions.
    #################################################################

    def normalize_hex(self, hex_value):
        """
        Normalize a hexadecimal color value to 6 digits, lowercase.
        """
        match = self.HEX_COLOR_RE.match(hex_value)
        if match is None:
            raise ValueError(
                u"'%s' is not a valid hexadecimal color value." % hex_value
            )
        hex_digits = match.group(1)
        if len(hex_digits) == 3:
            hex_digits = u''.join(2 * s for s in hex_digits)
        return u'#%s' % hex_digits.lower()

    def _normalize_integer_rgb(self, value):
        """
        Internal normalization function for clipping integer values into
        the permitted range (0-255, inclusive).
        """
        return 0 if value < 0 \
            else 255 if value > 255 \
            else value

    def normalize_integer_triplet(self, rgb_triplet):
        """
        Normalize an integer ``rgb()`` triplet so that all values are
        within the range 0-255 inclusive.
        """
        return tuple(self._normalize_integer_rgb(value) for value in rgb_triplet)

    def _normalize_percent_rgb(self, value):
        """
        Internal normalization function for clipping percent values into
        the permitted range (0%-100%, inclusive).
        """
        percent = value.split(u'%')[0]
        percent = float(percent) if u'.' in percent else int(percent)

        return u'0%' if percent < 0 \
            else u'100%' if percent > 100 \
            else u'%s%%' % percent

    def normalize_percent_triplet(self, rgb_triplet):
        """
        Normalize a percentage ``rgb()`` triplet so that all values are
        within the range 0%-100% inclusive.
        """
        return tuple(self._normalize_percent_rgb(value) for value in rgb_triplet)

    # Conversions from color names to various formats.
    #################################################################

    def name_to_hex(self, name, spec=u'css3'):
        """
        Convert a color name to a normalized hexadecimal color value.
        The optional keyword argument ``spec`` determines which
        specification's list of color names will be used; valid values are
        ``html4``, ``css2``, ``css21`` and ``css3``, and the default is
        ``css3``.
        When no color of that name exists in the given specification,
        ``ValueError`` is raised.
        """
        if spec not in self.SUPPORTED_SPECIFICATIONS:
            raise ValueError(self.SPECIFICATION_ERROR_TEMPLATE % spec)
        normalized = name.lower()
        hex_value = {u'css2': self.CSS2_NAMES_TO_HEX,
                     u'css21': self.CSS21_NAMES_TO_HEX,
                     u'css3': self.CSS3_NAMES_TO_HEX,
                     u'html4': self.HTML4_NAMES_TO_HEX}[spec].get(normalized)
        if hex_value is None:
            raise ValueError(
                u"'%s' is not defined as a named color in %s." % (name, spec)
            )
        return hex_value

    def name_to_rgb(self, name, spec=u'css3'):
        """
        Convert a color name to a 3-tuple of integers suitable for use in
        an ``rgb()`` triplet specifying that color.
        """
        return self.hex_to_rgb(self.name_to_hex(name, spec=spec))

    def name_to_rgb_percent(self, name, spec=u'css3'):
        """
        Convert a color name to a 3-tuple of percentages suitable for use
        in an ``rgb()`` triplet specifying that color.
        """
        return self.rgb_to_rgb_percent(self.name_to_rgb(name, spec=spec))

    # Conversions from hexadecimal color values to various formats.
    #################################################################

    def hex_to_name(self, hex_value, spec=u'css3'):
        """
        Convert a hexadecimal color value to its corresponding normalized
        color name, if any such name exists.
        The optional keyword argument ``spec`` determines which
        specification's list of color names will be used; valid values are
        ``html4``, ``css2``, ``css21`` and ``css3``, and the default is
        ``css3``.
        When no color name for the value is found in the given
        specification, ``ValueError`` is raised.
        """
        if spec not in self.SUPPORTED_SPECIFICATIONS:
            raise ValueError(self.SPECIFICATION_ERROR_TEMPLATE % spec)
        normalized = self.normalize_hex(hex_value)
        name = {u'css2': self.CSS2_HEX_TO_NAMES,
                u'css21': self.CSS21_HEX_TO_NAMES,
                u'css3': self.CSS3_HEX_TO_NAMES,
                u'html4': self.HTML4_HEX_TO_NAMES}[spec].get(normalized)
        if name is None:
            raise ValueError(
                u"'%s' has no defined color name in %s." % (hex_value, spec)
            )
        return name

    def hex_to_rgb(self, hex_value):
        """
        Convert a hexadecimal color value to a 3-tuple of integers
        suitable for use in an ``rgb()`` triplet specifying that color.
        """
        hex_value = self.normalize_hex(hex_value)
        hex_value = int(hex_value[1:], 16)
        return (hex_value >> 16,
                hex_value >> 8 & 0xff,
                hex_value & 0xff)

    def hex_to_rgb_percent(self, hex_value):
        """
        Convert a hexadecimal color value to a 3-tuple of percentages
        suitable for use in an ``rgb()`` triplet representing that color.
        """
        return self.rgb_to_rgb_percent(self.hex_to_rgb(hex_value))

    # Conversions from  integer rgb() triplets to various formats.
    #################################################################

    def rgb_to_name(self, rgb_triplet, spec=u'css3'):
        """
        Convert a 3-tuple of integers, suitable for use in an ``rgb()``
        color triplet, to its corresponding normalized color name, if any
        such name exists.
        The optional keyword argument ``spec`` determines which
        specification's list of color names will be used; valid values are
        ``html4``, ``css2``, ``css21`` and ``css3``, and the default is
        ``css3``.
        If there is no matching name, ``ValueError`` is raised.
        """
        return self.hex_to_name(
            self.rgb_to_hex(
                self.normalize_integer_triplet(rgb_triplet)),
            spec=spec)

    def rgb_to_hex(self, rgb_triplet):
        """
        Convert a 3-tuple of integers, suitable for use in an ``rgb()``
        color triplet, to a normalized hexadecimal value for that color.
        """
        return u'#%02x%02x%02x' % self.normalize_integer_triplet(rgb_triplet)

    def rgb_to_rgb_percent(self, rgb_triplet):

        specials = {255: u'100%', 128: u'50%', 64: u'25%',
                    32: u'12.5%', 16: u'6.25%', 0: u'0%'}
        return tuple(specials.get(d, u'%.02f%%' % (d / 255.0 * 100))
                     for d in self.normalize_integer_triplet(rgb_triplet))

    # Conversions from percentage rgb() triplets to various formats.
    #################################################################

    def rgb_percent_to_name(self, rgb_percent_triplet, spec=u'css3'):

        return self.rgb_to_name(
            self.rgb_percent_to_rgb(
                self.normalize_percent_triplet(
                    rgb_percent_triplet)),
            spec=spec)

    def rgb_percent_to_hex(self, rgb_percent_triplet):
        """
        Convert a 3-tuple of percentages, suitable for use in an ``rgb()``
        color triplet, to a normalized hexadecimal color value for that
        color.
        """
        return self.rgb_to_hex(
            self.rgb_percent_to_rgb(
                self.normalize_percent_triplet(rgb_percent_triplet)))

    def _percent_to_integer(self, percent):

        num = float(percent.split(u'%')[0]) / 100 * 255
        e = num - math.floor(num)
        return e < 0.5 and int(math.floor(num)) or int(math.ceil(num))

    def rgb_percent_to_rgb(self, rgb_percent_triplet):

        return tuple(map(self._percent_to_integer,
                         self.normalize_percent_triplet(rgb_percent_triplet)))

    def html5_parse_simple_color(self, input):
        if not isinstance(input, unicode) or len(input) != 7:
            raise ValueError(
                u"An HTML5 simple color must be a Unicode string "
                u"exactly seven characters long."
            )

        # 3. If the first character in input is not a U+0023 NUMBER SIGN
        #    character (#), then return an error.
        if not input.startswith('#'):
            raise ValueError(
                u"An HTML5 simple color must begin with the "
                u"character '#' (U+0023)."
            )

        # 4. If the last six characters of input are not all ASCII hex
        #    digits, then return an error.
        if not all(c in string.hexdigits for c in input[1:]):
            raise ValueError(
                u"An HTML5 simple color must contain exactly six ASCII hex digits."
            )

        result = (int(input[1:3], 16),
                  int(input[3:5], 16),
                  int(input[5:7], 16))
        return result

    def html5_serialize_simple_color(self, simple_color):
        """
        Apply the serialization algorithm for a simple color from section
        2.4.6 of HTML5.
        """
        red, green, blue = simple_color

        # 1. Let result be a string consisting of a single "#" (U+0023)
        #    character.
        result = u'#'

        result += (u"%02x" % red).lower()
        result += (u"%02x" % green).lower()
        result += (u"%02x" % blue).lower()

        # 3. Return result, which will be a valid lowercase simple color.
        return result

    def html5_parse_legacy_color(self, input):
        """
        Apply the legacy color parsing algorithm from section 2.4.6 of
        HTML5.
        """
        # 1. Let input be the string being parsed.
        if not isinstance(input, unicode):
            raise ValueError(
                u"HTML5 legacy color parsing requires a Unicode string as input."
            )

        # 2. If input is the empty string, then return an error.
        if input == "":
            raise ValueError(
                u"HTML5 legacy color parsing forbids empty string as a value."
            )

        # 3. Strip leading and trailing whitespace from input.
        input = input.strip()

        if input.lower() == u"transparent":
            raise ValueError(
                u'HTML5 legacy color parsing forbids "transparent" as a value.'
            )

        keyword_hex = self.CSS3_NAMES_TO_HEX.get(input.lower())
        if keyword_hex is not None:
            return self.html5_parse_simple_color(keyword_hex)

        if len(input) == 4 and \
                input.startswith(u'#') and \
                all(c in string.hexdigits for c in input[1:]):
            result = (int(input[1], 16) * 17,
                      int(input[2], 16) * 17,
                      int(input[3], 16) * 17)

            # 5. Return result.
            return result

        encoded_input = input.encode('utf_32_le')

        format_string = '<' + ('L' * (int(len(encoded_input) / 4)))
        codepoints = struct.unpack(format_string, encoded_input)
        input = ''.join(u'00' if c > 0xffff
                        else unichr(c)
                        for c in codepoints)

        # 8. If input is longer than 128 characters, truncate input,
        #    leaving only the first 128 characters.
        if len(input) > 128:
            input = input[:128]

        # 9. If the first character in input is a "#" (U+0023) character,
        #    remove it.
        if input.startswith(u'#'):
            input = input[1:]

        # 10. Replace any character in input that is not an ASCII hex
        #     digit with the character "0" (U+0030).
        if any(c for c in input if c not in string.hexdigits):
            input = ''.join(c if c in string.hexdigits else u'0' for c in input)

        # 11. While input's length is zero or not a multiple of three,
        #     append a "0" (U+0030) character to input.
        while (len(input) == 0) or (len(input) % 3 != 0):
            input += u'0'

        # 12. Split input into three strings of equal length, to obtain
        #     three components. Let length be the length of those
        #     components (one third the length of input).
        length = int(len(input) / 3)
        red = input[:length]
        green = input[length:length * 2]
        blue = input[length * 2:]

        # 13. If length is greater than 8, then remove the leading
        #     length-8 characters in each component, and let length be 8.
        if length > 8:
            red, green, blue = (red[length - 8:],
                                green[length - 8:],
                                blue[length - 8:])
            length = 8

        # 14. While length is greater than two and the first character in
        #     each component is a "0" (U+0030) character, remove that
        #     character and reduce length by one.
        while (length > 2) and (red[0] == u'0' and
                                green[0] == u'0' and
                                blue[0] == u'0'):
            red, green, blue = (red[1:],
                                green[1:],
                                blue[1:])
            length -= 1

        # 15. If length is still greater than two, truncate each
        #     component, leaving only the first two characters in each.
        if length > 2:
            red, green, blue = (red[:2],
                                green[:2],
                                blue[:2])

        result = (int(red, 16),
                  int(green, 16),
                  int(blue, 16))

        # 20. Return result.
        return result


class eye_col:
    def __init__(self):
        self.cc = color()
        pass

    def get_image(self, image_path):
        image = cv2.imread(image_path)
        # cv2 by default converts into the bgr form so we are converting into rgb
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def interpolating_image(self, image):
        modified_image = cv2.resize(image, (600, 400), interpolation=cv2.INTER_AREA)
        modified_image = modified_image.reshape(modified_image.shape[0] * modified_image.shape[1], 3)
        return modified_image

    def KModel(self, image):
        # we sett the max value of 255 in clusters
        clf = KMeans(n_clusters=4)
        labels = clf.fit_predict(image)
        return labels, clf

    def RGB2HEX(self, color):
        return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

    def hex2name(self, c):
        h_color = '#{:02x}{:02x}{:02x}'.format(int(c[0]), int(c[1]), int(c[2]))
        try:
            nm = self.cc.hex_to_name(h_color, spec=u'css3')
        except ValueError as v_error:
            # print("{}".format(v_error))
            rms_lst = []
            for img_clr, img_hex in self.cc.CSS3_NAMES_TO_HEX.items():
                cur_clr = self.cc.hex_to_rgb(img_hex)
                rmse = np.sqrt(mean_squared_error(c, cur_clr))
                rms_lst.append(rmse)

            closest_color = rms_lst.index(min(rms_lst))

            nm = list(self.cc.CSS3_NAMES_TO_HEX.items())[closest_color][0]
        return nm

    # here passing the model and the labels which are predicted from the model
    # def color_distribution(self, counts, clf):
    #     # counts = Counter(labels)
    #     colors = {}
    #     center_colors = clf.cluster_centers_
    #     # We get ordered colors by iterating through the keys
    #     ordered_colors = [center_colors[i] for i in counts.keys()]
    #     # We got the different range of colors
    #     hex_colors = [self.RGB2HEX(ordered_colors[i]) for i in counts.keys()]
    #     rgb_colors = [ordered_colors[i] for i in counts.keys()]
    #     lbl_color = [self.hex2name(ordered_colors[i]) for i in counts.keys()]
    #
    #     # plot the pie chart of those colors better for visualizing
    #     plt.pie(counts.values(), labels=lbl_color, colors=hex_colors, autopct='%.0f%%',
    #             textprops={'color': 'white', 'fontweight': 'bold'})

    def final(self, img):
        image1 = self.get_image(img)
        image = self.interpolating_image(image1)
        model = []
        values = []
        new = {}

        for i in range(1):
            labels, clf = self.KModel(image)
            if i == 0:
                model.append(clf)

            values.append(labels)

        zero = 0
        one = 0
        two = 0
        three = 0

        for i in range(1):
            zero += np.count_nonzero(values[i] == 0)
            one += np.count_nonzero(values[i] == 1)
            two += np.count_nonzero(values[i] == 2)
            three += np.count_nonzero(values[i] == 3)

        new[0] = int(zero / 4)
        new[1] = int(one / 4)
        new[2] = int(two / 4)
        new[3] = int(three / 4)
        return new, model

    def run(self, img):
        out = self.final(img)
        colors = {}
        counts = out[0]
        clf = out[1][0]
        center_colors = clf.cluster_centers_
        # We get ordered colors by iterating through the keys
        ordered_colors = [center_colors[i] for i in counts.keys()]
        # We got the different range of colors
        hex_colors = [self.RGB2HEX(ordered_colors[i]) for i in counts.keys()]
        rgb_colors = [ordered_colors[i] for i in counts.keys()]
        lbl_color = [self.hex2name(ordered_colors[i]) for i in counts.keys()]
        lst = list(counts.values())

        # plot the pie chart of those colors better for visualizing
        # plt.pie(counts.values(), labels=lbl_color, colors=hex_colors, autopct='%.0f%%',
        #         textprops={'color': 'white', 'fontweight': 'bold'})
        # plt.savefig(chartname, dpi=1000, bbox_inches='tight')

        return lbl_color, lst, hex_colors
