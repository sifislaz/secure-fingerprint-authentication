import readwrite as rw
from minutiae import MinutiaPoint
from homomorphic_template import HomomorphicTemplate
from phe import paillier

if __name__ == "__main__":
    # Keyring is used to store the private keys
    if not rw.check_keyring_existence():  # Check if the keyring doesn't exist
        keyring = paillier.PaillierPrivateKeyring()  # Create a new keyring
    else:
        keyring = rw.load_keyring()  # Load the keyring
    print("Secure Fingerprint Verification System\n")
    while True:
        print("1. Enroll a user")
        print("2. Verify a user")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == '3':
            print("Exiting...")
            break
        elif choice == '1':  # Enroll a user
            username = input("Enter the username: ")
            if rw.check_user_existence(username):  # Check if the user already exists
                print("User already exists! Please try again.\n")
                continue
            else:
                pubk,_ = paillier.generate_paillier_keypair(keyring)  # Generate a new public-private key pair
                print("To enroll a user, please provide 3 fingerprint images.\n")
                print("Please enter the image ids.\n")
                minutiae_points = []  # A list to store the minutiae points of the fingerprint images
                img_names = []  # A list to store the names of the fingerprint images
                img_cnt = 0  # A counter to keep track of the number of fingerprint images
                while True:
                    img_name = input("Enter the image id: ")
                    try:
                        if img_name in img_names:  # Check if the image has already been provided
                            print("The image has already been provided. Please try again.\n")
                            continue
                        img_path = rw.get_image_path(img_name)  # Get the image path
                    except FileNotFoundError:
                        print("The image requested does not exist. Please try again.\n")
                        continue
                    img_minutiae = MinutiaPoint.extract_minutiae(img_path)  # Extract the minutiae points
                    # Successful image enrollment
                    minutiae_points.append(img_minutiae)  # Save the minutiae points
                    print("Image processed successfully!\n")
                    img_names.append(img_name)  # Save the image name
                    img_cnt += 1  # Increment the image counter
                    if img_cnt == 3:  # Check if 3 images have been provided
                        break
                print("Enrolling user...")
                template = HomomorphicTemplate(username,minutiae_points,True, pubk)  # Create the template
                print("User {} enrolled successfully!\n".format(username))
        elif choice == '2':  # Verify a user
            username = input("Enter the username: ")
            if not rw.check_user_existence(username):  # Check if the user exists
                print("User does not exist! Please try again.\n")
                continue
            else:
                print("To verify a user, please provide a fingerprint image.\n")
                print("Please enter the image id.\n")
                img_name = input("Enter the image id: ")
                try:
                    img_path = rw.get_image_path(img_name)  # Get the image path
                except FileNotFoundError:
                    print("The image requested does not exist. Please try again.\n")
                    continue
                img_minutiae = MinutiaPoint.extract_minutiae(img_path)
                print("Verifying user...")
                query = HomomorphicTemplate(username,img_minutiae)  # Create the query template
                # Fetch the reference template
                ref = HomomorphicTemplate(username,reference=True)  
                ref.read_template()
                match = HomomorphicTemplate.match_templates(ref, query)  # Compare the templates
                match = keyring.decrypt(match)  # Decrypt similarity score
                print("Matching score: {}\n".format(match))
        else:
            print("Invalid choice! Please try again.\n")
