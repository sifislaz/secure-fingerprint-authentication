from pair_template import FingerprintTemplate
import numpy as np
import hashlib
import os


class BinaryTemplate(FingerprintTemplate):
    '''
        A class to represent a fingerprint template using binary minutiae pairs
    '''

    _length_bits = np.ceil(np.log2(FingerprintTemplate._max_dist//FingerprintTemplate._length_step))  # The number of bits needed to represent the quantized distance between two minutiae points
    _angle_bits = np.ceil(np.log2(2*np.pi//FingerprintTemplate._angle_step))  # The number of bits needed to represent the quantized angle between two minutiae points

    def __init__(self, username, minutiae_list=None, reference=False):
        '''
            On initialization, the fingerprint template is created from the input features
            :param username: The username of the user
            :param minutiae_list: The input features of the fingerprint images
            :param reference: If True, the template is a reference template, else it is a query template
        '''
        bin_pairs = []
        self._username = username
        self._reference = reference
        if minutiae_list is not None:
            super().__init__(self._username,minutiae_list, self._reference)
            for mp in self._features:
                # Get the local feature values
                L = mp.L
                a_i = mp.a_i
                a_j = mp.a_j
                t_i = mp.t_i
                t_j = mp.t_j
                # Convert the local feature values to binary
                L_bin = np.binary_repr(L, width=int(self._length_bits))
                a_i_bin = np.binary_repr(a_i, width=int(self._angle_bits))
                a_j_bin = np.binary_repr(a_j, width=int(self._angle_bits))
                # Create the binary minutiae pair
                bin_pairs.append(L_bin + a_i_bin + a_j_bin + str(t_i) + str(t_j))
            self._features = bin_pairs  # Set the binarized minutiae pairs as features
            if self._reference:
                BinaryTemplate.write_template(username, bin_pairs)  # Save the binarized minutiae pairs to a file (for evaluation purposes)

    @staticmethod
    def write_template(username, features):
        '''
            Write the fingerprint template to a file
        '''

        _username = hashlib.sha256(username.encode('utf-8')).hexdigest()  # Hash the username
        user_path = os.path.join(os.getcwd(), "assets", _username)  # Set the user directory path
        if not os.path.isdir(user_path):  # Check if the user directory doesn't exist
            os.mkdir(user_path)
        with open(os.path.join(user_path, _username + "_binary.dat"), "w") as f:
            for i in features:
                f.write(str(i)+"\n")  # Write a binarized minutiae pair per line in the file
            f.close()

    
    def read_template(self):
        '''
            Read the fingerprint template from a file
        '''

        _username = hashlib.sha256(self._username.encode('utf-8')).hexdigest()  # Hash the username
        user_path = os.path.join(os.getcwd(), "assets", _username)  # Set the user directory path
        if not os.path.isdir(user_path):  # Check if the user directory doesn't exist
            raise FileNotFoundError("The user requested does not exist. Please try again.")
        bin_pairs = []
        with open(os.path.join(user_path, _username + "_binary.dat"), "r") as f:
            for line in f:  # Each line contains a binarized minutiae pair
                line = line.strip()
                bin_pairs.append(line)
            f.close()
        self._features = bin_pairs  # Set the binarized minutiae pairs as features
                

    @staticmethod
    def match_templates(reference, query):
        '''
            Match two fingerprint templates using their binarized minutiae pairs
            :param reference: The reference fingerprint template
            :param query: The query fingerprint template
            :return: The similarity score between the two templates
        '''

        matches = 0
        ref_pairs = reference.get_features()  # Get the reference binarized pairs
        query_pairs = query.get_features()  # Get the query binarized pairs
        for pair in query_pairs:
            if pair in ref_pairs:  # Count the matching pairs
                matches += 1
        return matches/len(query_pairs)  # The maximum possible matches is the number of pairs in the query template
