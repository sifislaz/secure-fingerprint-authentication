import numpy as np

def angle_diff(theta1, theta2):
        '''
            Calculate the difference theta1 - theta2 between two angles in radians and normalize it in the [0,2*pi) range
            :param theta1: The first angle
            :param theta2: The second angle
            :return: The normalized difference
            :author: @sifislaz
        '''
        diff = theta1 - theta2
        if diff < 0:
            diff += 2*np.pi  # Add 2*pi to the angle difference to normalize it in the [0,2*pi) range
        elif diff >=2*np.pi:
            diff = 2*np.pi - diff  # Subtract the angle difference from 2*pi to normalize it in the [0,2*pi) range
        return diff

# Used for reduce vector size in HomomorphicTemplate (Not used in this implementation)
def generate_uniform_matrix(n, m, seed):
    '''
    Generate a random matrix with uniform distribution real values in the range [-1,1]
    :param n: The number of rows of the matrix
    :param m: The number of columns of the matrix
    :param seed: The seed for the random number generator
    '''
    np.random.seed(seed)  # Set the seed for the random number generator
    return np.random.uniform(-1, 1, (n, m))  # Generate a random matrix with uniform distribution real values in the range [-1,1]


def encrypted_xor(a,b):
    '''
        Calculate the encrypted XOR between an encrypted bit and a plaintext bit
        :param a: The encrypted bit
        :param b: The plaintext bit
        :return: The encrypted XOR
    '''
    return a + b -2*a*b