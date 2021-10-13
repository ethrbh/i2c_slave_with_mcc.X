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
#include "mcc_generated_files/memory.h"

/*
 * Define "internal" EEPROM to be read/write via I2C
 *
 */
volatile uint8_t SLAVE_EEPROM_SIZE = 128;
static uint8_t EEPROM_Buffer[] = {
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
    0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f,
    0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f,
    0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x4f,
    0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x5e, 0x5f,
    0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6e, 0x6f,
    0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x7b, 0x7c, 0x7d, 0x7e, 0x7f
};

volatile uint8_t i2c1SlaveAddr = 0x00;
uint8_t i2c1EEMemAddr = 0x00;
volatile bool isEEMemoryAddr = false;

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
    i2c1SlaveAddr = I2C1_Read() >> 1;

    /*
     * If SSP1STATbits.R_nW is 1, the next byte from MASTER will be the
     * EEPROM register address, thus isEEMemoryAddr signs this.
     */
    if (!I2C1_IsRead()) {
        isEEMemoryAddr = true;
    }

    return;
}

/*
 * MASTER device has been sent a READ request to the SLAVE device.
 * The SLAVE will send back data from EEPROM (aka SLAVE) to MASTER.
 */
static void EEPROM_SlaveSetWriteIntHandler(void) {
    if (i2c1EEMemAddr >= SLAVE_EEPROM_SIZE) {
        i2c1EEMemAddr = 0x00;
    }

    eeprom_write(0x20, i2c1EEMemAddr);

    uint8_t i2c1EEMemValue = EEPROM_Buffer[i2c1EEMemAddr++];

    eeprom_write(0x21, i2c1EEMemValue);

    I2C1_Write(i2c1EEMemValue);
    //I2C1_Write(1);
    return;
}

/*
 * MASTER device has been sent a WRITE request to the SLAVE device (aka EEPROM).
 * SLAVE device should read data from the I2C bus, and saves into the pointed
 * register address in the EEPROM.
 */
static void EEPROM_SlaveSetReadIntHandler(void) {
    /*
     * If isEEMemoryAddr true, SSPBUF register should contains the EEPROM
     * register address.
     */
    if (isEEMemoryAddr) {

        // Read EEPROM register address
        i2c1EEMemAddr = I2C1_Read();

        // If the given address higher than the max EEPROM size, start
        // reading EEPROM from the 0x00 address.
        if (i2c1EEMemAddr >= SLAVE_EEPROM_SIZE) {
            i2c1EEMemAddr = 0x00;
        }

        // Clear the isEEMemoryAddr flag and exit from the function.
        isEEMemoryAddr = false;
        return;
    } else {
        // Read value to be write into EEPROM at the address
        uint8_t i2c1EEMemValue = I2C1_Read();

        // Save the data into the internal EE too, just for test purpose
        eeprom_write(i2c1EEMemAddr, i2c1EEMemAddr);
        uint8_t i2c1EEMemAddrTmp = i2c1EEMemAddr + 16;
        eeprom_write(i2c1EEMemAddrTmp, i2c1EEMemValue);

        // Write the value into the EEPROM
        EEPROM_Buffer[i2c1EEMemAddr++] = i2c1EEMemValue;

        return;
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

    // Open I2C device
    I2C1_Open();

    // Configure handler functions to be used.
    // This will overwrite the handlers were set by I2C1_Open().
    I2C1_SlaveSetAddrIntHandler(EEPROM_I2C1_SlaveSetAddrIntHandler);
    I2C1_SlaveSetWriteIntHandler(EEPROM_SlaveSetWriteIntHandler);
    I2C1_SlaveSetReadIntHandler(EEPROM_SlaveSetReadIntHandler);

    while (1) {
        // Add your application code
        //IO_RA2_SetHigh();
    }
}
/**
 End of File
 */