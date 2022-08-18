import os
import inspect
from .mouse_position import MousePosition

class DirectoryNotAbsolute(Exception):
    pass

class Storage:
    def __init__(self, dir, *, max_bytes = 50000000):
        if _directory_is_absolute_path(dir):
            self.dir = dir
        else:
            raise DirectoryNotAbsolute(dir)
        _create_directory_if_nonexistent(self.dir)
        self.max_bytes = max_bytes

    def position(self, name: str):
        return self._get_storage_file(MousePositionFile, name) 
    
    def integer(self, name: str):
        return self._get_storage_file(IntegerFile, name)
    
    def float(self, name: str):
        return self._get_storage_file(FloatFile, name)
    
    def string(self, name: str):
        return self._get_storage_file(StringFile, name)
    
    def boolean(self, name: str):
        return self._get_storage_file(BooleanFile, name)

    def _get_storage_file(self, type, name: str):
        return type.create(self.get_path(), name, max_bytes = self.max_bytes)

    def get_path(self):
        return self.dir

def _create_directory_if_nonexistent(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def _directory_is_absolute_path(path):
    return os.path.isabs(path)

class RelativeStorage(Storage):
    def __init__(self, path, name = 'Fire Chicken Storage', *, max_bytes = 50000000):
        target_directory = _compute_directory_at_path(path)
        dir = _join_path(target_directory, name)
        Storage.__init__(self, dir, max_bytes = max_bytes)

def _compute_directory_at_path(path):
    if os.path.isdir(path):
        return path
    else:
        return _compute_file_directory(path)

def _compute_file_directory(path):
    absolute_filepath = os.path.abspath(path)
    file_directory = os.path.dirname(absolute_filepath)
    return file_directory

def _join_path(directory, path):
    return os.path.join(directory, path)

#Parent class not meant to be instantiated
#Implement Python string method for storing object for storage
#Implement classmethod get_value_from_text for reading from the file
#Implement _initial_value for setting the initial value
class StorageFile:
    def __init__(self, folder: str, name: str, *, max_bytes: int = 50000000):
        self.folder = folder
        self.name = name
        self.max_bytes = max_bytes
        self._initialize_file_if_nonexistent()
        self._retrieve_value()
    @classmethod
    def create(cls, folder: str, name: str, *, max_bytes: int = 50000000):
        return cls(folder, name, max_bytes = max_bytes)


    def get(self):
        return self.value
    
    def set(self, value):
        self.value = value
        self._store_value()
    
    def _store_value(self):
        with open(self.get_path(), 'w') as value_file:
            value_text = str(self.value)
            value_file.write(value_text)
    
    def _retrieve_value(self):
        if self._file_too_big():
            self._raise_file_too_big_exception()
        with open(self.get_path(), 'r') as position_file:
            value_text = position_file.read(self.max_bytes)
            self.value = self.get_value_from_text(value_text)

    def _file_too_big(self):
        file_size = os.path.getsize(self.get_path())
        return file_size > self.max_bytes

    def _raise_file_too_big_exception(self):
        raise InvalidFileSizeException(f'Storage file at path {self.get_path()} exceeded maximum size of'
        f'{self.max_bytes} bytes!'
        )

    def get_path(self):
        return os.path.join(self.folder, self.name)

    def _initialize_file_if_nonexistent(self):
        if not os.path.exists(self.get_path()):
            self._make_directory_if_nonexistent()
            initial_value = self._initial_value()
            self.set(initial_value)
    def _make_directory_if_nonexistent(self):
        _create_directory_if_nonexistent(self.folder)

class InvalidFileSizeException(Exception):
    pass

class MousePositionFile(StorageFile):
    def set_to_current_mouse_position(self):
        position = MousePosition.current()
        self.set(position)
    
    @classmethod
    def get_value_from_text(self, text: str):
        return MousePosition.from_text(text)
    
    def _initial_value(self):
        return MousePosition(0, 0)
    
class IntegerFile(StorageFile):
    @classmethod
    def get_value_from_text(self, text: str):
        return int(text)
    
    def _initial_value(self):
        return 0

class FloatFile(StorageFile):
    @classmethod
    def get_value_from_text(self, text: str):
        return float(text)
    
    def _initial_value(self):
        return 0.0
    
class StringFile(StorageFile):
    @classmethod
    def get_value_from_text(self, text: str):
        return text
    
    def _initial_value(self):
        return ''

class BooleanFile(StorageFile):
    @classmethod
    def get_value_from_text(self, text: str):
        return bool(text)
    
    def _initial_value(self):
        return False

    

    