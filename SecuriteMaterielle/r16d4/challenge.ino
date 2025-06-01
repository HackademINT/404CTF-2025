int value = 0;
int input_pin[16] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, A6, A7};

void setup() {
  for(int i = 0; i < 16; i++) {
    pinMode(input_pin[i], INPUT);
  }
  
  pinMode(A0, OUTPUT);
  pinMode(A1, OUTPUT);
  pinMode(A2, OUTPUT);
  pinMode(A3, OUTPUT);
}

void loop() {
  
  value = -1;
  for(int i = 0; i < 16; i++) {
    if (digitalRead(input_pin[i]) == HIGH) {
      value++;
    }
  }
  
  if (value & 1) {
    digitalWrite(A3, HIGH);
  } else {
    digitalWrite(A3, LOW);
  }
  
  value = value >> 1;
  if (value & 1) {
    digitalWrite(A2, HIGH);
  } else {
    digitalWrite(A2, LOW);
  }
  
  value = value >> 1;
  if (value & 1) {
    digitalWrite(A1, HIGH);
  } else {
    digitalWrite(A1, LOW);
  }
  
  value = value >> 1;
  if (value & 1) {
    digitalWrite(A0, HIGH);
  } else {
    digitalWrite(A0, LOW);
  }
  
  delay(10);
}
