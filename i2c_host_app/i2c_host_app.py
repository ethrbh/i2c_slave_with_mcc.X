#!/usr/local/bin/python
# encoding: utf-8
'''
i2c_host_app.i2c_host_app -- shortdesc

i2c_host_app.i2c_host_app is a description

It defines classes_and_methods

@author:     Robert Balogh

@copyright:  2021 organization_name. All rights reserved.

@license:    license

@contact:    ethrbh@gmail.com
@deffield    updated: Updated
'''

import sys
import os
import i2c_wrapper
import logging
import host_logger

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from _curses import OK

__all__ = []
__version__ = 0.1
__date__ = '2021-11-15'
__updated__ = '2021-11-15'

DEBUG = 1
TESTRUN = 0
PROFILE = 0
I2C_OPERATION_READ = "read"
I2C_OPERATION_WRITE = "write"


# ===========================================================================
# ===========================================================================
class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''

    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


# ===========================================================================
# Read a single byte from a device. In EEPROM terminology, this is the
# current address read operation.
#
# Input:
#    i2c_obj     -    object of the I2C wrapper
#    i2c_bus     -    int, the integer id of the I2C bus to be used
#                     For example if the I2C bus name is /dev/i2c-1
#                     the integer id to be used here is 1.
#    i2c_addr    -    int, i2c address
# Output:
#    ["ok", data] | ["error", reason]
#    data: integer
#    reason: string
# ===========================================================================
def read_byte(i2c_obj, i2c_bus, i2c_addr):
    return i2c_obj.read_byte(i2c_bus, i2c_addr)


# ===========================================================================
# Read a single byte from a device by specify the register address to be read out.
# In EEPROM terminology, this is the random read operation.
#
# Input:
#    i2c_obj     -    object of the I2C wrapper
#    i2c_bus     -    int, the integer id of the I2C bus to be used
#                     For example if the I2C bus name is /dev/i2c-1
#                     the integer id to be used here is 1.
#    i2c_addr    -    i2c address
#                     valid type: int | hex string
#    reg_addr    -    the address of the register to be read
#                     valid type: int | hex string
# Output:
#    ["ok", data] | ["error", reason]
#    data: integer
#    reason: string
# ===========================================================================
def read_byte_data(i2c_obj, i2c_bus, i2c_addr, reg_addr):
    return i2c_obj.read_byte_data(i2c_bus, i2c_addr, reg_addr)


# ===========================================================================
# Read a block of byte data from a given register
#
# Input:
#    i2c_obj     -    object of the I2C wrapper
#    i2c_bus     -    int, the integer id of the I2C bus to be used
#                     For example if the I2C bus name is /dev/i2c-1
#                     the integer id to be used here is 1.
#    i2c_addr    -    i2c address
#                     valid type: int | hex string
#    reg_addr    -    the address of the register to be read
#                     valid type: int | hex string
#    length      -    integer, number of byte to be read out
# Output:
#    ["ok", data] | ["error", reason]
#    data: list of integer
#    reason: string
# ===========================================================================
def read_i2c_block_data(i2c_obj, i2c_bus, i2c_addr, reg_addr, length):
    return i2c_obj.read_i2c_block_data(i2c_bus, i2c_addr, reg_addr, length)

# # ===========================================================================
# # Write a single register.
# #
# # Input:
# #    i2c_obj     -    object of the I2C wrapper
# #    i2c_bus     -    int, the integer id of the I2C bus to be used
# #                     For example if the I2C bus name is /dev/i2c-1
# #                     the integer id to be used here is 1.
# #    i2c_addr    -    i2c address
# #                     valid type: int | hex string
# #    reg_addr    -    the address of the register to be write
# #                     valid type: int | hex string
# #    reg_value   -    the value of the register to be write
# #                     valid type: int | hex string
# # Output:
# #    ["ok", data] | ["error", reason]
# #    data: integer
# #    reason: string
# # ===========================================================================
# def write_byte_data(i2c_obj, i2c_bus, i2c_addr, reg_addr, reg_value):
#     return i2c_obj.write_byte_data(i2c_bus, i2c_addr, reg_addr, reg_value)


# ===========================================================================
# Write a block of byte data to a given register
#
# Input:
#    i2c_obj     -    object of the I2C wrapper
#    i2c_bus     -    int, the integer id of the I2C bus to be used
#                     For example if the I2C bus name is /dev/i2c-1
#                     the integer id to be used here is 1.
#    i2c_addr    -    i2c address
#                     valid type: int | hex string
#    reg_addr    -    the address of the register to be write
#                     valid type: int | hex string
#    reg_value   -    list of byte to be write
#                     valid type: list of int | list of hex string
# Output:
#    ["ok", data] | ["error", reason]
#    data: integer
#    reason: string
# ===========================================================================
def write_i2c_block_data(i2c_obj, i2c_bus, i2c_addr, reg_addr, reg_value):
    return i2c_obj.write_i2c_block_data(i2c_bus, i2c_addr, reg_addr, reg_value)


