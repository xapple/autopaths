################################################################################
class FileSize(object):
    """
    Container for a size in bytes with a human readable representation
    Use it like this:

        >>> size = FileSize(123123123)
        >>> print size
        '117.4 MiB'
    """

    precisions = [0, 0, 1, 2, 2, 2]

    def __init__(self, size, system='decimal'):
        # Record the size #
        self.size = size
        # Pick the system used #
        if system is 'binary':
            self.chunk = 1024
            self.units = ['bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']
        elif system is 'decimal':
            self.chunk = 1000
            self.units = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']
        else:
            raise Exception("Unrecognized file size system '%s'" % system)

    def __eq__(self, other):
        return self.size == other

    def __str__(self):
        if self.size == 0: return '0 bytes'
        from math import log
        unit = self.units[min(int(log(self.size, self.chunk)), len(self.units) - 1)]
        return self.format(unit)

    def format(self, unit):
        # Input checking #
        if unit not in self.units: raise Exception("Not a valid file size unit: '%s'" % unit)
        # Special no plural case #
        if self.size == 1 and unit == 'bytes': return '1 byte'
        # Compute #
        exponent      = self.units.index(unit)
        quotient      = float(self.size) / self.chunk**exponent
        precision     = self.precisions[exponent]
        format_string = '{:.%sf} {}' % (precision)
        # Return a string #
        return format_string.format(quotient, unit)
