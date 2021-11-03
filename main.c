/**
  Generated Main Source File

  Company:
    Microchip Technology Inc.

  File Name:
    main.c

  Summary:
    This is the main file generated using PIC10 / PIC12 / PIC16 / PIC18 MCUs

  Description:
    This header file provides implementations for driver APIs for all modules selected in the GUI.
    Generation Information :
        Product Revision  :  PIC10 / PIC12 / PIC16 / PIC18 MCUs - 1.81.6
        Device            :  PIC16F18325
        Driver Version    :  2.00
 */

/*
    (c) 2018 Microchip Technology Inc. and its subsidiaries.

    Subject to your compliance with these terms, you may use Microchip software and any
    derivatives exclusively with Microchip products. It is your responsibility to comply with third party
    license terms applicable to your use of third party software (including open source software) that
    may accompany Microchip software.

    THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
    EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY
    IMPLIED WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS
    FOR A PARTICULAR PURPOSE.

    IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
    INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
    WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP
    HAS BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO
    THE FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL
    CLAIMS IN ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT
    OF FEES, IF ANY, THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS
    SOFTWARE.
 */

#include "mcc_generated_files/mcc.h"
#include "mcc_generated_files/examples/i2c2_master_example.h" /* For I2C Master  application interface. */

/*
 * Define "internal" EEPROM to be read/write via I2C
 *
 */
volatile uint8_t SLAVE_EEPROM_SIZE = 64;
static uint8_t EEPROM_Buffer[] = {
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
    0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f,
    0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f
};

volatile uint8_t i2c1SlaveAddr = 0x00;
uint8_t i2c1EEMemAddr = 0x00;

#define EE_ADDR_NONE  0
#define  EE_ADDR_WAITING 1
#define  EE_ADDR_RECEIVED 2
volatile uint8_t isEEMemoryAddrState = EE_ADDR_NONE;

// If I2C MASTER device also has to be run, set this define to true,
// otherwise this should be false.
#define isI2CMasterDeviceUsed true

/*
 * Handlers to be used by I2C1 device
 */
// ADDRESS Event Interrupt Handler
static void EEPROM_I2C1_SlaveSetAddrIntHandler(void);
// I2C Master Write data into EEPROM
static void EEPROM_SlaveSetWriteIntHandler(void);
// Reading EEPROM register by I2C MASTER device
static void EEPROM_SlaveSetReadIntHandler(void);

/*
 * Handler function to be sued for store received
 * data from MASTER.
 * If
 */
static void EEPROM_I2C1_SlaveSetAddrIntHandler(void) {
    /*
     * Note: Getting the address of Slave device is done by reading
     *       SSP1BUF and shifting the value with 1 to right.
     *       The 7 bit slave address is represented by the 7 bits
     *       from left hand side.
     */
    i2c1SlaveAddr = I2C1_Read();

    /*
     * If SSP1STATbits.R_nW is 1, the next byte from MASTER will be the
     * EEPROM register address, thus isEEMemoryAddr signs this.
     */
    if (!I2C1_IsRead()) {
        // Master sent a WRITE request, the next byte from MASTER
        // should be the register address to be read/write.
        isEEMemoryAddrState = EE_ADDR_WAITING;
    }

    return;
}

/*
 * MASTER device has been sent a READ request to the SLAVE device.
 * The SLAVE should WRITE the value of the EEPROM, pointed by the i2c1EEMemAddr
 * on the I2C BUS.
 */
static void EEPROM_SlaveSetWriteIntHandler(void) {
    if (i2c1EEMemAddr >= SLAVE_EEPROM_SIZE) {
        i2c1EEMemAddr = 0;
    }

    uint8_t i2c1EEMemValue = EEPROM_Buffer[i2c1EEMemAddr++];

    if (!SSP1CON2bits.ACKSTAT) {
        I2C1_Write(i2c1EEMemValue);
    }

    return;
}

/*
 * MASTER device has been sent a WRITE request to the SLAVE device (aka EEPROM).
 * SLAVE device should READ data from the I2C bus, and saves into the pointed
 * register address in the EEPROM.
 */
