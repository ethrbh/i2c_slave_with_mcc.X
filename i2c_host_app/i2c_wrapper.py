# ===========================================================================
# Description
#
# This module is a wrapper for ordinary
# i2c-tool program in Ubuntu.
#
# Unfortunately smbus2 Python lib
# does not works with my PIC MCU SLAVE
# code, but works with real EEPROM.
# Thus, until I do not fix the fault in the
# PIC SLAVE code, I use i2c-tool for read/write
# byte in the I2C SLAVE device.
# ===========================================================================

# ===========================================================================
# Imports
# ===========================================================================
import subprocess

# ===========================================================================
# Global definitions
# ===========================================================================
I2C_PROGRAM_SET = "sudo i2cset"
I2C_PROGRAM_GET = "sudo i2cget"

RES_CODE_OK = "ok"
RES_CODE_ERROR = "error"

RETURN_CODE_SUCCESS = 0
RETURN_CODE_FAILED = 1


# ===========================================================================
# Checks the given string is an integer in string format or not.
# Input:
#    intString    :    string
# Output:
#    boolean
# ===========================================================================
def is_intstring(intString):
    try:
        int(intString)
        return True
    except ValueError:
        return False


# ===========================================================================
# Check the given string is a Hexadecimal number
# or not.
# A hexadecimal number SHOULD starts with "0x"
# substring.
#
# Input:
#    theString    :    string
# Output
#    boolean
# ===========================================================================
def is_hex(theString):
    return theString.lower().startswith("0x")


# ===========================================================================
# Check the given data integer or not.
#
# Input:
#    data    :    any
# Output:
#    boolean
# ===========================================================================
def is_integer(data):
    return isinstance(data, int)


# ===========================================================================
# Convert the given data to hexadecimal string
# if the given data does not hexadecimal string already.
#
# Input:
#    data    : int | hex string
# Output:
#    ["ok", hexStr] | ["error", reason]
# ===========================================================================
def int_to_hex(data):
    # Check the given data is an integer number but in string format.
    # If so, convert it to integer.
    if is_intstring(data):
        data = int(data)

    if (is_integer(data)):
        return ["ok", hex(data)]
    else:
        if (is_hex(data)):
            return [RES_CODE_OK, data]
        else:
            return [RES_CODE_ERROR, "invalid data. " + str(data)]


# ===========================================================================
# Converts hex number to integer
# Input:
#    hexNUmber    :    string, hex number in string format. e.g. "0x02"
# Output:
#    intNumber    :    integer
# ===========================================================================
def hex_to_int(hexNumberInString):
    return int(hexNumberInString, 16)