# ===========================================================================
# ===========================================================================
def main(argv=None):  # IGNORE:C0111
    global I2C_OPERATION_READ, I2C_OPERATION_WRITE

    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Robert Balogh on %s.
  Copyright 2021 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

  This program demonstrates how to read/write I2C EEPROM via
  ordinary i2c-tools on Ubuntu OS using Python language.
  
  In my case the I2C EEPROM is emulated by a PIC MCU,
  and unfortunately ordinary SMBUS2 Python lib does not work
  properly. The "Random Read" I2C operation, where 2 control-byte
  has been used within the full operation, wont work.
  
  I did not find the root-cause of this :-( 
  
  Because I still want use Python for my "Host app" in the future, 
  I made a wrapper script  around i2cget and i2cset programs, 
  because using these, accessing to the emulated EEPROM in the PIC,
  is working well.
  
USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-v', '--version', action='version', version=program_version_message)

        parser.add_argument("-i2c_bus", default=1, help="The i2c bus number (e.g. 0 or 1). Default is 1")
        parser.add_argument("-i2c_addr", help="The 7 bit wide address of the I2C slave device. This can be integer of HEX string.")
        parser.add_argument("-reg_addr", help=("The 8 bit wide address of the register to be read/write in the I2C slave device. " +
                                                  "This can be integer of HEX string."))
        parser.add_argument("-reg_value", help=("The 8 bit wide data or comma separated list of data to be write into the register in the I2C slave device. " +
                                                "Each data element can be integer of HEX string. " +
                                                "For example " +
                                                "    when only one data byte should be write into a specified register address: " +
                                                "      -reg_value 6 " +
                                                "    when more than one data byte should be write from a specified register address: " +
                                                "      -reg_value 6,7,8,9 NOTE: NO SPACE is allowed between comma and number!!"))
        parser.add_argument("-length", help="The number of byte to be read out from the given register address from the I2C slave device.")
        parser.add_argument("-i2c_operation",
                            help=("The operation to be executed in the I2C slave device. This can be " +
                                  I2C_OPERATION_READ + " | " + I2C_OPERATION_WRITE))
        parser.add_argument("-loglevel", default="INFO", help=("The level of the logger to be used. " +
                                                               "It can be INFO, WARNING, ERROR, CRITICAL, DEBUG, FATAL " +
                                                               "Default is INFO"))

        # Process arguments
        args = parser.parse_args()

        # Setup logger's parameters
        toolname = "i2c_wrapper"
        caller_module = os.path.basename(__file__)
        logfile = toolname + ".log"

        # Setup log level
        if args.loglevel == "INFO":
            loglevel = logging.INFO;
        elif args.loglevel == "WARNING":
            loglevel = logging.WARNING
        elif args.loglevel == "ERROR":
            loglevel = logging.ERROR
        elif args.loglevel == "CRITICAL":
            loglevel = logging.CRITICAL
        elif args.loglevel == "DEBUG":
            loglevel = logging.DEBUG
        elif args.loglevel == "FATAL":
            loglevel = logging.FATAL

        # Create the logger object to be used for logging
        logger_obj = host_logger.setup(toolname, caller_module, loglevel, logfile)

        # Validate I2C mandatory CLI parameters
        if args.i2c_addr is None:
            logger_obj.fatal("I2C address CLI parameter is missing.")

        # Init I2C wrapper
        i2c_obj = i2c_wrapper.I2CBus(args.i2c_bus, logger_obj)

        # Perform the I2C operation
        if args.i2c_operation == I2C_OPERATION_READ:
            if args.reg_addr is None:
                return read_byte(i2c_obj, args.i2c_bus, args.i2c_addr)
            else:
                if args.length is None:
                    return read_byte_data(i2c_obj, args.i2c_bus, args.i2c_addr, args.reg_addr)
                else:
                    return read_i2c_block_data(i2c_obj, args.i2c_bus, args.i2c_addr, args.reg_addr, args.length)

        elif args.i2c_operation == I2C_OPERATION_WRITE:
            if args.reg_addr is None or args.reg_value is None:
                logger_obj.fatal("Register address (-reg_addr) and/or register value (-reg_val) CLI parameter(s) missing.")
            else:
                # Convert the given reg_value to list, and pass that to the write_i2c_block_data function
                return write_i2c_block_data(i2c_obj, args.i2c_bus, args.i2c_addr, args.reg_addr, args.reg_value.split(","))

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


if __name__ == "__main__":
    sys.exit(main())
