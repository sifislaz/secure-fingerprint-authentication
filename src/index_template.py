from binary_template import BinaryTemplate
import numpy as np
import hashlib
import os


class IndexTemplate(BinaryTemplate):

    '''
        A class to represent a fingerprint template using index of binary minutiae pairs
    '''

    _index_factor = 2**16 - 1  # The number of bits needed to represent the index of the binary minutiae pairs

    def __init__(self, username, minutiae_list=None, reference=False):
        '''
            On initialization, the fingerprint template is created from the input features
            :param username: The username of the user
            :param minutiae_list: The input features of the fingerprint images
            :param reference: If True, the template is a reference template, else it is a query template
        '''
        self._username = username
        self._reference = reference
        if minutiae_list is not None:  # If the minutiae list is not provided, then the template remains empty to be read from a file
            super().__init__(self._username, minutiae_list, self._reference)  # Call the parent class constructor
            index = [0 for i in range(self._index_factor)]  # Initialize the index
            # Perform the hashing of the binary minutiae pairs to generate the index
            for mp in self._features:
                a = int(mp, 2)
                idx = np.mod(a, self._index_factor)
                index[idx] = 1
            self._features = index  # Set the index vector as the features
            if self._reference:
                IndexTemplate.write_template(self._username, index)  # Save the index to a file (for evaluation purposes)
        else:
            self._features = None

    
    @staticmethod
    def write_template(username, features):
        '''
            Write the fingerprint template to a file
        '''

        _username = hashlib.sha256(username.encode('utf-8')).hexdigest()  # Hash the username
        user_path = os.path.join(os.getcwd(), "assets", _username)  # Set the user directory path
        if not os.path.isdir(user_path):  # Check if the user directory doesn't exist
            os.mkdir(user_path)
        with open(os.path.join(user_path, _username + "_index.dat"), "w") as f:
            for i in features:  # Write the index vector to the file
                f.write(str(i)+" ")
            f.close()


    def read_template(self):
        '''
            Read the fingerprint template from a file
        '''

        _username = hashlib.sha256(self._username.encode('utf-8')).hexdigest()  # Hash the username
        user_path = os.path.join(os.getcwd(), "assets", _username)  # Set the user directory path
        if not os.path.isdir(user_path):  # Check if the user directory doesn't exist
            raise FileNotFoundError("The user directory does not exist.")
        with open(os.path.join(user_path, _username + "_index.dat"), "r") as f:
            line = f.readline()
            line = line.strip()
            self._features = line.split(" ")  # Read the index vector from the file
            self._features = [int(i) for i in self._features]  # Convert the index elements to integers
            f.close()

    
    @staticmethod
    def match_templates(reference, query):
        '''
            Match two fingerprint templates using their indexes
            :param reference: The reference fingerprint template
            :param query: The query fingerprint template
            :return: The similarity score
        '''

        ref_index = reference.get_features()  # Get the index of the reference fingerprint template
        query_index = query.get_features()  # Get the index of the query fingerprint template
        corr = np.sum(np.bitwise_and(ref_index, query_index))  # Find the common 1's between the two indexes and sum them to find their count
        return corr/np.sum(query_index)  # The maximum possible corrects is the number of 1's in the query index
