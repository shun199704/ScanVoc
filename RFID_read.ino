#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>

#define RST_PIN    A0     // Reset pin
#define SS_PIN     10     // Chip select pin
#define I2C_SLAVE_ADDRESS 0x08  // I2C address for the Arduino

MFRC522 mfrc522(SS_PIN, RST_PIN);    // Create MFRC522 instance

MFRC522::MIFARE_Key key;  // Key storage

byte sector = 15;   // Sector to read/write, possible values: 0~15
byte block = 1;     // Block to read/write, possible values: 0~3

unsigned long previousMillis = 0;
const long interval = 1000;  // interval for 1 second

// Buffer to hold block data, MIFARE_Read() requires at least 18 bytes to hold 16 bytes of data.
byte buffer[18];

void readBlock(byte _sector, byte _block, byte _blockData[]) {
  if (_sector < 0 || _sector > 15 || _block < 0 || _block > 3) {
    Serial.println(F("Wrong sector or block number."));
    return;
  }

  byte blockNum = _sector * 4 + _block;  // Calculate actual block number (0~63)
  byte trailerBlock = _sector * 4 + 3;   // Control block number

  // Authenticate key
  MFRC522::StatusCode status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(mfrc522.uid));
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("PCD_Authenticate() failed: "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    return;
  }

  byte buffersize = 18;
  status = (MFRC522::StatusCode) mfrc522.MIFARE_Read(blockNum, _blockData, &buffersize);
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("MIFARE_read() failed: "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    return;
  }

  Serial.println(F("Data was read."));
}

void setup() {
  Serial.begin(9600);
  SPI.begin();               // Initialize SPI bus
  mfrc522.PCD_Init();        // Initialize MFRC522
  Wire.begin(I2C_SLAVE_ADDRESS);  // Initialize I2C as slave
  Wire.onRequest(requestEvent);  // Register function to handle requests from master
  pinMode(2,OUTPUT);
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;  // Prepare key (used for both key A and key B), default value is 6 x 0xFF.
  }
}

void loop() {
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    readBlock(sector, block, buffer);   // Read block data
    Serial.flush();
    mfrc522.PICC_HaltA();  // Halt PICC
    mfrc522.PCD_StopCrypto1();  // Stop encryption on PCD
  }
}

void requestEvent() {
  if (buffer[0] != 0){
    if (millis() - previousMillis >= interval) {
      digitalWrite(2, HIGH);
      previousMillis = millis();  // save the last time you blinked the LED
    }
    Wire.write(buffer[0]);  // Send 16 bytes of block data
    Serial.println((char)buffer[0]);
    digitalWrite(2,LOW);
    memset(buffer, 0, sizeof(buffer));
    }  // Clear buffer before reading
}
