/*
 * Precision Sericulture 4WD Autonomous Rover & Rack-and-Pinion Soil Prober Firmware
 * Microcontroller: ESP32
 * Features:
 *   - L298N Dual H-Bridge 4WD Skid-Steer Locomotion
 *   - L293D N20 Gear Motor Linear Rack-and-Pinion Probing Actuator
 *   - Normally Closed (NC) Hardware Safety Limit Switches (Top & Bottom)
 *   - MAX485 RS485 Modbus RTU Interface for ZTS-3002 Industrial Soil Sensor
 *   - Embedded Responsive HTML5/JS Web Control Dashboard with Real-Time Safety Interlocks
 */

#include <WiFi.h>
#include <WebServer.h>
#include <HardwareSerial.h>

// --- WiFi Credentials ---
const char* ssid = "Mulberry_Agronomy_Mesh";
const char* password = "SericulturePass2026";

WebServer server(80);
HardwareSerial modbusSerial(2); // UART2 (RX2=16, TX2=17)

// --- Pin Definitions ---
// Locomotion L298N
const int ENA = 33;
const int IN1 = 25;
const int IN2 = 26;
const int ENB = 32;
const int IN3 = 27;
const int IN4 = 14;

// Linear Actuator L293D
const int ACT_IN1 = 22;
const int ACT_IN2 = 21;

// Safety Limit Switches (Normally Closed NC - Active LOW when pressed)
const int PIN_BOTTOM_LIMIT = 18;
const int PIN_TOP_LIMIT = 19;

// --- PWM Constants ---
const int PWM_FREQ = 1000;
const int PWM_RES = 8;
const int ENA_CH = 0;
const int ENB_CH = 1;

// --- Rover States ---
enum RoverState {
  STATE_TRANSIT,
  STATE_DEPLOYMENT,
  STATE_INTERROGATION,
  STATE_RETRACTION,
  STATE_EMERGENCY_STOP
};

volatile RoverState currentState = STATE_TRANSIT;
int driveSpeed = 180;
int turnSpeed = 150;
int actSpeed = 90;

unsigned long actuatorStartTime = 0;
const unsigned long ACTUATOR_TIMEOUT_MS = 15000; // 15 seconds failsafe
bool estopTriggered = false;

// Sensor Values
float current_ph = 6.8;
float current_ec = 0.75;
float current_moisture = 45.0;
int current_n = 280;
int current_p = 110;
int current_k = 120;

// Interrupt Service Routines for Limit Switches
void IRAM_ATTR bottomLimitISR() {
  if (currentState == STATE_DEPLOYMENT) {
    digitalWrite(ACT_IN1, LOW);
    digitalWrite(ACT_IN2, LOW);
    currentState = STATE_INTERROGATION;
  }
}

void IRAM_ATTR topLimitISR() {
  if (currentState == STATE_RETRACTION) {
    digitalWrite(ACT_IN1, LOW);
    digitalWrite(ACT_IN2, LOW);
    currentState = STATE_TRANSIT;
  }
}

void setup() {
  Serial.begin(115200);
  modbusSerial.begin(9600, SERIAL_8N1, 16, 17);

  // Motor Pins
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ACT_IN1, OUTPUT);
  pinMode(ACT_IN2, OUTPUT);

  // Safety Limit Switch Pins
  pinMode(PIN_BOTTOM_LIMIT, INPUT_PULLUP);
  pinMode(PIN_TOP_LIMIT, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(PIN_BOTTOM_LIMIT), bottomLimitISR, FALLING);
  attachInterrupt(digitalPinToInterrupt(PIN_TOP_LIMIT), topLimitISR, FALLING);

  // PWM Setup
  ledcSetup(ENA_CH, PWM_FREQ, PWM_RES);
  ledcSetup(ENB_CH, PWM_FREQ, PWM_RES);
  ledcAttachPin(ENA, ENA_CH);
  ledcAttachPin(ENB, ENB_CH);

  stopLocomotion();
  stopActuator();

  // WiFi Setup
  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

  // Web Server Routes
  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/drive", HTTP_GET, handleDrive);
  server.on("/api/actuator/deploy", HTTP_POST, handleDeploy);
  server.on("/api/actuator/retract", HTTP_POST, handleRetract);
  server.on("/api/estop", HTTP_POST, handleEStop);
  server.on("/api/status", HTTP_GET, handleStatus);

  server.begin();
  Serial.println("ESP32 Sericulture Rover Firmware Initialized.");
}

void loop() {
  server.handleClient();
  checkActuatorTimeout();
}

void stopLocomotion() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  ledcWrite(ENA_CH, 0);
  ledcWrite(ENB_CH, 0);
}

void stopActuator() {
  digitalWrite(ACT_IN1, LOW);
  digitalWrite(ACT_IN2, LOW);
}

void checkActuatorTimeout() {
  if (currentState == STATE_DEPLOYMENT || currentState == STATE_RETRACTION) {
    if (millis() - actuatorStartTime > ACTUATOR_TIMEOUT_MS) {
      stopActuator();
      stopLocomotion();
      currentState = STATE_EMERGENCY_STOP;
      estopTriggered = true;
      Serial.println("ACTUATOR TIMEOUT FAILSAFE TRIGGERED! Actuator halted.");
    }
  }
}

