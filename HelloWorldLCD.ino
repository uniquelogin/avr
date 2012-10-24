#include <LiquidCrystal.h>

LiquidCrystal lcd(4, 6, 5, 10, 11, 12, 13);

char msg[121];
char lcdBuf[81];
int MAX_MSG;
int msgLen;
int msgMode;
int msgReceivedLen;
int voltage;
int targetVoltage;
unsigned long prevMillis;

void resetMsg() {
  msgLen = 0;
  msgMode = 0; 
  msgReceivedLen = -2;
}

void processMsg() {
  int n;
  int row;
  char* ptrEnd;
  char* ptr;
  char* ptrSrc;
  if (msgMode == 1) {
    lcd.clear();
  }
  else if (msgMode == 2 && msgLen >= 1) {
    row = byte(msg[0]) - 1;
    if (row > 3) {
      return;
    }
    n = msgLen - 1;
    if (n > 20) {
      n = 20;
    }
    ptr = lcdBuf + (row*20);  
    ptrSrc = msg + 1;
    ptrEnd = ptrSrc + n;
    while (ptrSrc != ptrEnd) {
      *ptr = *ptrSrc;
      ++ptr;
      ++ptrSrc;
    }
    ptrEnd = ptr + (20 - n);
    while (ptr < ptrEnd) {
      *ptr = ' ';
      ++ptr;
    }
  }
  else if (msgMode == 4) {
    lcdBuf[80] = 0;
    lcd.setCursor(0, 0);
    lcd.print(lcdBuf);
  }
  else if (msgMode == 3 && msgLen >= 1) {
    targetVoltage = byte(msg[0]); 
  }
}

void setup() {
  int i;
  
  MAX_MSG = 120;
  analogWrite(3, 0); 
  prevMillis = 0;  
  targetVoltage = 0;
  voltage = 0;
  lcd.begin(20, 4);
  lcd.clear();
  for (i = 0; i < 80; i++) {
    lcdBuf[i] = ' '; 
  }
  resetMsg();
  Serial.begin(19200);
  lcd.print("INIT OK");
}


void loop() {
  unsigned long timeDelta;
  unsigned long maxDelta;
  int inByte;
  int voltDiff;
  
  // update voltage
  if (targetVoltage != voltage) {
     voltDiff = targetVoltage - voltage;
     timeDelta = millis() - prevMillis;
     maxDelta = 20;
     if (voltDiff < -5 || voltDiff > 5)
       maxDelta = 10;
     if (voltDiff < -10 || voltDiff > 10)
       maxDelta = 5;
     if (timeDelta > maxDelta) {
       prevMillis = millis();
       if (targetVoltage > voltage)
         voltage += 1;
       else
         voltage -= 1;
       analogWrite(3, voltage);
     }
  }
  
  // read and process input
  if (Serial.available() == 0) {
    return;
  }
  
  inByte = Serial.read();
  if (inByte == 0) {
      resetMsg();
  }
  else {     
     if (msgReceivedLen == -2) {
       msgMode = inByte;
       if (msgMode == 1 || msgMode == 4) {
         msgLen = 0;
         msgReceivedLen += 1; // skip reading message length
       }
     }
     else if (msgReceivedLen == -1) {
       msgLen = inByte;
     }
     else if (msgReceivedLen < MAX_MSG) {
       msg[msgReceivedLen] = inByte;
       msg[msgReceivedLen + 1] = 0;
     }
     
     msgReceivedLen += 1;
     if (msgReceivedLen >= 0 && msgReceivedLen >= msgLen) {
       processMsg();
       resetMsg(); 
     }
  }
}

