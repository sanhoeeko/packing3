# Import the json module
import json


# define a function to round float numbers to 4 significant figures
def round_floats(obj):
    # if the object is a float, round it to 4 significant figures
    if isinstance(obj, float):
        return float(format(obj, '.4g'))
    # if the object is a list, apply the function to each element
    elif isinstance(obj, list):
        return [round_floats(x) for x in obj]
    # if the object is a dictionary, apply the function to each value
    elif isinstance(obj, dict):
        return {k: round_floats(v) for k, v in obj.items()}
    # otherwise, return the object as it is
    else:
        return obj


def Json4SF(filepath: str):
    # Open the json file and load its contents
    jss = []
    with open(filepath, "r") as f:
        for line in f.readlines():
            dic = json.loads(line)
            jss.append(dic)

    # Loop through the data and apply the function to any float values
    for i in range(len(jss)):
        # convert all float numbers to 4 digit float numbers
        jss[i] = round_floats(jss[i])

    # print(jss[0])

    # Open the json file again and write the modified data
    with open(filepath, "w") as f:
        for data in jss:
            f.write(json.dumps(data) + "\n")

    # Print a confirmation message
    print(f"The json file has been updated: {filepath}")
