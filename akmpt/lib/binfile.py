#!/usr/bin/python
""" binary file read/writing operations """
import struct
from struct import *


class UnpackingError(BaseException):
    def __init__(self, binfile, str_err):
        super(UnpackingError, self).__init__('Error unpacking {}: {}'.format(binfile.filename, str_err))


class PackingError(BaseException):
    def __init__(self, binfile, str_err):
        super(PackingError, self).__init__('Error packing {}: {}'.format(binfile.filename, str_err))


# -------------------------------------------------------------------------------
class BinFile:
    """ BinFile class: for packing and unpacking binary files"""
    STRIDE_MAP = {'f':4, 'I':4, 'i':4, 'H':2, 'h':2, 'B':2, 'b':2}

    def __init__(self, filename, mode='r', bom='>'):
        """
        filename:   name of file to read/write
        bom:    byte order mark (>|<) Big endian or little endian
        mode:   (r|w)
        len:    initial length of file (write only)
        """
        self.beginOffset = self.offset = 0
        self.filename = filename
        self.names_offset = float('inf')
        self.stack = []  # used for tracking depth in files
        self.references = {}  # used for forward references in relation to start
        self.bom = bom  # byte order mark > | <
        self.nameRefMap = {}  # for packing name references
        self.names_packed = False
        self.lenMap = {}  # used for tracking length of files
        self.c_length = None  # for tracking current length

        self.isWriteMode = (mode == 'w')
        if not self.isWriteMode:
            with open(filename, "rb") as file:
                self.file = file.read()
        else:
            self.file = bytearray()
        self.start()

    def commit_write(self):
        """ writes the file """
        # check references
        if len(self.stack) > 1:
            raise PackingError(self, 'Incorrect stack, {} items still on'.format(len(self.stack) - 1))
        if not self.names_packed:
            self.pack_names()
        # write
        # print('Length of file is {}'.format(len(self.file)))
        with open(self.filename, "wb") as f:
            f.write(self.file)
        return True

    def is_aligned(self, alignment=0x20):
        return (self.offset - self.beginOffset) % alignment == 0

    def align(self, alignment=0x20):
        """ Aligns to the alignment of the current file """
        past_align = self.offset % alignment
        if past_align:
            self.advance(alignment - past_align)

    def align_to_parent(self, alignment=0x20):
        """ Aligns to alignment, with respect to parent"""
        parent_offset = self.stack[-2]  # possible error here
        past_align = (self.offset - parent_offset) % alignment
        if past_align:
            self.advance(alignment - past_align)

    # start / marks offset which pointers are based
    def start(self):
        """ Starts reading a file, remembering the offset """
        self.beginOffset = self.offset
        self.stack.append(self.offset)
        self.refMarker = []
        self.c_length = None  # reset
        self.references[self.beginOffset] = self.refMarker
        return self.offset

    def align_and_end(self, alignment=0x20):
        self.align(alignment)
        self.end()

    #  end / pops last start offset off stack
    def end(self):
        # write file length?
        if self.isWriteMode:
            offset = self.lenMap.get(self.beginOffset)
            if offset:
                self.write_offset("I", offset, self.offset - self.beginOffset)
            self.offset = len(self.file)
        else:  # read mode
            if self.c_length:
                current_read_len = self.offset - self.beginOffset
                if self.c_length < current_read_len:
                    raise UnpackingError(self, 'offset is outside current section')
        self.stack.pop()
        self.beginOffset = self.stack[-1]
        if self.beginOffset in self.lenMap:
            self.c_length = self.lenMap[self.beginOffset]
        else:
            self.c_length = None  # possibly search stack for a length?
        self.refMarker = self.references[self.beginOffset]
        return self.offset

    def mark_len(self):
        """ Marks the current offset as length of file,
            which gets filled in by binfile.end in write mode
        """
        self.lenMap[self.beginOffset] = self.offset
        self.advance(4)

    def read_len(self):
        [self.c_length] = self.read('I', 4)
        self.lenMap[self.beginOffset] = self.c_length
        return self.c_length

    # Writing back ptrs, use mark and createref together, write mode
    def mark(self, num_refs=1):
        """ Marks the current offset(s) relative to start as storage for ptrs,
            advancing the file offset
            Use in write mode with createRef
        """
        li = self.refMarker
        offset = self.offset
        for i in range(num_refs):
            li.append(offset)
            # self.linked_offsets.append(offset)      #- debug
            offset += 4
        self.advance(num_refs * 4)

    def unmark(self, ref_index=0, pop=True):
        """Retrieves marked offset"""
        try:
            if pop:
                return self.refMarker.pop(ref_index)
            else:
                return self.refMarker[ref_index]
        except IndexError:
            raise PackingError(self, "Marked index from {} at {} does not exist!".format(self.beginOffset, ref_index))

    def create_ref_from_stored(self, ref_index=0, pop=True, start_ref=None):
        """ Creates reference to the current file offset
            in relation to the stored offset (not start!)
        """
        refMarker = self.refMarker if start_ref is None else self.references[start_ref]
        try:
            if pop:
                marked_offset = refMarker.pop(ref_index)
            else:
                marked_offset = refMarker[ref_index]
            self.write_offset("I", marked_offset, self.offset - marked_offset)
            return marked_offset
        except IndexError:
            raise PackingError(self, "Marked index from {} at {} does not exist!".format(self.beginOffset, ref_index))

    def create_ref(self, ref_index=0, pop=True):
        """
         Creates a reference to the current file offset
         using the reference marked at refIndex relative to start
         pops and returns the marked offset
        """
        try:
            if pop:
                marked_offset = self.refMarker.pop(ref_index)
            else:
                marked_offset = self.refMarker[ref_index]
            self.write_offset("I", marked_offset, self.offset - self.beginOffset)
            return marked_offset
        except IndexError:
            raise PackingError(self, "Marked index from {} at {} does not exist!".format(self.beginOffset, ref_index))

    def create_parent_ref(self, ref_index=0, pop=True):
        """ Creates a reference from parent marked offset"""
        return self.create_ref_from(self.get_parent_offset(), ref_index, pop)

    def create_ref_from(self, start_ref, index=0, pop=True):
        """ Creates ref by getting marked offset, indexing from startRef, at the index """
        try:
            refs = self.references[start_ref]
            if pop:
                marked_offset = refs.pop(index)
            else:
                marked_offset = refs[index]
            self.write_offset("I", marked_offset, self.offset - start_ref)
            return marked_offset
        except IndexError:
            raise PackingError(self, "Marked index from {} at {} does not exist!".format(start_ref, index))

    # Storing and recalling forward pointers - read mode
    def push_current_offset(self):
        """ pushes current offset to come back to with recall in ref from start"""
        offset = self.offset - self.beginOffset
        self.refMarker.append(offset)

    def bl_unpack(self, unpack_fptr, from_start=True):
        """reads offset and unpacks object """
        offset = self.offset
        [off] = self.read("I", 4)
        self.offset = self.beginOffset + off if from_start else offset + off
        result = unpack_fptr(self)
        self.offset = offset + 4
        return result

    def store(self, num_refs=1):
        """ Reads and stores a pointer relative to start
            Use in read mode with recallAndPop
        """
        refs = self.read("I" * num_refs, num_refs * 4)
        ret = len(self.refMarker)
        self.refMarker.extend(list(refs))
        return ret

    def recall(self, index=0, pop=True):
        """
            Recalls a reference, advancing to it
            returns the reference offset relative to start
        """
        try:
            if pop:
                offset = self.refMarker.pop(index)
            else:
                offset = self.refMarker[index]
            self.offset = offset + self.beginOffset
            return offset
        except IndexError:
            raise UnpackingError(self, "Stored index from {} at {} does not exist!".format(self.beginOffset, index))

    def recall_parent(self, index=0, pop=True):
        """ Recalls reference from parent
            returns offset in relation to current start
        """
        return self.recall_offset(self.get_parent_offset(), index, pop)

    def recall_offset(self, start_offset, index=0, pop=True):
        """ recalls reference at specific offset """
        # possible error if out of range startoffset or index
        try:
            refs = self.references[start_offset]
            if pop:
                offset = refs.pop(index)
            else:
                offset = refs[index]
            self.offset = offset + start_offset
            return offset
        except IndexError:
            raise UnpackingError(self, "Stored index from {} at {} does not exist!".format(start_offset, index))

    def recall_all(self):
        """ retrieves all refs at current start, removing them """
        refs = self.refMarker
        self.references[self.beginOffset] = self.refMarker = []
        return refs

    # advance
    def advance(self, step):
        """ advances offset pointer, possibly padding with 0's in write mode """
        # self.linked_offsets.extend([i + self.offset for i in range(step)])  #- debug
        self.offset += step
        if self.isWriteMode:
            m = self.offset - len(self.file)
            if m > 0:
                self.file.extend(b'\0' * m)
        else:  # read mode
            if self.c_length and self.offset - self.beginOffset > self.c_length:
                raise UnpackingError(self, 'offset outside of section')

    def advance_and_end(self, length):
        self.advance(length - (self.offset - self.beginOffset))
        self.end()

    def get_parent_offset(self):
        """ Gets the parent offset off the stack"""
        length = len(self.stack)
        if length > 1:
            return self.stack[length - 2]
        else:
            return 0

    # get outer (file/container) offset
    def get_outer_offset(self):
        """ Gets the negative offset to the outer file in relation to current start"""
        length = len(self.stack)
        if length > 1:
            return self.stack[length - 2] - self.beginOffset
        else:
            return 0

    # Reading / unpacking
    def read_magic(self, advance=True):
        """ reads the magic from this file, optionally advancing """
        magic = unpack_from(self.bom + "4s", self.file, self.offset)
        if advance:
            self.advance(4)
        return magic[0].decode()

    def read(self, fmt, length):
        read = unpack_from(self.bom + fmt, self.file, self.offset)
        self.advance(length)
        return read

    def read_matrix(self, width, height, fmt='f'):
        row_fmt = str(width) + fmt
        stride = self.STRIDE_MAP[fmt] * width
        matrix = []
        for i in range(height):
            matrix.append(self.read(row_fmt, stride))
        return matrix

    def read_offset(self, fmt, offset):  # len not needed
        return unpack_from(self.bom + fmt, self.file, offset)

    def read_remaining(self, filelen=None):
        """ Reads and returns remaining data as bytes """
        if not filelen:
            filelen = self.lenMap[self.beginOffset]
        end = self.beginOffset + filelen
        slice = self.file[self.offset:end]
        self.offset = end
        return slice

    # Writing/packing
    def write_magic(self, magic):
        self.write("4s", magic.encode('ascii'))

    def write(self, fmt, *args):
        """ Packs data onto end of file, shifting the offset"""
        self.file.extend(pack(self.bom + fmt, *args))
        self.offset = len(self.file)
        #- debug
        # to_remove = [x for x in self.target if self.offset >= x - 4]
        # for x in to_remove:
            # self.target.remove(x)
        # return
        #- end debug

    def write_offset(self, fmt, offset, args):
        """ packs data at offset, must be less than file length """
        pack_into(self.bom + fmt, self.file, offset, args)

    def write_remaining(self, data):
        """ writes the remaining bytes at current offset """
        length = len(data)
        self.file.extend(data)
        self.offset = len(self.file)
        return length

    def write_matrix(self, matrix, fmt='f'):
        width = len(matrix[0])
        fmt = str(width) + fmt
        for x in matrix:
            self.write(fmt, *x)

    def write_outer_offset(self):
        # self.linked_offsets.append(self.offset)     #- debug
        self.write('i', self.get_outer_offset())

    # Names
    def unpack_name(self, advance=True):
        """ Unpacks a single name from a pointer """
        [ptr] = self.read("I", 4 * advance)
        if not ptr:
            return None
        offset = self.beginOffset + ptr
        name = self.nameRefMap.get(offset)
        if name:
            return name
        try:
            if offset - 4 < self.names_offset:
                self.names_offset = offset - 4
            [name_lens] = self.read_offset("I", offset - 4)
        except struct.error:
            raise UnpackingError(self, 'Incorrect name offset')
        if name_lens > 256:
            raise UnpackingError(self, "Incorrect name offset")
        else:
            self.nameRefMap[offset] = name = self.read_offset(str(name_lens) + "s", offset)[0].decode()
            return name

    def store_name_ref(self, name, is_encoded=False):
        """ Stores a name reference offset to be filled when packing names
            assumes file to be at name offset to store
            assumes start to be at the parent relation offset
            and advances the file offset
        """
        name_map = self.nameRefMap
        if not is_encoded:
            name = name.encode('Ascii')
        if name not in name_map:
            name_map[name] = [(self.beginOffset, self.offset)]
        else:
            name_map[name].append((self.beginOffset, self.offset))
        self.advance(4)

    def pack_names(self):
        """packs in the names"""
        if len(self.nameRefMap) == 0:
            return
        names = self.nameRefMap
        self.names_offset = self.offset
        for key in sorted(names):
            if key is not None and key != b'':
                self.align(4)
                offset = self.offset + 4
                length = len(key)
                self.write("I{}sB".format(length), length, key, 0)
                # write name reference pointers
                reflist = names[key]
                for ref in reflist:
                    self.write_offset("I", ref[1], offset - ref[0])
        self.names_packed = True
        self.align(32)

    def convert_byte_arr(self):
        if type(self.file) != bytearray:
            self.file = bytearray(self.file)


