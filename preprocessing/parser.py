import os
def to_json(batch):
    dir = f"./{batch}"

    for folder in os.listdir(dir):
        if not os.path.isdir(os.path.join(dir, folder)):
            continue
        for filename in os.listdir(os.path.join(dir,folder)):
            old = os.path.join(dir, folder, filename)

            i = old[1:].find(".")
            if i > 0:
                new = old[:i] + ".json"
            else:
                new = old + ".json"

            os.rename(old, new)



