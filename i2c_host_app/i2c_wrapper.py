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
    try:
        return isinstance(data, int)
    except ValueError:
        return False


# ===========================================================================
# Convert the given data to hexadecimal string
# if the given data does not hexadecimal string already.
#
# Input:
#    data    : int | hex string
# Output:
#    hexStr | ["error", reason]
# ===========================================================================
def int_to_hex(data):
    # Check the given data is an integer number but in string format.
    # If so, convert it to integer.
    if is_intstring(data):
        data = int(data)

    if (is_integer(data)):
        return hex(data)
    else:
        if (is_hex(data)):
            return [RES_CODE_OK, data]
        else:
            return [RES_CODE_ERROR, "invalid data. " + str(data)]


# ===========================================================================
# Converts hex number to integer
# Input:
#    hexNumber    :    string, hex number in string format. e.g. "0x02"
# Output:
#    intNumber | ["error", reason]
#    intNumber: integer
#    reason: string
# ===========================================================================
def hex_to_int(hexNumberInString):
    try:
        return int(hexNumberInString, 16)
    except ValueError:
        return [RES_CODE_ERROR, "Failed to convert " + str(hexNumberInString) + " to integer"]


# ===========================================================================
# Converts hex number or integer number which is in string to integer
# Input:
#    strNumber    :    string, hex number or integer in string format. e.g. "0x02", "123"
# Output:
#    intNumber | ["error", reason]
#    intNumber: integer
#    reason: string
# ===========================================================================
def str_to_int(strNumber):
    if (is_integer(strNumber)):
        return strNumber
    elif (is_hex(strNumber)):
        return hex_to_int(strNumber)
    elif (is_intstring(strNumber)):
        return int(strNumber)
    else:
        return [RES_CODE_ERROR, "Invalid string for integer conversation, " + str(strNumber)]


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
    # Test to convert given string to integer
    # ===========================================================================
    def test_conv_string_data_to_in(self, stringData):
        return str_to_int(stringData)

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
    #    data | ["error", reason]
    #    data: integer
    #    reason: string
    # ===========================================================================
    def set_register_address_for_read(self, i2c_bus, i2c_addr, reg_addr):
        result = int_to_hex(i2c_addr)
        if isinstance(result, list):
            [_, reason] = result
            return [RES_CODE_ERROR, "Invalid i2c_addr " + str(i2c_addr) + " " + reason]
        else:
            # Save the hex value of the I2C address
            i2c_addr_hex_value = result

            result = int_to_hex(reg_addr)
            if isinstance(result, list):
                [_, reason] = result
                return [RES_CODE_ERROR, "Invalid reg_addr " + str(reg_addr) + " " + reason]
            else:
                # Save the hex value of the register address
                reg_addr_hex_value = result

                # I2C cmd part 1 - setup the register address to be read out
                i2cCmd = I2C_PROGRAM_SET + " " + "-y " + str(i2c_bus) + " " + i2c_addr_hex_value + " " + reg_addr_hex_value
                [returnCode, stdOut, errorText] = execute_bash_cmd(i2cCmd, self.logger_obj)

                if returnCode == RETURN_CODE_SUCCESS:
                    return str_to_int(stdOut)
                else:
                    if errorText is None:
                        return [RES_CODE_ERROR, str(stdOut)]
                    else:
                        return [RES_CODE_ERROR, str(errorText)]

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
    #    data | ["error", reason]
    #    data: integer
    #    reason: string
    # ===========================================================================
    def read_byte(self, i2c_bus, i2c_addr):
        result = int_to_hex(i2c_addr)

        if isinstance(result, list):
            [_, reason] = result
            return [RES_CODE_ERROR, "Invalid i2c_addr, " + str(i2c_addr) + " " + reason]
        else:
            # Save the hex value of the I2C address
            i2c_addr_hex_value = result

            i2cCmd = I2C_PROGRAM_GET + " " + "-y " + str(i2c_bus) + " " + i2c_addr_hex_value
            [returnCode, stdOut, errorText] = execute_bash_cmd(i2cCmd, self.logger_obj)

            if returnCode == 0:
                return str_to_int(stdOut)
            else:
                if errorText is None:
                    return [RES_CODE_ERROR, str(stdOut)]
                else:
                    return [RES_CODE_ERROR, str(errorText)]

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
    #    data | ["error", reason]
    #    data: integer
    #    reason: string
    # ===========================================================================
    def read_byte_data(self, i2c_bus, i2c_addr, reg_addr):
        # Mark the register to be read out
        result = self.set_register_address_for_read(i2c_bus, i2c_addr, reg_addr)

        if isinstance(result, list):
            return result
        else:
            # I2C cmd part - read the previously set register
            result = int_to_hex(i2c_addr)

            if isinstance(result, list):
                [_, reason] = result
                return [RES_CODE_ERROR, "Invalid i2c_addr, " + str(i2c_addr) + " " + reason]
            else:
                # Save the hex value of the I2C address
                i2c_addr_hex_value = result

                i2cCmd = I2C_PROGRAM_GET + " " + "-y " + str(i2c_bus) + " " + i2c_addr_hex_value
                [returnCode, stdOut, errorText] = execute_bash_cmd(i2cCmd, self.logger_obj)

                if returnCode == 0:
                    return str_to_int(stdOut)
                else:
                    if errorText is None:
                        return [RES_CODE_ERROR, str(stdOut)]
                    else:
                        return [RES_CODE_ERROR, str(errorText)]

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
    #    data | ["error", reason]
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
        result = self.set_register_address_for_read(i2c_bus, i2c_addr, reg_addr)
        if isinstance(result, list):
            return result

        for _i in range(lengthInt):
            result = self.read_byte(i2c_bus, i2c_addr)
            if isinstance(result, list):
                return result
            else:
                # Convert the given string data to integer. Exit, if it failed.
                conv_to_int_result = str_to_int(result)
                if isinstance(conv_to_int_result, list):
                    # Invalid data gave from the I2C slave.
                    return conv_to_int_result
                else:
                    # Append the byte into the data
                    data.append(conv_to_int_result)

        return data

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
    #    "ok" | ["error", reason]
    #    data: integer
    #    reason: string
    # ===========================================================================
    def write_byte_data(self, i2c_bus, i2c_addr, reg_addr, reg_value):
        result = int_to_hex(i2c_addr)

        if isinstance(result, list):
            [_, reason] = result
            return [RES_CODE_ERROR, "Invalid i2c_addr " + str(i2c_addr) + " " + reason]

        else:
            # Save the hex value of the I2C address
            i2c_addr_hex_value = result

            result = int_to_hex(reg_addr)
            if isinstance(result, list):
                [_, reason] = result
                return [RES_CODE_ERROR, "Invalid reg_addr " + str(reg_addr) + " " + reason]
            else:
                # Save the hex value of the register address
                reg_addr_hex_value = result

                # I2C cmd- setup the register address to be read out
                result = int_to_hex(reg_value)
                if isinstance(result, list):
                    [_, reason] = result
                    return [RES_CODE_ERROR, "Invalid reg_value " + str(reg_value) + " " + reason]
                else:
                    # Save the hex value of the register value
                    reg_value_hex_value = result

                    i2cCmd = (I2C_PROGRAM_SET + " " + "-y " + str(i2c_bus) + " " +
                              i2c_addr_hex_value + " " + reg_addr_hex_value + " " +
                              reg_value_hex_value)
                    [returnCode, stdOut, errorText] = execute_bash_cmd(i2cCmd, self.logger_obj)

                    if returnCode == RETURN_CODE_SUCCESS:
                        return RES_CODE_OK
                    else:
                        if errorText is None:
                            return [RES_CODE_ERROR, str(stdOut)]
                        else:
                            return [RES_CODE_ERROR, str(errorText)]

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
    #    "ok" | ["error", reason]
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
            result = self.write_byte_data(i2c_bus, i2c_addr, reg_addr_runtime, theByte)
            if isinstance(result, list):
                return result
            else:
                # Increment reg_addr_runtime
                reg_addr_runtime = reg_addr_runtime + 1

        return RES_CODE_OK