# ===========================================================================
# Execute a BASH command
# Input:
#    bashCmd     -    string
#    logger_obj  -    None | logger object
# Output:
#    [returnCode, stdOut, errorText]
#    returnCode    : if 0, the command execution was success, otherwise does not
#    stdOut        : string, the STDO result of the command execution
#    errorText     : None, if no error occurred during the command execution, otherwise
#                    some text
# ===========================================================================
def execute_bash_cmd(bashCmd, logger_obj=None):
    process = subprocess.Popen(bashCmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    returnCode = process.wait()
    stdOut, errorText = process.communicate()

    if logger_obj is not None:
        logger_obj.debug("I2C command execution. " +
                        str({'bashCmd': bashCmd,
                             'returnCode': returnCode,
                             'stdOut': stdOut,
                             'errorText': errorText}))

    return [returnCode, stdOut, errorText]


class I2CBus(object):

    def __init__(self, i2c_bus, logger_obj=None):
        """
        Initialize and (optionally) open an i2c bus connection.
        
        :param i2c_bus: i2c bus number (e.g. 0 or 1)
            or an absolute file path (e.g. `/dev/i2c-42`).
            If not given, a subsequent  call to ``open()`` is required.
        :type i2c_bus: int or str
        
        :param logger_obj: logger object to be used
        :type logger_obj : ??
        """
        self.i2c_bus = i2c_bus
        self.logger_obj = logger_obj

    def __enter__(self):
        """Enter handler."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit handler."""
        self.close()

    # ===========================================================================
    # Set the register address to be read
    #
    # Input:
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
    def set_register_address_for_read(self, i2c_bus, i2c_addr, reg_addr):
        [i2c_addr_hex_res_code, i2c_addr_hex_value] = int_to_hex(i2c_addr)

        if i2c_addr_hex_res_code == RES_CODE_OK:
            [reg_addr_hex_res_code, reg_addr_hex_value] = int_to_hex(reg_addr)

            if reg_addr_hex_res_code == RES_CODE_OK:
                # I2C cmd part 1 - setup the register address to be read out
                i2cCmd = I2C_PROGRAM_SET + " " + "-y " + str(i2c_bus) + " " + i2c_addr_hex_value + " " + reg_addr_hex_value
                [returnCode, stdOut, errorText] = execute_bash_cmd(i2cCmd, self.logger_obj)

                if returnCode == RETURN_CODE_SUCCESS:
                    return [RES_CODE_OK, stdOut]
                else:
                    if errorText is None:
                        return [RES_CODE_ERROR, str(stdOut)]
                    else:
                        return [RES_CODE_ERROR, str(errorText)]
            else:
                return [RES_CODE_ERROR, "invalid reg_addr " + str(reg_addr)]
        else:
            return [RES_CODE_ERROR, "invalid i2c_addr " + str(i2c_addr)]

    # ===========================================================================
    # Read a single byte from a device. In EEPROM terminology, this is the
    # current address read operation.
    #
    # Input:
    #    i2c_bus     -    int, the integer id of the I2C bus to be used
    #                     For example if the I2C bus name is /dev/i2c-1
    #                     the integer id to be used here is 1.
    #    i2c_addr    -    int | hex string, i2c address
    # Output:
    #    ["ok", data] | ["error", reason]
    #    data: integer
    #    reason: string
    # ===========================================================================
    def read_byte(self, i2c_bus, i2c_addr):
        [i2c_addr_hex_res_code, i2c_addr_hex_value] = int_to_hex(i2c_addr)

        if i2c_addr_hex_res_code == RES_CODE_OK:

            i2cCmd = I2C_PROGRAM_GET + " " + "-y " + str(i2c_bus) + " " + i2c_addr_hex_value
            [returnCode, stdOut, errorText] = execute_bash_cmd(i2cCmd, self.logger_obj)

            if returnCode == 0:
                return [RES_CODE_OK, hex_to_int(stdOut)]
            else:
                if errorText is None:
                    return [RES_CODE_ERROR, str(stdOut)]
                else:
                    return [RES_CODE_ERROR, str(errorText)]
        else:
            return [RES_CODE_ERROR, "Invalid i2c_addr, " + str(i2c_addr)]

    # ===========================================================================
    # Read a single byte from a device by specify the register address to be read out.
    # In EEPROM terminology, this is the random read operation.
    #
    # Input:
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
    def read_byte_data(self, i2c_bus, i2c_addr, reg_addr):
        # Mark the register to be read out
        [resCode, resText] = self.set_register_address_for_read(i2c_bus, i2c_addr, reg_addr)

        if resCode == RES_CODE_OK:
            # I2C cmd part - read the previously set register
            [_i2c_addr_hex_res_code, i2c_addr_hex_value] = int_to_hex(i2c_addr)

            i2cCmd = I2C_PROGRAM_GET + " " + "-y " + str(i2c_bus) + " " + i2c_addr_hex_value
            [returnCode, stdOut, errorText] = execute_bash_cmd(i2cCmd, self.logger_obj)

            if returnCode == 0:
                return [RES_CODE_OK, hex_to_int(stdOut)]
            else:
                if errorText is None:
                    return [RES_CODE_ERROR, str(stdOut)]
                else:
                    return [RES_CODE_ERROR, str(errorText)]
        else:
            return [resCode, resText]

    # ===========================================================================
    # Read a block of byte data from a given register
    #
    # Input:
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
    def read_i2c_block_data(self, i2c_bus, i2c_addr, reg_addr, length):
        data = []
        lengthInt = 0
        if is_intstring(length):
            lengthInt = int(length)
        elif is_integer(length):
            lengthInt = length
        else:
            return [RES_CODE_ERROR, "Invalid length value, " + str(length)]

        # Set the register address
        [resCode, resText] = self.set_register_address_for_read(i2c_bus, i2c_addr, reg_addr)
        if resCode == RES_CODE_ERROR:
            return [resCode, resText]

        for _i in range(lengthInt):
            [resCode, resText] = self.read_byte(i2c_bus, i2c_addr)
            if resCode == RES_CODE_ERROR:
                return [resCode, resText]
            else:
                # Append the byte into the data
                data.append(resText)

        return [RES_CODE_OK, data]

    # ===========================================================================
    # Write a single register.
    #
    # Input:
    #    i2c_bus     -    int, the integer id of the I2C bus to be used
    #                     For example if the I2C bus name is /dev/i2c-1
    #                     the integer id to be used here is 1.
    #    i2c_addr    -    i2c address
    #                     valid type: int | hex string
    #    reg_addr    -    the address of the register to be write
    #                     valid type: int | hex string
    #    reg_value   -    the value of the register to be write
    #                     valid type: int | hex string
    # Output:
    #    ["ok", data] | ["error", reason]
    #    data: integer
    #    reason: string
    # ===========================================================================
    def write_byte_data(self, i2c_bus, i2c_addr, reg_addr, reg_value):
        [i2c_addr_hex_res_code, i2c_addr_hex_value] = int_to_hex(i2c_addr)

        if i2c_addr_hex_res_code == RES_CODE_OK:
            [reg_addr_hex_res_code, reg_addr_hex_value] = int_to_hex(reg_addr)

            if reg_addr_hex_res_code == RES_CODE_OK:
                # I2C cmd- setup the register address to be read out
                [reg_value_hex_res_code, reg_value_hex_value] = int_to_hex(reg_value)

                if reg_value_hex_res_code == RES_CODE_OK:

                    i2cCmd = (I2C_PROGRAM_SET + " " + "-y " + str(i2c_bus) + " " +
                              i2c_addr_hex_value + " " + reg_addr_hex_value + " " +
                              reg_value_hex_value)
                    [returnCode, stdOut, errorText] = execute_bash_cmd(i2cCmd, self.logger_obj)

                    if returnCode == RETURN_CODE_SUCCESS:
                        return [RES_CODE_OK, stdOut]
                    else:
                        if errorText is None:
                            return [RES_CODE_ERROR, str(stdOut)]
                        else:
                            return [RES_CODE_ERROR, str(errorText)]
                else:
                    return [RES_CODE_ERROR, "invalid reg_value " + str(reg_value)]
            else:
                return [RES_CODE_ERROR, "invalid reg_addr " + str(reg_addr)]
        else:
            return [RES_CODE_ERROR, "invalid i2c_addr " + str(i2c_addr)]

    # ===========================================================================
    # Write a block of byte data to a given register
    #
    # Input:
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
    def write_i2c_block_data(self, i2c_bus, i2c_addr, reg_addr, reg_value):
        # Convert the given reg_addr to integer, because it is much easier to
        # count with integer than hex value.

        if is_intstring(reg_addr):
            reg_addr = int(reg_addr, 10)
        elif is_integer(reg_addr):
            reg_addr = reg_addr
        elif is_hex(reg_addr):
            # Convert the hex string
            reg_addr = int(reg_addr, 16)
        else:
            return [RES_CODE_ERROR, "Invalid reg_addr value. " + str(reg_addr)]

        reg_addr_runtime = reg_addr
        for theByte in reg_value:
            [resCode, resText] = self.write_byte_data(i2c_bus, i2c_addr, reg_addr_runtime, theByte)

            if resCode == RES_CODE_ERROR:
                return [resCode, resText]

            # Increment reg_addr_runtime
            reg_addr_runtime = reg_addr_runtime + 1

        return [RES_CODE_OK, ""]

