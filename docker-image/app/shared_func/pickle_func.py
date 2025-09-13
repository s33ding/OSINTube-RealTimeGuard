import pickle 

def rpickle(file_name):
    try:
        with open(file_name, 'rb') as f:
            data = pickle.load(f)
            print(f"Successfully read pickle file: {file_name}")
            return data
    except FileNotFoundError:
        print(f"Error: file {file_name} not found")
    except pickle.UnpicklingError:
        print(f"Error: invalid pickle file {file_name}")

def spickle(data, file_name='output.pickle'):
    try:
        # Directly from dictionary
        with open(file_name, 'wb') as outfile:
            pickle.dump(data, outfile)
    except Exception as e:
        print("erro:",e)