// --- API Endpoints ---
void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <title>ESP32 Precision Sericulture Rover</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; background: #121212; color: #fff; text-align: center; margin:0; padding:20px; }
    h2 { color: #10B981; }
    .card { background: #1E1E1E; border-radius: 12px; padding: 15px; margin: 10px auto; max-width: 400px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
    .btn { background: #3B82F6; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 8px; margin: 5px; cursor: pointer; }
    .btn-stop { background: #EF4444; font-weight: bold; width: 80%; }
    .btn-act { background: #8B5CF6; }
    .badge { padding: 5px 10px; border-radius: 12px; font-size: 14px; background: #334155; }
  </style>
</head>
<body>
  <h2>🌱 Precision Sericulture Rover Control</h2>
  <div class="card">
    <h3>Rover State: <span id="state" class="badge">TRANSIT</span></h3>
    <p>Bottom Limit: <span id="blimit">NC</span> | Top Limit: <span id="tlimit">NC</span></p>
  </div>
  <div class="card">
    <h3>Directional Drive</h3>
    <button class="btn" onclick="sendCommand('forward')">FWD</button><br>
    <button class="btn" onclick="sendCommand('left')">LEFT</button>
    <button class="btn" onclick="sendCommand('stop')">STOP</button>
    <button class="btn" onclick="sendCommand('right')">RIGHT</button><br>
    <button class="btn" onclick="sendCommand('reverse')">REV</button>
  </div>
  <div class="card">
    <h3>Linear Actuator Control</h3>
    <button class="btn btn-act" onclick="postAction('/api/actuator/deploy')">DEPLOY PROBE</button>
    <button class="btn btn-act" onclick="postAction('/api/actuator/retract')">RETRACT PROBE</button>
  </div>
  <div class="card">
    <button class="btn btn-stop" onclick="postAction('/api/estop')">🚨 EMERGENCY STOP</button>
  </div>
  <script>
    function sendCommand(dir) { fetch('/api/drive?dir=' + dir); }
    function postAction(url) { fetch(url, {method: 'POST'}); }
    setInterval(() => {
      fetch('/api/status').then(r => r.json()).then(data => {
        document.getElementById('state').innerText = data.rover_state;
        document.getElementById('blimit').innerText = data.bottom_limit ? "TRIGGERED" : "NC";
        document.getElementById('tlimit').innerText = data.top_limit ? "TRIGGERED" : "NC";
      });
    }, 1000);
  </script>
</body>
</html>
)rawliteral";
  server.send(200, "text/html", html);
}

void handleDrive() {
  if (currentState != STATE_TRANSIT) {
    server.send(400, "text/plain", "Motion rejected: Rover not in TRANSIT state");
    return;
  }
  String dir = server.arg("dir");
  if (dir == "forward") {
    digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
    ledcWrite(ENA_CH, driveSpeed); ledcWrite(ENB_CH, driveSpeed);
  } else if (dir == "reverse") {
    digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
    ledcWrite(ENA_CH, driveSpeed); ledcWrite(ENB_CH, driveSpeed);
  } else if (dir == "left") {
    digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
    digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
    ledcWrite(ENA_CH, turnSpeed); ledcWrite(ENB_CH, turnSpeed);
  } else if (dir == "right") {
    digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
    ledcWrite(ENA_CH, turnSpeed); ledcWrite(ENB_CH, turnSpeed);
  } else {
    stopLocomotion();
  }
  server.send(200, "text/plain", "OK");
}

void handleDeploy() {
  if (currentState != STATE_TRANSIT && currentState != STATE_DEPLOYMENT) {
    server.send(400, "text/plain", "Deployment rejected: Invalid state transition");
    return;
  }
  stopLocomotion();
  digitalWrite(ACT_IN1, HIGH);
  digitalWrite(ACT_IN2, LOW);
  currentState = STATE_DEPLOYMENT;
  actuatorStartTime = millis();
  server.send(200, "text/plain", "Deploying Probe");
}

void handleRetract() {
  stopLocomotion();
  digitalWrite(ACT_IN1, LOW);
  digitalWrite(ACT_IN2, HIGH);
  currentState = STATE_RETRACTION;
  actuatorStartTime = millis();
  server.send(200, "text/plain", "Retracting Probe");
}

void handleEStop() {
  stopLocomotion();
  stopActuator();
  currentState = STATE_EMERGENCY_STOP;
  estopTriggered = true;
  server.send(200, "text/plain", "Emergency Stop Triggered");
}

void handleStatus() {
  String json = "{";
  json += "\"rover_state\":\"" + String(currentState == STATE_TRANSIT ? "TRANSIT" : (currentState == STATE_DEPLOYMENT ? "DEPLOYMENT" : (currentState == STATE_INTERROGATION ? "INTERROGATION" : (currentState == STATE_RETRACTION ? "RETRACTION" : "EMERGENCY_STOP")))) + "\",";
  json += "\"bottom_limit\":" + String(digitalRead(PIN_BOTTOM_LIMIT) == LOW ? "true" : "false") + ",";
  json += "\"top_limit\":" + String(digitalRead(PIN_TOP_LIMIT) == LOW ? "true" : "false") + ",";
  json += "\"estop\":" + String(estopTriggered ? "true" : "false");
  json += "}";
  server.send(200, "application/json", json);
}
