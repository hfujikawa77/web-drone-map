# Web Drone Map

Web Drone Map is a user-friendly web application that visualizes the position and HUD (Heads-Up Display) of an ArduPilot drone directly in your browser. This application is designed to evaluate the feasibility of implementing server-side functionality in both Python and JavaScript.

## Setup

To get started, you need to install the required dependencies. You can choose between Python and JavaScript:

### For Python:
```bash
pip install flask flask-socketio pymavlink mavproxy
```

### For JavaScript:
```bash
npm install express socket.io node-mavlink
```

## Running the Application

Follow these steps to run the application:

1. **Run the Simulator**  
   To easily test the simulation of the ArduPilot drone, it is convenient to use the built-in simulator of Mission Planner. Follow these steps:
   1. Install Mission Planner.
   2. After launching, click the Simulation button in the top menu.
   3. Select Multirotor on the next screen.
   4. Click the Stable button in the dialog.
  
   The ArduPilot simulator will start and begin listening on tcp:127.0.0.1:5762. For more details, visit:  
   [Mission Planner Simulation Guide](https://ardupilot.org/planner/docs/mission-planner-simulation.html)

2. **Forward Telemetry**  
   Use the following command to forward telemetry data:
   ```bash
   mavproxy.py --master=tcp:127.0.0.1:5762 --out=udp:127.0.0.1:14551
   ```

3. **Start the Server**  
   Depending on your chosen language, start the server with one of the following commands:
   - For Python:
     ```bash
     python server.py
     ```
   - For JavaScript:
     ```bash
     node server.js
     ```

4. **Open the Client**  
   Launch your web browser and navigate to:  
   [http://localhost:3000/](http://localhost:3000/)  
   ![Drone HUD](image.png)
