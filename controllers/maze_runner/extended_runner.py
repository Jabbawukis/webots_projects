from controller import Robot


class MazeRunner(Robot):
    def __init__(self):
        super().__init__()
        # Get simulation step length.
        self.timeStep = int(self.getBasicTimeStep())

        self.central = 0.0
        self.central_left = 0.0
        self.outer_left = 0.0
        self.central_right = 0.0
        self.outer_right = 0.0
        self.wall_collision_threshold = 2500.0
        self.collisions_detected = None
        self.wall_collision_detected = False
        self.last_turn_after_dead_end = ""

        self.black_circles_detected = 0
        self.black_circle_detected = False
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
        collision = {}
        self.central = self.centralSensor.getValue()
        self.central_left = self.centralLeftSensor.getValue()
        self.outer_left = self.outerLeftSensor.getValue()
        self.central_right = self.centralRightSensor.getValue()
        self.outer_right = self.outerRightSensor.getValue()
        if self.central > 0.0:
            collision["central"] = self.central
            if print_data:
                print(f"centralSensor: {self.central}")
        if self.central_left > 0.0:
            collision["central_left"] = self.central_left
            if print_data:
                print(f"centralLeftSensor: {self.central_left}")
        if self.outer_left > 0.0:
            collision["outer_left"] = self.outer_left
            if print_data:
                print(f"outerLeftSensor: {self.outer_left}")
        if self.central_right > 0.0:
            collision["central_right"] = self.central_right
            if print_data:
                print(f"centralRightSensor: {self.central_right}")
        if self.outer_right > 0.0:
            collision["outer_right"] = self.outer_right
            if print_data:
                print(f"outerRightSensor: {self.outer_right}")
        if len(collision.keys()) > 0:
            self.collisions_detected = collision
            self.wall_collision_detected = True

    def get_and_print_ground_sensor_data(self, print_data=True):
        self.ground_left = self.groundLeftSensor.getValue()
        self.ground_right = self.groundRightSensor.getValue()
        if self.ground_left <= self.black_circle_threshold and print_data:
            print(f"groundLeftSensor: {self.ground_left}")
        if self.ground_right <= self.black_circle_threshold and print_data:
            print(f"groundRightSensor: {self.ground_right}")
        if self.ground_left <= self.black_circle_threshold or self.ground_right <= self.black_circle_threshold:
            self.init_time = self.getTime()
            self.black_circle_detected = True
        else:
            current_time = self.getTime()
            if self.black_circle_detected and current_time > self.init_time + 2.0:
                self.black_circle_detected = False
                self.black_circles_detected += 1
                print(self.black_circles_detected)

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

    def robot_detect_open_space(self):
        pass


maze_runner = MazeRunner()
maze_runner.robot_go()
while maze_runner.step(maze_runner.timeStep) != -1:
    maze_runner.get_and_print_distance_sensor_data(print_data=True)
    maze_runner.get_and_print_ground_sensor_data(print_data=False)