static void EEPROM_SlaveSetReadIntHandler(void) {
    /*
     * If isEEMemoryAddr true, SSPBUF register should contains the EEPROM
     * register address.
     */
    if (isEEMemoryAddrState == EE_ADDR_WAITING) {
        // Read EEPROM register address
        i2c1EEMemAddr = I2C1_Read();
        // If the given address higher than the max EEPROM size, start
        // reading EEPROM from the 0x00 address.
        if (i2c1EEMemAddr >= SLAVE_EEPROM_SIZE) {
            i2c1EEMemAddr = 0;
        }

        isEEMemoryAddrState = EE_ADDR_RECEIVED;

        return;
    } else {
        if (isEEMemoryAddrState == EE_ADDR_RECEIVED) {

            // Read value to be write into EEPROM at the address
            uint8_t i2c1EEMemValue = I2C1_Read();

            // Write the value into the EEPROM
            EEPROM_Buffer[i2c1EEMemAddr++] = i2c1EEMemValue;

            return;
        }
    }
}

/*
                         Main application
 */
void main(void) {
    // initialize the device
    SYSTEM_Initialize();

    // When using interrupts, you need to set the Global and Peripheral Interrupt Enable bits
    // Use the following macros to:

    // Enable the Global Interrupts
    INTERRUPT_GlobalInterruptEnable();

    // Enable the Peripheral Interrupts
    INTERRUPT_PeripheralInterruptEnable();

    // Disable the Global Interrupts
    //INTERRUPT_GlobalInterruptDisable();

    // Disable the Peripheral Interrupts
    //INTERRUPT_PeripheralInterruptDisable();

    // Configure handler functions to be used by the I2C SLAVE device.
    // This will overwrite the handlers were set by I2C1_Open().
    I2C1_Open();
    I2C1_SlaveSetAddrIntHandler(EEPROM_I2C1_SlaveSetAddrIntHandler);
    I2C1_SlaveSetWriteIntHandler(EEPROM_SlaveSetWriteIntHandler);
    I2C1_SlaveSetReadIntHandler(EEPROM_SlaveSetReadIntHandler);

    // Execute I2C MASTER operations
    if (isI2CMasterDeviceUsed) {

        // The EEPROM register address in the SLAVE device
        // to be read/write.
        static uint8_t i2c1EEMemAddr_Master = 0x00;

        // The buffer to be used by I2C MASTER from/to read/write
        // data from/to I2C SLAVE device.
        static uint8_t i2cBuffer_Master[] = {
            0x00,
            0xFF, 0xFE, 0xFD, 0xFC, 0xFB, 0xFA, 0xF9, 0xF8, 0xF7, 0xF6, 0xF5, 0xF4, 0xF3, 0xF2, 0xF1, 0xF0
        };

        // The I2C SLAVE device address
        static uint8_t i2cSlaveAddress = 103;

        // 1. Write N bytes to the I2C SLAVE.
        //    Number of bytes is 4 (1 address, 3 data).
        //    The i2cBuffer_Master is used for this,
        //    where the 1st EEPROM register for the write is in the 0. position
        //    in the i2cBuffer_Master, and the next bytes (1,2, ect) are the data
        //    to be write into the SLAVE.
        uint8_t byteNumber = 4;
        I2C2_WriteNBytes(i2cSlaveAddress, i2cBuffer_Master, byteNumber);

        // 2. Read a block from I2C SLAVE. Start EEPROM register of the block
        //    is 0x10, read 3 bytes, and save the read byte into i2cBuffer_Master
        //    buffer from index 1.
        i2c1EEMemAddr_Master = 0x10;
        uint8_t byteNumber = 3;
        I2C2_ReadDataBlock(i2cSlaveAddress, i2c1EEMemAddr_Master, &i2cBuffer_Master[1], byteNumber);

        // 3. Read a block from I2C SLAVE. Start EEPROM register of the block
        //    is 0x00, read 3 bytes, and save the read byte into i2cBuffer_Master
        //    buffer from index 1.
        i2c1EEMemAddr_Master = 0x00;
        uint8_t byteNumber = 3;
        I2C2_ReadDataBlock(i2cSlaveAddress, i2c1EEMemAddr_Master, &i2cBuffer_Master[1], byteNumber);

        // 4. Write value 0x12 into EEPROM register 0x03
        i2c1EEMemAddr_Master = 0x03;
        I2C2_Write1ByteRegister(i2cSlaveAddress, i2c1EEMemAddr_Master, 0x12);

        // 5. Read data from I2C SLAVE at EEPROM register 0x03
        I2C2_Read1ByteRegister(i2cSlaveAddress, i2c1EEMemAddr_Master);

        IO_RA2_Toggle();
    }
    while (1) {
    }
}
/**
 End of File
 */