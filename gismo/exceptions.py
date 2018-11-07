#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).



# ==============================================================================
class GISMOException(Exception):
    """
    Created     20180926     
    Updated

    Blueprint for error message.
    code is for external mapping of exceptions. For example if a GUI wants to
    handle the error text for different languages.
    """
    code = None
    message = ''

    def __init__(self, message='', code=''):
        self.message = '{}: {}'.format(self.message, message)
        if code:
            self.code = code


# ==============================================================================
class GISMOExceptionMissingPath(GISMOException):
    """
    Created     20180926     
    """
    code = ''
    message = ''


# ==============================================================================
class GISMOExceptionInvalidPath(GISMOException):
    """
    Created     20181002     
    """
    code = ''
    message = ''


# ==============================================================================
class GISMOExceptionMissingKey(GISMOException):
    """
    Created     20180926     
    """
    code = ''
    message = ''


# ==============================================================================
class GISMOExceptionMissingInputArgument(GISMOException):
    """
    Created     20180926     
    """
    code = ''
    message = ''

# ==============================================================================
class GISMOExceptionMissingQualityParameter(GISMOException):
    """
    Created     20181005     
    """
    code = ''
    message = ''


# ==============================================================================
class GISMOExceptionInvalidParameter(GISMOException):
    """
    Created     20180927     
    """
    code = ''
    message = ''


# ==============================================================================
class GISMOExceptionInvalidSamplingType(GISMOException):
    """
    Created     20181002     
    """
    code = ''
    message = ''


# ==============================================================================
class GISMOExceptionInvalidClass(GISMOException):
    """
    Created     20181002     
    """
    code = ''
    message = ''


# ==============================================================================
class GISMOExceptionInvalidFileId(GISMOException):
    """
    Created     20181004     
    """
    code = ''
    message = ''

# ==============================================================================
class GISMOExceptionInvalidOption(GISMOException):
    """
    Created     20181004     
    """
    code = ''
    message = ''

# ==============================================================================
class GISMOExceptionInvalidInputArgument(GISMOException):
    """
    Created     20181004     
    """
    code = ''
    message = ''


# ==============================================================================
class GISMOExceptionInvalidFlag(GISMOException):
    """
    Created     20181004     
    """
    code = ''
    message = ''


# ==============================================================================
class GISMOExceptionCopyFiles(GISMOException):
    """
    Created     20181001     
    """
    code = ''
    message = ''


# ==============================================================================
class GISMOExceptionMetadataError(GISMOException):
    """
    Created     20181002     
    """
    code = ''
    message = ''


# ==============================================================================
class GISMOExceptionMethodNotImplemented(GISMOException):
    """
    Created     20181002     
    """
    code = ''
    message = 'Method not implemented'

# ==============================================================================
class GISMOExceptionInvalidTimeFormat(GISMOException):
    """
    Created     20181019
    """
    code = ''
    message = ''

# ==============================================================================
class GISMOExceptionFileExcists(GISMOException):
    """
    Created     20181106
    """
    code = ''
    message = ''
