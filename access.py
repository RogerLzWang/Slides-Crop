#!/usr/bin/python
################################################################################
#
#   access.py
#   Author: Roger Wang
#   Date: 2024-06-25
#
#   Static class that helps to check the permission for read and write actions 
#   to files and directories.
#
################################################################################

import os

class Access():
    """
    Check whether or not the given path to a file is readable.
    @param path: str, the path to be checked.
    @return 0: path is readable.
    @return 1: ERROR, path does not exist.
    @return 2: ERROR, path is not a file.
    @return 3: ERROR, permission error.
    """
    def check_file_read(path):
        if not os.path.exists(path):
            return 1
        if not os.path.isfile(path):
            return 2

        try:
            # Check if the file is writable using os.access().
            if os.access(path, os.R_OK):
                return 0
            else:
                return 3
        
        except FileNotFoundError:
            return 1
        
        except PermissionError:
            return 3
        
    """
    Check whether or not the given path to a file is writable.
    @param path: str, the path to be checked.
    @return 0: path is writable.
    @return 1: ERROR, path does not exist.
    @return 2: ERROR, path is not a file.
    @return 3: ERROR, permission error.
    """
    def check_file_write(path):
        if not os.path.exists(path):
            return 1
        if not os.path.isfile(path):
            return 2

        try:
            # Check if the file is writable using os.access().
            if os.access(path, os.W_OK):
                return 0
            else:
                return 3
        
        except FileNotFoundError:
            return 1
        
        except PermissionError:
            return 3

    """
    Check whether or not the given path to a new file is writable.
    @param path: str, the path to be checked.
    @return 0: path is writable.
    @return 1: ERROR, path does not exist.
    @return 2: ERROR, path is not a file.
    @return 3: ERROR, permission error.
    """
    def check_new_file_write(path):
        # If the file already exists, check if we can write to that file.
        if os.path.exists(path):
            return Access.check_file_write(path)
        
        # Otherwise, check if we can write to the directory.
        dir_path = os.path.dirname(path)
        return Access.check_dir_write(dir_path)

    """
    Check whether or not the given path to a directory is readable.
    @param path: str, the path to be checked.
    @return 0: path is readable.
    @return 1: ERROR, path does not exist.
    @return 2: ERROR, path is not a directory.
    @return 3: ERROR, permission error.
    """
    def check_dir_read(path):
        if not os.path.exists(path):
            return 1
        if not os.path.isdir(path):
            return 2

        try:
            # Check if the directory is writable using os.access().
            if os.access(path, os.R_OK):
                return 0
            else:
                return 3
        
        except FileNotFoundError:
            return 1
        
        except PermissionError:
            return 3
        
    """
    Check whether or not the given path to a directory is writable.
    @param path: str, the path to be checked.
    @return 0: path is writable.
    @return 1: ERROR, path does not exist.
    @return 2: ERROR, path is not a directory.
    @return 3: ERROR, permission error.
    """
    def check_dir_write(path):
        if not os.path.exists(path):
            return 1
        if not os.path.isdir(path):
            return 2

        try:
            # Check if the directory is writable using os.access().
            if os.access(path, os.W_OK):
                return 0
            else:
                return 3
        
        except FileNotFoundError:
            return 1
        
        except PermissionError:
            return 3