class FolderEntry:
    """ A single entry in folder """

    def __init__(self, parent, idx, name="", data_ptr=0):
        self.parent = parent
        self.idx = idx  # id in relation to folder (first never a data entry)
        self.id = 0xffff  # id, left, right as calculated by binary tree
        self.left = 0
        self.right = 0
        self.name = name.encode('ascii')
        # name.encode('Ascii')
        self.dataPtr = data_ptr

    def getName(self):
        return self.name

    def get_offset(self):
        return self.dataPtr

    def follow(self, binfile):
        binfile.offset = self.dataPtr

    def unpack(self, binfile):
        self.id, u, self.left, self.right = binfile.read("4H", 8)
        self.name = binfile.unpack_name()
        # [dataptr] = binfile.read("I", 0)
        # print("{} entry {}: id {} left {} right {} data ptr {}".format(offset, self.name, self.id, self.left,
        #                                                                self.right, dataptr + binfile.beginOffset))
        binfile.store()

    def pack(self, binfile):
        # print("{} : {} ID {} left {} right {}".format(binfile.offset, self.name, self.id, self.left, self.right))
        # binfile.linked_offsets.append(binfile.offset)     #- debug
        # binfile.linked_offsets.append(binfile.offset + 4)     #- debug

        binfile.write("4H", self.id, 0, self.left, self.right)
        binfile.store_name_ref(self.name, True)
        if self.dataPtr:
            binfile.write("I", self.dataPtr)
        else:
            binfile.mark()  # marks the ref for storing data

    # ------------------------------------------------------------------------------
    # Most of this courtesy of Wiim http://wiki.tockdom.com/wiki/BRRES_Index_Group_(File_Format)
    #    modified slightly to accomodate
    def calc_brres_id(self, objectname):
        """ Calculates entry id """
        objlen = len(objectname)
        subjlen = len(self.name)
        if objlen < subjlen:
            val = self.name[subjlen - 1] # if IS_PY3 else ord(self.name[subjlen - 1])  # ugly hack to fix compatibility
            self.id = subjlen - 1 << 3 | self.get_highest_bit(val)
        else:
            while subjlen > 0:
                subjlen -= 1
                # if not IS_PY3:
                #     ch = ord(objectname[subjlen]) ^ ord(self.name[subjlen])
                # else:
                ch = objectname[subjlen] ^ self.name[subjlen]
                if ch:
                    self.id = subjlen << 3 | self.get_highest_bit(ch)
                    break

    @staticmethod
    def get_highest_bit(val):
        start = 0x80
        i = 7
        while start and not (val & start):
            i -= 1
            start >>= 1
        return i

    def get_brres_id_bit(self, id):
        idx = id >> 3
        if idx < len(self.name):
            val = self.name[idx] # if IS_PY3 else ord(self.name[idx])  # ugly hack to fix compatibility
            return val >> (id & 7) & 1
        return False

    def calc_brres_entry(self, entrylist):
        """ calculates brres entry, given an entry array"""
        head = entrylist[0]
        self.calc_brres_id(''.encode('ascii'))
        self.left = self.right = self.idx
        prev = head
        current = entrylist[head.left]
        is_right = False
        # loop
        while self.id <= current.id < prev.id:
            if self.id == current.id:
                # calculate new brres entry
                self.calc_brres_id(current.name)
                if current.get_brres_id_bit(self.id):
                    self.left = self.idx
                    self.right = current.idx
                else:
                    self.left = current.idx
                    self.right = self.idx
            prev = current
            is_right = self.get_brres_id_bit(current.id)
            if is_right:
                current = entrylist[current.right]
            else:
                current = entrylist[current.left]
        if len(current.name) == len(self.name) and current.get_brres_id_bit(self.id):
            self.right = current.idx
        else:
            self.left = current.idx
        if is_right:
            prev.right = self.idx
        else:
            prev.left = self.idx


