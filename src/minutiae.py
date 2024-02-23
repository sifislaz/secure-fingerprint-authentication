import numpy as np
import os
import subprocess
import base64
import cbor2
from utils import angle_diff


class MinutiaPoint:
    def __init__(self,x, y, theta, type):
        '''
            A class to represent a minutia point
            :param x: The coordinate x of the point in pixels
            :param y: The coordinate y of the point in pixels
            :param theta: The orientation of the minutia point (counterclockwise angle)
            :param type: 0 if the minutia point is a ridge ending, 1 if it is a bifurcation.
            :return A MinutiaPoint object
        '''
        self.x = x
        self.y = y
        self.theta = theta
        self.type = type

    def __str__(self):
        typeconv = lambda t : "Bifurcation" if t == 1 else "Ending"  # If type is 1, convert to Bifurcation else Ridge ending
        return "{} {} {:.3f} {}".format(self.x, self.y, self.theta, typeconv(self.type))
    

    @staticmethod
    def extract_minutiae(img_path):
        '''
            Extract minutiae points from a fingerprint image, using SourceAFIS
            :param img: The path to the fingerprint image
            :return: The minutiae points
        '''
        path = os.path.join(os.getcwd(),"external","minutiaeextraction-0.0.1-SNAPSHOT-jar-with-dependencies.jar")  # Get the SourceAFIS API jar file path
        dpi = "500"
        cmd = ["java", "-jar", path, img_path, dpi]  # Build the command to run the jar file passing the image path as an argument
        proc = subprocess.run(cmd, capture_output=True, text=True)  # Run the jar file and capture the output
        minutiae_b64_str = proc.stdout.strip()
        minutiae_barr = base64.b64decode(minutiae_b64_str)  # Decode the output from the base64 encoding
        minutiae_dict = cbor2.loads(minutiae_barr)  # Deserialize from the cbor format to a dictionary
        # Get the details from the template
        positionsX = minutiae_dict["positionsX"]
        positionsY = minutiae_dict["positionsY"]
        angles = minutiae_dict["directions"]
        types = minutiae_dict["types"]
        minutiae = []
        for i in range(len(positionsX)):
            typeconv = lambda a : 1 if a == "B" else 0  # If type is Bifurcation, convert to 1 else 0
            angle = 2*np.pi - angles[i] # SourceAFIS calculates the orientation angle clockwise, we need the counterclockwise value
            minutiae.append(MinutiaPoint(positionsX[i], positionsY[i], angle, typeconv(types[i])))  # Create a MinutiaPoint object and save it in the list

        return minutiae


class MinutiaePair:
    def __init__(self, *args):
        '''
            Create a minutiae pair between two minutia points
            :param m_i: The reference minutia point
            :param m_j: The neighbor minutia point
            :return: The minutiae pair object

            Create a minutiae pair from the local features
            :param L: The distance between the two minutiae points
            :param a_i: The angle between the reference minutia point and the line connecting the two minutiae points
            :param a_j: The angle between the neighbor minutia point and the line connecting the two minutiae points
            :param t_i: The type of the reference minutia point
            :param t_j: The type of the neighbor minutia point
            :return: The minutiae pair object
        '''
        if len(args) == 2: # If the input arguments are two minutiae points
            m_i = args[0]
            m_j = args[1]
            if type(m_i) is MinutiaPoint and type(m_j) is MinutiaPoint:
                x_diff = m_j.x - m_i.x
                y_diff = m_j.y - m_i.y
                phi = np.pi + np.arctan2(y_diff, x_diff)  # Calculate the orientation of the line connecting the two minutiae points
                if phi - 2*np.pi == 0:  # Keep the range [0,2pi)
                    phi = 0
                self.L = int(np.sqrt(np.power(x_diff,2) + np.power(y_diff,2)))  # Calculate the distance between the two minutiae points
                self.a_i = angle_diff(m_i.theta, phi)  # Calculate the angle between the reference minutia point and the line connecting the two minutiae points
                self.a_j = angle_diff(m_j.theta, phi)  # Calculate the angle between the neighbor minutia point and the line connecting the two minutiae points
                self.t_i = m_i.type  # Save the type of the reference minutia point
                self.t_j = m_j.type  # Save the type of the neighbor minutia point
            else:
                raise TypeError("The input arguments must be of type MinutiaPoint.")
        elif len(args) == 5:  # If the input arguments are the local features
            L = args[0]
            a_i = args[1]
            a_j = args[2]
            t_i = args[3]
            t_j = args[4]
            if type(L) is int and type(a_i) is int and type(a_j) is int and type(t_i) is int and type(t_j) is int:
                self.L = L
                self.a_i = a_i
                self.a_j = a_j
                self.t_i = t_i
                self.t_j = t_j
            else:
                raise TypeError("The input arguments must be of type int.")

    def __str__(self):
        return "{} {:.3f} {:.3f} {} {}".format(self.L, self.a_i, self.a_j, self.t_i, self.t_j)  # The format of the angles is kept in case no quantization is applied
    

    def __eq__(self, other):
        if isinstance(other, MinutiaePair):
            return self.L == other.L and self.a_i == other.a_i and self.a_j == other.a_j and self.t_i == other.t_i and self.t_j == other.t_j
        return False
    
    def __hash__(self):
        return hash((self.L, self.a_i, self.a_j, self.t_i, self.t_j))

    def quantize(self, length_step, angle_step):
        '''
            Quantize the minutiae pair
            :param length_step: The length step
            :param angle_step: The angle step
            :return: The quantized minutiae pair
        '''
        self.L = int(self.L//length_step)  # Quantize the distance between the two minutiae points
        self.a_i = int(self.a_i//angle_step)  # Quantize the angle between the reference minutia point and the line connecting the two minutiae points
        self.a_j = int(self.a_j//angle_step)  # Quantize the angle between the neighbor minutia point and the line connecting the two minutiae points
        return self
