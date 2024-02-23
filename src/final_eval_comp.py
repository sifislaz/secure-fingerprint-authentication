import logging
import os
import readwrite as rw
from minutiae import MinutiaPoint
from homomorphic_template import HomomorphicTemplate
from phe import paillier
from index_template import IndexTemplate
from binary_template import BinaryTemplate

# Logging configuration

logpath = os.path.join(os.getcwd(), "log", "final_eval_comp.log")
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
    '''
    logger.debug("Registration process for user {} started".format(username))
    minutiae_list = []  # A list to store the minutiae points of the fingerprint images
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
    pubk, _ = paillier.generate_paillier_keypair(keyring)  # Generate the public and private keys
    template = HomomorphicTemplate(username, minutiae_list, True, pubk)  # Generate the template
    logger.debug("User {} template generation completed".format(username))


def compare_user(username, keyring):
    '''
        Perform the comparison process for a user
        :param username: The username of the user
    '''
    logger.debug("Comparison process for user {} started".format(username))
    images = rw.get_picture_set_ids()  # Get all image ids
    images.remove(username)  # Keep the different ones
    # Create reference templates
    ref_hom = HomomorphicTemplate(username, reference=True)
    ref_hom.read_template()
    ref_ind = IndexTemplate(username, reference=True)
    ref_ind.read_template()
    ref_bin = BinaryTemplate(username, reference=True)
    ref_bin.read_template()
    # Perform true comparisons
    for i in range(4,9):
        try:
            img_name = "{}_{}".format(username, i)
            img_path = rw.get_image_path(img_name)
        except FileNotFoundError:
            logger.error("Image {} not found".format(img_name))
            print("The image requested does not exist. Please try again.\n")
            continue
        img_minutiae = MinutiaPoint.extract_minutiae(img_path)
        query_hom = HomomorphicTemplate(username, img_minutiae)
        query_ind = IndexTemplate(username, img_minutiae)
        query_bin = BinaryTemplate(username, img_minutiae)
        hom_match = HomomorphicTemplate.match_templates(ref_hom, query_hom)
        hom_match = keyring.decrypt(hom_match)
        ind_match = IndexTemplate.match_templates(ref_ind, query_ind)
        bin_match = BinaryTemplate.match_templates(ref_bin, query_bin)
        logger.info("{} {} {} {} {} T".format(username, img_name, hom_match, ind_match, bin_match))
    # Perform false comparisons
    for image in images:
        for i in range(1,9):
            try:
                img_name = "{}_{}".format(image, i)
                img_path = rw.get_image_path(img_name)
            except FileNotFoundError:
                logger.error("Image {} not found".format(img_name))
                print("The image requested does not exist. Please try again.\n")
                continue
            img_minutiae = MinutiaPoint.extract_minutiae(img_path)
            query_hom = HomomorphicTemplate(username, img_minutiae)
            query_ind = IndexTemplate(username, img_minutiae)
            query_bin = BinaryTemplate(username, img_minutiae)
            hom_match = HomomorphicTemplate.match_templates(ref_hom, query_hom)
            hom_match = keyring.decrypt(hom_match)
            ind_match = IndexTemplate.match_templates(ref_ind, query_ind)
            bin_match = BinaryTemplate.match_templates(ref_bin, query_bin)
            logger.info("{} {} {} {} {} F".format(username, img_name, hom_match, ind_match, bin_match))


if __name__ == "__main__":
    # Create or load the keyring with the private keys
    if not rw.check_keyring_existence():
        keyring = paillier.PaillierPrivateKeyring()
    else:
        keyring = rw.load_keyring()
    images = rw.get_picture_set_ids()  # Get all image ids
    # Register all users
    for image in images:
        register_user(image, keyring)
    rw.save_keyring(keyring)  # Save the keyring
    # Compare all users
    for image in images:
        compare_user(image, keyring)
