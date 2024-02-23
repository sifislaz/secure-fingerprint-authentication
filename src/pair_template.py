import numpy as np
from minutiae import MinutiaPoint, MinutiaePair
import hashlib
import os


class FingerprintTemplate:
    '''
        An abstract representation of fingerprint, using minutiae pairs
    '''

    _length_step = 12 # Quantization step for the distances
    _angle_step = np.pi/10  # Quantization step for the angles
    _x_length = 504  # The length of the fingerprint image in the x-axis
    _y_length = 480  # The length of the fingerprint image in the y-axis
    _max_dist = np.sqrt(np.power(_x_length, 2) + np.power(_y_length, 2))  # The maximum distance between two minutiae points
    
    def __init__(self, username, minutiae_list=None, reference=False):
        '''
            On initialization, the fingerprint template is created from the input features
            :param username: The username of the user
            :param minutiae_list: The input features of the fingerprint images
            :param reference: If True, the template is a reference template, else it is a query template
            Registration: minutiae_list is a list of lists of MinutiaPoint objects
            Verification_Reference: minutiae_list is None
            Verification_Query: minutiae_list is a list of MinutiaPoint objects
            
        '''
        self._features = []
        self._username = username
        self._reference = reference

        if minutiae_list is not None:
            if type(minutiae_list[0]) == list:  # Registration
                for minutiae in minutiae_list:
                    # Initialize the minutiae pairs
                    for i in range(len(minutiae)):
                        for j in range(i+1, len(minutiae)):
                            # Create the quantized symmetric minutiae pairs
                            self._features.append(MinutiaePair(minutiae[i], minutiae[j]).quantize(self._length_step, self._angle_step))
                            self._features.append(MinutiaePair(minutiae[j], minutiae[i]).quantize(self._length_step, self._angle_step))
            elif type(minutiae_list[0]) == MinutiaPoint:  # Verification Query
                for i in range(len(minutiae_list)):
                        for j in range(i+1, len(minutiae_list)):
                            # Create the quantized symmetric minutiae pairs
                            self._features.append(MinutiaePair(minutiae_list[i], minutiae_list[j]).quantize(self._length_step, self._angle_step))
                            self._features.append(MinutiaePair(minutiae_list[j], minutiae_list[i]).quantize(self._length_step, self._angle_step))
            # Keep only the unique minutiae pairs
            self._features = pairs = list(set(self._features))
            if self._reference:
                FingerprintTemplate.write_template(self._username, pairs)  # Save the minutiae pairs to a file (for evaluation purposes)


    def get_features(self):
       '''
           Get the minutiae pairs of the fingerprint template
           :return: The minutiae pairs
       '''

       return self._features
    
    @staticmethod
    def write_template(username, features):
        '''
            Write the fingerprint template to a file
        '''

        _username = hashlib.sha256(username.encode('utf-8')).hexdigest()  # Hash the username
        user_path = os.path.join(os.getcwd(), "assets", _username)  # Set the user directory path
        if not os.path.isdir(user_path):  # Check if the user directory doesn't exist
            os.mkdir(user_path)
        with open(os.path.join(user_path, _username + "_raw.dat"), "w") as f:
            for i in features:
                f.write(str(i)+"\n")
            f.close()


    def read_template(self):
        '''
            Read the fingerprint template from a file
        '''

        _username = hashlib.sha256(self._username.encode('utf-8')).hexdigest()  # Hash the username
        user_path = os.path.join(os.getcwd(), "assets", _username)  # Set the user directory path
        if not os.path.isdir(user_path):  # Check if the user directory doesn't exist
            raise FileNotFoundError("The user requested does not exist. Please try again.")
        with open(os.path.join(user_path, _username + "_raw.dat"), "r") as f:
            for line in f:  # Each line contains a minutiae pair
                line = line.strip()
                L, a_i, a_j, t_i, t_y = line.split(" ")
                # Get the angle classes
                a_i,_ = a_i.split(".")
                a_j,_ = a_j.split(".")
                self._features.append(MinutiaePair(int(L), int(a_i), int(a_j), int(t_i), int(t_y)))  # Read the minutiae pair from the file
            f.close()
            

    @staticmethod
    def match_templates(reference, query):
        '''
            Match two fingerprint templates using their minutiae pairs
            :param reference: The reference fingerprint template
            :param query: The query fingerprint template
            :return: The similarity score between the two templates
        '''

        matches = 0
        ref_pairs = reference.get_features()  # Get the reference minutiae pairs
        query_pairs = query.get_features()  # Get the query minutiae pairs
        # Count the matches
        for qpair in query_pairs:
            for rpair in ref_pairs:
                if qpair.L == rpair.L and qpair.a_i == rpair.a_i and qpair.a_j == rpair.a_j and qpair.t_i == rpair.t_i and qpair.t_j == rpair.t_j:
                    matches += 1
        return matches/len(query_pairs)  # The maximum possible matches is the number of pairs in the query template