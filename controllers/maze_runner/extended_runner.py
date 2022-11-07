from controller import Robot


class MazeRunner(Robot):
    def __init__(self):
        super().__init__()
        # Get simulation step length.
        self.timeStep = int(self.getBasicTimeStep())
        self.distance_sensor_data = None
        self.wall_collision_threshold = 2500.0

        self.black_circles_detected = 0
        self.init_time = 0.0

        self.robot_state = "halting"
        self.robot_previous_state = "halting"

        self.ground_left = 0.0
        self.ground_right = 0.0
        self.black_circle_threshold = 500.0

        # Constants of the Thymio II motors and distance sensors.
        self.maxMotorVelocity = 6

        # Get left and right wheel motors.
        self.leftMotor = self.getDevice("motor.left")
        self.rightMotor = self.getDevice("motor.right")

        # Frontal distance sensors that can be use to detect the walls.
        self.outerLeftSensor = self.getDevice("prox.horizontal.0")
        self.centralLeftSensor = self.getDevice("prox.horizontal.1")
        self.centralSensor = self.getDevice("prox.horizontal.2")
        self.centralRightSensor = self.getDevice("prox.horizontal.3")
        self.outerRightSensor = self.getDevice("prox.horizontal.4")

        # Enable sensors.
        self.outerLeftSensor.enable(self.timeStep)
        self.centralLeftSensor.enable(self.timeStep)
        self.centralSensor.enable(self.timeStep)
        self.centralRightSensor.enable(self.timeStep)
        self.outerRightSensor.enable(self.timeStep)

        # Get and enable ground sensors to detect the black circles.
        self.groundLeftSensor = self.getDevice("prox.ground.0")
        self.groundRightSensor = self.getDevice("prox.ground.1")
        self.groundLeftSensor.enable(self.timeStep)
        self.groundRightSensor.enable(self.timeStep)

        # Disable motor PID control mode.
        self.leftMotor.setPosition(float(0.0))
        self.rightMotor.setPosition(float(0.0))

        self.init_time = self.getTime()

        # Set ideal motor velocity.
        self.velocity = 0.7 * self.maxMotorVelocity

    def get_and_print_distance_sensor_data(self, print_data=True):
        data = {"central": self.centralSensor.getValue(),
                "central_left": self.centralLeftSensor.getValue(),
                "central_right": self.centralRightSensor.getValue(),
                "outer_left": self.outerLeftSensor.getValue(),
                "outer_right": self.outerRightSensor.getValue()}
        self.distance_sensor_data = data
        if print_data:
            print(self.distance_sensor_data)

    def robot_go(self):
        self.leftMotor.setPosition(float('inf'))
        self.rightMotor.setPosition(float('inf'))
        if self.robot_state != "going_forward":
            self.robot_previous_state = self.robot_state
            self.robot_state = "going_forward"

    def robot_stop(self):
        self.leftMotor.setPosition(float(0.0))
        self.rightMotor.setPosition(float(0.0))
        if self.robot_state != "halting":
            self.robot_previous_state = self.robot_state
            self.robot_state = "halting"

    def robot_back_of(self):
        self.leftMotor.setVelocity(-self.velocity)
        self.rightMotor.setVelocity(-self.velocity)
        if self.robot_state != "backing_off":
            self.robot_previous_state = self.robot_state
            self.robot_state = "backing_off"

    def robot_turn_right(self):
        self.leftMotor.setPosition(float(0.0))
        self.rightMotor.setPosition(float(0.0))
        self.leftMotor.setPosition(float('inf'))
        self.rightMotor.setPosition(float('inf'))
        if self.robot_state != "turning_right":
            self.robot_previous_state = self.robot_state
            self.robot_state = "turning_right"
        self.leftMotor.setVelocity(self.velocity)
        self.rightMotor.setVelocity(-self.velocity)

    def robot_turn_left(self):
        self.leftMotor.setPosition(float(0.0))
        self.rightMotor.setPosition(float(0.0))
        self.leftMotor.setPosition(float('inf'))
        self.rightMotor.setPosition(float('inf'))
        if self.robot_state != "turning_left":
            self.robot_previous_state = self.robot_state
            self.robot_state = "turning_left"
        self.leftMotor.setVelocity(-self.velocity)
        self.rightMotor.setVelocity(self.velocity)

    def robot_stop_turning_and_go(self):
        self.leftMotor.setVelocity(self.velocity)
        self.rightMotor.setVelocity(self.velocity)
        self.leftMotor.setPosition(float('inf'))
        self.rightMotor.setPosition(float('inf'))
        if self.robot_state != "going_forward_after_turning":
            self.robot_previous_state = self.robot_state
            self.robot_state = "going_forward_after_turning"

    def robot_decide_next_maneuver(self):
        pass


maze_runner = MazeRunner()
maze_runner.robot_go()
while maze_runner.step(maze_runner.timeStep) != -1:
    maze_runner.get_and_print_distance_sensor_data(print_data=True)
    next_maneuver = maze_runner.robot_decide_next_maneuver()
    print(next_maneuver)
    if next_maneuver == "go_back":
        maze_runner.robot_back_of()
    if next_maneuver == "turn_right":
        maze_runner.robot_turn_right()
    if next_maneuver == "turn_left":
        maze_runner.robot_turn_left()
    if next_maneuver == "go_forward":
        maze_runner.robot_stop_turning_and_go()
