from serial import Serial

ACK_LEN = 8  # Length of ack string received from robot


class Communicator(object):
    """
    Handles communication between the system and the robot.
    Should be part of a subprocess spawned by the Robot class.

    If the Robot object is not awaiting a status update or acknowledgement, it
    will send its queued command to the communicator. If the communicator is
    not await an acknowledgement, it will wait for a command from the Robot
    object before sending this command and waiting for an ack - lost commands
    are also dealt with. Once a valid ack is received, the communicator
    forwards the status string to the Robot object.
    """

    def __init__(self, pipe_end, port="/dev/ttyACM0", timeout=0.1, rate=115200):
        """
        Create a Communicator object.
        :param port: Serial port used. The default corresponds to that on DICE.
        :param timeout: Read timeout (seconds)
        :param rate: Baud rate.
        """
        self.comm_pipe = pipe_end
        self.current_command = None  # The command currently being dealt with
        self.serial = Serial(port, rate, timeout=timeout)
        self.ack_bit = '0'

    def runner(self):
        """
        The main communicator loop.
        """
        while True:
            if self.current_command is None:  # No current command
                # TODO read/build a new command - can block here
                pass

            else:  # Have a current command, get ack/state
                self.serial.write(self.current_command)
                ack = self.serial.readline()
                if self.ack_test_update(ack):
                    self.current_command = None  # Successful ack, we're done

    def ack_test_update(self, ack):
        """
        Test the ack string for validity. If this is a successful ack then
        flip the bit, send the state string to the parent process, and return
        true. Else return false.
        """
        test = len(ack) == ACK_LEN and ack[0] == self.ack_bit
        if test:
            self.ack_bit = '0' if self.ack_bit == '1' else '1'  # Flip
            # TODO update / send state
            state_str = ack[1:]
            self.current_command = None
        return test