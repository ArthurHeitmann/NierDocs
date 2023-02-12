# This is now deprecated. Use [F-SERVO](https://github.com/ArthurHeitmann/F-SERVO) instead.

&nbsp;

&nbsp;

# PAK, YAX & XML Tools

XML scripting files for Nier:Automata.

#### Files covered by these tools

PAK files: Container for YAX files.  
YAX files: Binary xml files, that don't support attributes. I call them "Yet Another Xml encoding" (there are now 3 different xml encodings used in this game).  
XML files: Decoded YAX files, with some helpful annotations in the attributes (translations, unhashed strings).

## Usage

All tools can be used by either dragging files/folder onto the .py files or from the command line.

#### PAK

Drag pak files onto `pakExtractor.py` to unpack to `./pakExtracted/<pakName>`.  
Or drag a folder onto `allPakUnpacker.py` to unpack all pak files recursively in the folder.

To repack, drag a folder from `./pakExtracted/<pakName>` onto `pakPacker.py`.

#### YAX/XML

Drag the files onto either `yaxToXml.py` or `xmlToYax.py`.

##### Notes:
If an XML tag is `<UNKNOWN>` and has an `id="..."` attribute, do not remove it.  
All Japanese texts have a translation in the `eng="..."` attribute.  
Some tags (like `<code>`) only have a hex number as a value. The unhashed string, if available, is in the `str="..."` attribute. During XML to YAX conversion, only the number hash is used and the string is ignored.

## Technical Stuff

Here are binary template for for [PAK files](../../BinaryTemplates/NierA_PAK.bt) and [YAX files](../../BinaryTemplates/NierA_YAX.bt).

#### PAK

Is a container for YAX files. If the files are > 1024 bytes, they are compressed. In the header, each file has a `type` int between 1 and 6, what exactly it means is unknown.

#### YAX

A yax files is a list of xml nodes with an indentation, tag name hash and a string value. Child relations are based on the indentation. There is no official lookup table to convert the hash to the tag name. Instead I collected all strings from the games exe, and monitored all hash function calls in the exe to generate a lookup table. This is only needed for YAX to XML. For XML to YAX, the tag name is just crc32 hashed. For cases where the hash cannot be found, the tag hash is stored in the `id="..."` attribute with an UNKNOWN tag name.
