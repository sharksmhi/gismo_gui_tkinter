# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 16:51:08 2018

@author: a001985
"""

# ==============================================================================
class GTBException(Exception):
    """
    Created     20181002    by Magnus Wenzer
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


class GTBExceptionMissingAttribute(GTBException):
    """
    Created 20180625    by Magnus Wenzer
    Updated 20181002    by Magnus Wenzer
    """
    code = ''
    message = ''