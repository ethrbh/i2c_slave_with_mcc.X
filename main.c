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
#include "test.h"

/*
 * Define "internal" EEPROM to be read/write via I2C
 *
 */
volatile uint8_t SLAVE_EEPROM_SIZE = 64;
static uint8_t EEPROM_Buffer[] = {
    0x00, 0x01, 0x022, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
    0x10, 0x11, 0x12, 0x13, 0x16, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
    0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f,
    0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f
};

static uint8_t MASTER_Buffer[] = {
    0x01, 0xFF, 0xFE, 0xFD, 0xFC, 0xFB, 0xFA, 0xF9, 0xF8, 0xF7, 0xF6, 0xF5, 0xF4, 0xF3, 0xF2, 0xF1, 0xF0
};

volatile uint8_t i2c1SlaveAddr = 0x00;
uint8_t i2c1EEMemAddr = 0x00;

#define EE_ADDR_NONE  0
#define  EE_ADDR_WAITING 1
#define  EE_ADDR_RECEIVED 2
volatile uint8_t isEEMemoryAddrState = EE_ADDR_NONE;

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
    //eeprom_write(tmpCntI2C2++, i2c1SlaveAddr);


    /*
     * If SSP1STATbits.R_nW is 1, the next byte from MASTER will be the
     * EEPROM register address, thus isEEMemoryAddr signs this.
     */
    //eeprom_write(tmpCntI2C++, 0x10);

    if (!I2C1_IsRead()) {
        // Master sent a WRITE request
        //eeprom_write(tmpCntI2C++, 0x12);
        isEEMemoryAddrState = EE_ADDR_WAITING;

        //        if (isEEMemoryAddrState == EE_ADDR_NONE) {
        //            //eeprom_write(tmpCntI2C++, 0x13);
        //            // If no register address received yet,
        //            // the next byte on the I2C bus will be that.
        //            isEEMemoryAddrState = EE_ADDR_WAITING;
        //        }
    }

    return;
}

/*
 * MASTER device has been sent a READ request to the SLAVE device.
 * The SLAVE should WRITE data to MASTER.
 */
static void EEPROM_SlaveSetWriteIntHandler(void) {
    if (i2c1EEMemAddr >= SLAVE_EEPROM_SIZE) {
        i2c1EEMemAddr = 0;
    }

    uint8_t i2c1EEMemValue = EEPROM_Buffer[i2c1EEMemAddr++];

    if (!SSP1CON2bits.ACKSTAT) {
        //eeprom_write(tmpCntI2C++, 0x21);

        I2C1_Write(i2c1EEMemValue);
        IO_RA2_Toggle();

        //while (SSPSTATbits.BF);
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
    //eeprom_write(tmpCntI2C++, 0x30);
    if (isEEMemoryAddrState == EE_ADDR_WAITING) {
        //eeprom_write(tmpCntI2C++, 0x31);

        // Read EEPROM register address
        i2c1EEMemAddr = I2C1_Read();
        //eeprom_write(tmpCntI2C2++, i2c1EEMemAddr);

        // If the given address higher than the max EEPROM size, start
        // reading EEPROM from the 0x00 address.
        if (i2c1EEMemAddr >= SLAVE_EEPROM_SIZE) {
            i2c1EEMemAddr = 0;
        }
        //eeprom_write(tmpCntI2C++, 0x32);
        //eeprom_write(tmpCntI2C++, i2c1EEMemAddr);

        isEEMemoryAddrState = EE_ADDR_RECEIVED;

        return;
    } else {
        //eeprom_write(tmpCntI2C++, 0x33);
        if (isEEMemoryAddrState == EE_ADDR_RECEIVED) {
            //eeprom_write(tmpCntI2C++, 0x34);

            // Read value to be write into EEPROM at the address
            uint8_t i2c1EEMemValue = I2C1_Read();
            //eeprom_write(tmpCntI2C2++, i2c1EEMemValue);

            // Save the data into the internal EE too, just for test purpose
            //eeprom_write(tmpCntI2C++, i2c1EEMemAddr);
            //eeprom_write(tmpCntI2C++, i2c1EEMemValue);

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

    // Open I2C device
    I2C1_Open();

    // Configure handler functions to be used.
    // This will overwrite the handlers were set by I2C1_Open().
    I2C1_SlaveSetAddrIntHandler(EEPROM_I2C1_SlaveSetAddrIntHandler);
    I2C1_SlaveSetWriteIntHandler(EEPROM_SlaveSetWriteIntHandler);
    I2C1_SlaveSetReadIntHandler(EEPROM_SlaveSetReadIntHandler);

    static uint8_t Memory_Index = 1;
    static uint8_t SlaveAddress = 103;

    static uint8_t value1 = 0x00;
    static uint8_t value2 = 0x00;
    static uint8_t value3 = 0x00;
    value1 = I2C2_Read1ByteRegister(SlaveAddress, 0x02);
    value2 = I2C2_Read1ByteRegister(SlaveAddress, 0x14);
    value3 = value1 + value2;
    while (1) {
        // Add your application code
        //IO_RA2_Toggle();
        //printf("hello\n");
        //__delay_ms(200);

        //MASTER_Buffer[0] = Memory_Index;
        /* 1 byte memory address and 8 bytes data from the same buffer. Mysil */
        //I2C2_WriteNBytes(SlaveAddress, MASTER_Buffer, 9);
        //I2C2_Write1ByteRegister(SlaveAddress, 0x02, 0xcc);

        IO_RA2_Toggle();

        //I2C2_ReadDataBlock(SlaveAddress, Memory_Index, &MASTER_Buffer[1], 16);
        //Memory_Index += 8;
        //I2C2_Read1ByteRegister(SlaveAddress, 0x02);
        __delay_ms(200);
    }
}
/**
 End of File
 */