#    Game over
# --------------------------------------------------------------------------------


class Folder:
    """ A folder for indexing files with a number of entries. (Index Group)"""

    def __init__(self, binfile, name=None):
        self.name = name
        self.binfile = binfile
        self.entries = []

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, key):
        return self.entries[key]

    def byte_size(self):
        """ returns byte size of folder """
        # headerlen + (numEntries + refEntry) * 16 bytes
        return 8 + (len(self.entries) + 1) * 16

    def add_entry(self, name, dataPtr=0):
        """Adds a named entry to folder"""
        length = len(self.entries)
        e = FolderEntry(self, length + 1, name, dataPtr)
        self.entries.append(e)
        return e

    def unpack(self, binfile):
        """ Unpacks folder """
        # print('Folder {} offset {}'.format(self.name, binfile.offset))
        self.offset = binfile.start()
        len, num_entries = binfile.read("2I", 8)
        binfile.advance(16)  # skip first entry
        # first = FolderEntry(self, 0)
        # first.unpack(binfile)
        for i in range(num_entries):
            sub = FolderEntry(self, i + 1)  # +1 because skips first entry
            sub.unpack(binfile)
            self.entries.append(sub)
        binfile.end()
        return self

    def pack(self, binfile):
        """ packs folder """
        self.offset = binfile.start()
        entries = self.calc_entries()
        binfile.write("2I", self.byte_size(), len(entries) - 1)  # -1 to ignore reference entry
        for x in entries:
            x.pack(binfile)
        binfile.end()

    def calc_entries(self):
        """ Calculates the left, right, and id of entries, returns the entries plus the first reference entry """
        # add on the first reference entry
        head = FolderEntry(self, 0)
        li = [head] + self.entries
        for x in li:
            x.calc_brres_entry(li)
        return li

    def open(self, name):
        """ opens the entry with name """
        try:
            return self.recall_entry(name)
        except UnpackingError:
            return False

    def open_i(self, index=0):
        """ opens entry at index, returns false on failure """
        try:
            return self.recall_entry_i(index)
        except IndexError:
            return False

    def recall_entry(self, name):
        """Advances to the file offset for unpacking (once only)"""
        for i in range(len(self.entries)):
            if self.entries[i].name == name:
                return self.recall_entry_i(i)
        raise UnpackingError(self.binfile, "Entry name {} not in folder {}".format(name, self.name))

    def recall_entry_i(self, index=0):
        """ Recalls entry at index (once only)"""
        entry = self.entries.pop(index)
        self.binfile.recall_offset(self.offset, index)
        return entry.name

    def create_entry_ref(self, name):
        """creates the reference in folder to the section (data pointer)"""
        name = name.encode('Ascii')
        for i in range(len(self.entries)):
            if self.entries[i].name == name:
                return self.create_entry_ref_i(i)
        raise PackingError(self.binfile, "Entry name {} not in folder {}".format(name, self.name))

    def create_entry_ref_i(self, index=0, pop=True):
        """ creates reference in folder to section at entry[index]"""
        if pop:
            entry = self.entries.pop(index)
        return self.binfile.create_ref_from(self.offset, index + 1, pop=pop)  # index + 1 ignoring the first ref entry


def printCollectionHex(collection):
    st = ""
    i = 0
    for x in collection:
        st += "{0:02X} ".format(x)
        if i % 16 == 15:
            print("{}".format(st))
            st = ""
        i += 1
    print("{}".format(st))
