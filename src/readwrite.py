import os
import hashlib
import pickle

assets_dir = os.path.join(os.getcwd(), "assets")  # The path of the assets directory
dataset_dir_name = "CrossMatch_Sample_DB"  # The name of the dataset directory

def get_image_path(img_name):
    '''
        Check if there is a fingerprint image file with the given name
        :img_name: The name of the image file.
        :return: The path of the image file
    '''
    img_path = os.path.join(assets_dir,dataset_dir_name, img_name+".tif")  # Set the image file path
    if not os.path.isfile(img_path):
         raise FileNotFoundError("The image requested does not exist. Please try again.")
    return img_path


def check_user_existence(username):
    '''
        Check if there is a user with the given username
        :username: The username to check
        :return: True if the user exists, False otherwise
    '''
    username = hashlib.sha256(username.encode('utf-8')).hexdigest()  # Hash the username
    user_path = os.path.join(assets_dir, username)  # Set the user directory path
    return os.path.isdir(user_path)  # Return True if the user directory exists, False otherwise


def check_keyring_existence():
    '''
        Check if the keyring file exists
        :return: True if the keyring file exists, False otherwise
    '''
    return os.path.isfile(os.path.join(assets_dir, "keyring.dat"))


def load_keyring():
    '''
        Load the keyring from the keyring file
        :return: The keyring
    '''
    with open(os.path.join(assets_dir, "keyring.dat"), "rb") as f:
        keyring = pickle.load(f)
        f.close()
    return keyring


def save_keyring(keyring):
    '''
        Save the keyring to the keyring file
        :param keyring: The keyring to save
    '''
    with open(os.path.join(assets_dir, "keyring.dat"), "wb") as f:
        pickle.dump(keyring, f)
        f.close()


def get_picture_set_ids():
    '''
        Get the ids of the fingerprint images in the picture set
        :return: A list of the ids of the fingerprint images in the picture set
    '''

    finger_ids = ["_".join(f.split(".")[0].split("_")[:2]) for f in os.listdir(os.path.join(assets_dir, dataset_dir_name)) if f.endswith(".tif")]  # Get the ids of the fingerprint images in the picture set
    return list(set(finger_ids))  # Return the unique ids

