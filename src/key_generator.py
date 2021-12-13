from cryptography.fernet import Fernet

# Print this to the console
print("Add the following key to your config.yaml file:")
print(str(Fernet.generate_key())[2:-2])