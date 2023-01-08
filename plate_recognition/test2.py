def validate_plate(text):
    if len(text) == 7:
        #if first 2 characters are letters
        if text[0].isalpha() and text[1].isalpha():
            #if next 3 characters are numbers
            if text[2].isnumeric() and text[3].isnumeric() and text[4].isnumeric():
                #if last 2 characters are letters
                if text[5].isalpha() and text[6].isalpha():
                    return True
    return False
    
def fix_plate(text):
    while len(text) > 7:
        print("fix:", text)
        
        if text[0].isnumeric():
            text = text[1:]
            continue
        
        if text[-1].isnumeric():
            text = text[:-1]
            continue

        if not (text[0].isalpha() and text[1].isalpha() and text[2].isnumeric()):
            text = text[1:]
            continue

        if not (text[-1].isalpha() and text[-2].isalpha() and text[-3].isnumeric()):
            text = text[:-1]
            continue
    if validate_plate(text):
        return text
    else:
        return None

fixed = fix_plate("BAA123AA8")
print(fixed)