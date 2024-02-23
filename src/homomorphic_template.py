from index_template import IndexTemplate
from utils import generate_uniform_matrix, encrypted_xor
import numpy as np
import hashlib
import json
import os
from phe import paillier


class HomomorphicTemplate(IndexTemplate):
    '''
        A class to represent a fingerprint template using Pailler Partial Homomorphic Encryption
        Following the paper "Secure Fingerprint Authentication with Homomorphic Encryption" by
        Yang et al. (https://doi.org/10.1109/DICTA51227.2020.9363426)
    '''
    _vector_size = 600  # The size of the reduced vector (Not used in this implementation)

    def __init__(self,username,minutiae_list=None, reference = False, pubkey = None):
        '''
            On initialization, the fingerprint template is created from the input features
            :param username: The username of the user
            :param minutiae_list: The input features of the fingerprint images
            :param reference: If True, the template is a reference template, else it is a query template
            :param pubkey: The public key of the Pailler cryptosystem (only used for reference templates)
        '''
        self._username = username
        self._reference = reference
        if minutiae_list is not None:  # If the minutiae list is not provided, then the template remains empty to be read from a file
            super().__init__(self._username, minutiae_list, self._reference)  # Call the parent class constructor
            if self._reference:  # If the template is a reference template
                if pubkey is None:  # If the public key is not provided
                    raise ValueError("Public key is required for reference templates.")
                self._pubkey = pubkey
                self._encrypt_features()  # Perform the encryption of the vector
                self.write_template()  # Write the template to a file
        else:
            self._features = None
    

    def _reduce_features(self):
        '''
            Reduce the dimension of the index vector (Not used in this implementation)
        '''
        _username = hashlib.sha256(self._username.encode('utf-8')).hexdigest()  # Hash the username
        seed = int(_username, 16) % (2**32-1)  # Generate a seed from the username
        mat = generate_uniform_matrix(self._index_factor, HomomorphicTemplate._vector_size, seed)  # Generate a random matrix
        self._features = np.dot(self._features, mat)  # Reduce the dimension of the index vector
        self._features = (self._features > 0).astype(int)  # Binarize the index vector


    def _encrypt_features(self):
        '''
            Encrypt the index vector
        '''
        self._features = [self._pubkey.encrypt(i) for i in self._features]  # Encrypt the index vector


    def write_template(self):
        '''
            Write the serialized homomorphic template to a file
        '''
        _username = hashlib.sha256(self._username.encode('utf-8')).hexdigest()  # Hash the username
        user_path = os.path.join(os.getcwd(), "assets", _username)  # Set the user directory path
        if not os.path.isdir(user_path):  # Check if the user directory doesn't exist
            os.mkdir(user_path)
        if self._reference:  # If the template is a reference template
            # Save the public key and the encrypted vector to the template
            ser = {}
            ser["pubkey"] = {'n':self._pubkey.n}
            ser["features"] = [(str(i.ciphertext()), i.exponent) for i in self._features]

        with open(os.path.join(user_path, _username + "_homomorphic.dat"), "w") as f:
            json.dump(ser, f)
            f.close()
    

    def read_template(self):
        '''
            Read the serialized homomorphic template from a file
        '''
        _username = hashlib.sha256(self._username.encode('utf-8')).hexdigest()  # Hash the username
        user_path = os.path.join(os.getcwd(), "assets", _username)  # Set the user directory path
        if not os.path.isdir(user_path):  # Check if the user directory doesn't exist
            raise FileNotFoundError("The user does not exist.")
        with open(os.path.join(user_path, _username + "_homomorphic.dat"), "r") as f:
            ser = json.load(f)  # Load the serialized template
            f.close()
        self._pubkey = paillier.PaillierPublicKey(n=int(ser["pubkey"]["n"]))  # Load the public key
        # Load the encrypted vector
        self._features = [
            paillier.EncryptedNumber(self._pubkey, int(i[0]), int(i[1])) for i in ser["features"]
        ]


    @staticmethod
    def match_templates(reference, query):
        '''
            Match two fingerprint templates using their indexes
            :param reference: The reference fingerprint template
            :param query: The query fingerprint template
            :return: The encrypted similarity score
        '''
        ref_features = reference.get_features()  # Get the reference features
        query_features = query.get_features()  # Get the query features
        common_ones = [ref_features[i]*query_features[i] for i in range(len(ref_features))]  # Compute the common ones
        return sum(common_ones)/sum(query_features)  # Return the similarity score