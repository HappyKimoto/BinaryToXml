import os
import struct
from lxml import etree
import datetime

#  | Character | Byte order             | Size     | Alignment | 
#  | --------- | ---------------------- | -------- | --------- | 
#  | @         | native                 | native   | native    | 
#  | =         | native                 | standard | none      | 
#  | <         | little-endian          | standard | none      | &lt;
#  | >         | big-endian             | standard | none      | &gt;
#  | !         | network (= big-endian) | standard | none      |

# | Format | C Type             | Python type       | Standard size | Notes    | 
# | ------ | ------------------ | ----------------- | ------------- | -------- | 
# | x      | pad byte           | no value          |               |          | 
# | c      | char               | bytes of length 1 |             1 |          | 
# | b      | signed char        | integer           |             1 | (1), (2) | 
# | ?      | _Bool              | bool              |             1 | (1)      | 
# | h      | short              | integer           |             2 | (2)      | 
# | H      | unsigned short     | integer           |             2 | (2)      | 
# | i      | int                | integer           |             4 | (2)      | 
# | I      | unsigned int       | integer           |             4 | (2)      | 
# | l      | long               | integer           |             4 | (2)      | 
# | L      | unsigned long      | integer           |             4 | (2)      | 
# | q      | long long          | integer           |             8 | (2)      | 
# | Q      | unsigned long long | integer           |             8 | (2)      | 
# | n      | ssize_t            | integer           |               | (3)      | 
# | N      | size_t             | integer           |               | (3)      | 
# | e      | (6)                | float             |             2 | (4)      | 
# | f      | float              | float             |             4 | (4)      | 
# | d      | double             | float             |             8 | (4)      | 
# | s      | char[]             | bytes             |               |          | 
# | p      | char[]             | bytes             |               |          | 
# | P      | void*              | integer           |               | (5)      | 


class CustomFuncs:
    @staticmethod
    def systemtime_16_le(bytes16):
        """
        typedef struct _SYSTEMTIME {
          WORD wYear;
          WORD wMonth;
          WORD wDayOfWeek;
          WORD wDay;
          WORD wHour;
          WORD wMinute;
          WORD wSecond;
          WORD wMilliseconds;
        } SYSTEMTIME, *PSYSTEMTIME, *LPSYSTEMTIME;
        """
        n = struct.unpack('<8H', bytes16)
        d = datetime.datetime(n[0], n[1], n[3], n[4], n[5], n[6], n[7] * 1000)
        return d.isoformat()

    @staticmethod
    def hex_str(bytes0):
        """ convert unknown length of bytes to hex string. """
        return bytes0.hex()

class ByteSnipper:
    def __init__(self, fp_bin):
        self.f = open(fp_bin, 'rb')

    def get_bytes(self, start_offset, byte_size):
        self.f.seek(start_offset, 0)
        return self.f.read(byte_size)

class TreeFuncs:
    @staticmethod
    def get_tree(fp):
        if os.path.isfile(fp):
            with open(fp, 'rb') as f:
                try:
                    tree = etree.parse(f)
                except Exception as e:
                    print(f'Error: Failed to open the input XML file! fp={fp}')
                    print(e)
                    quit()
                else:
                    return tree
        else:
            print(f'fp="{fp}" is not a file!')
            quit()

    @staticmethod
    def write_tree(fp, tree):
        with open(fp, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)

def parse_to_xml(fp_bin, fp_xml):
    # parse binary data
    byte_snipper = ByteSnipper(fp_bin)
    # parse xml settings
    tree_root = TreeFuncs.get_tree(fp_xml)
    # loop through <Pattern> element
    for pattern in tree_root.xpath('/Patterns/Pattern'):
        data_result = "Not Set Error"
        # get start offset in integer
        try:
            start_offset_int = int(pattern.get('start_offset'), 0)
        except Exception as e:
            data_result = f"{e.__class__.__name__}: start_offset"
        else:
            # Unpack Format -------------------
            if pattern.get('unpack_format') is not None:
                data_format = pattern.get('unpack_format')
                print(f'data_format={data_format}')
                # Validate data length
                try:
                    data_length = struct.calcsize(data_format)
                except Exception as e:
                    data_result = f'{e.__class__.__name__}: data_length'
                else:
                    data_bytes = byte_snipper.get_bytes(start_offset_int, data_length)
                    # if unpack_index is not specified, return tuple.
                    if pattern.get('unpack_index') is None:
                        data_result = str(struct.unpack(data_format, data_bytes))
                    else:
                        # Validate unpack index type
                        try:
                            unpack_index = int(pattern.get('unpack_index'))
                        except Exception as e:
                            data_result = f'{e.__class__.__name__}: unpack_index'
                        else:
                            # Validate unpack index range
                            try:
                                data_result = str(struct.unpack(data_format, data_bytes)[unpack_index])
                            except Exception as e:
                                data_result = f"{e.__class__.__qualname__}: unpack_index"
            # Code Page -----------------------
            elif pattern.get('code_page') is not None:
                decode_error = pattern.get('decode_error') if pattern.get('decode_error') is not None else 'replace'
                data_length = int(pattern.get('length'), 0)
                data_bytes = byte_snipper.get_bytes(start_offset_int, data_length)
                data_result = data_bytes.decode(pattern.get('code_page'), decode_error).rstrip(' \0\r\n\t')
            # Function -------------------------
            elif pattern.get('function') is not None:
                data_length = int(pattern.get('length'), 0)
                custom_fnc = getattr(CustomFuncs, pattern.get('function'))
                data_bytes = byte_snipper.get_bytes(start_offset_int, data_length)
                data_result = custom_fnc(data_bytes)
            # Nested -----------------------
            elif pattern.get('nested') is not None:
                pass
        # set XML element value
        finally:
            pattern.text = data_result
    return tree_root

def test_from_cmd():
    fp_data = 'bintoxml_data.dat'
    fp_xml_in = 'bintoxml_input.xml'
    fp_xml_out = 'bintoxml_output.xml'
    tree_root = parse_to_xml(fp_data, fp_xml_in)
    TreeFuncs.write_tree(fp_xml_out, tree_root)

if __name__ == "__main__":
    test_from_cmd()
