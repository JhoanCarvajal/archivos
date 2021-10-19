import hashlib

inputFile = str(input("Enter the name of the file "))
openedFile = open(inputFile, "rb")
readFile = openedFile.read()

sha1Hash = hashlib.sha1(readFile)
sha1Hashed = sha1Hash.hexdigest()

print(f"{sha1Hashed}  {inputFile}")