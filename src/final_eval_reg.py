import logging
import os
import readwrite as rw
import time
from minutiae import MinutiaPoint
from homomorphic_template import HomomorphicTemplate
from phe import paillier

logpath = os.path.join(os.getcwd(), "log", "final_eval_reg.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s %(message)s")
file_handler = logging.FileHandler(logpath)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def register_user(username, keyring):
    '''
        Perform the registration process for a user
        :param username: The username of the user
        :param keyring: The paillier keyring to keep the private keys
    '''
    logger.debug("Registration process for user {} started".format(username))
    minutiae_list = []  # A list to store the minutiae points of the fingerprint images
    reg_time = time.perf_counter()
    for i in range(1,4):
        try:
            img_name = "{}_{}".format(username, i)
            img_path = rw.get_image_path(img_name)  # Get the image path
        except FileNotFoundError:
            logger.error("Image {} not found".format(img_name))
            print("The image requested does not exist. Please try again.\n")
            continue
        img_minutiae = MinutiaPoint.extract_minutiae(img_path)
        minutiae_list.append(img_minutiae)  # Save the minutiae points
        logger.debug("Img {} processed successfully!".format(img_name))
    pubk,_ = paillier.generate_paillier_keypair(keyring)  # Generate the paillier keypair
    template = HomomorphicTemplate(username, minutiae_list, True, pubk)  # Generate the template
    reg_time = time.perf_counter() - reg_time  # Calculate the registration time
    logger.info("Registration time: {}".format(reg_time))
    logger.debug("User {} template generation completed".format(username))

if __name__ == "__main__":
    
    if not rw.check_keyring_existence():
        keyring = paillier.PaillierPrivateKeyring()
    else:
        keyring = rw.load_keyring()

    images = ['045_7','017_3','012_5','076_8']
    for image in images:
        logger.info(image)
        register_user(image, None)
    rw.save_keyring(keyring)