items_price_per_kilo = {}
items_price_per_percentage_discount = {}

def checkStringForFilter(str, filter):

    for i in filter:
        if i in str:
            return True

    return False

def processByPricePerKilo(hit, dep_filter):
        price_per_unit = hit["pricing"]["price_per_unit"]

        if "per Kg." not in price_per_unit and "per Ltr." not in price_per_unit:
                #print(price_per_unit)
            return

        if checkStringForFilter(hit["department_name"], dep_filter):
                #print(hit["name"] + " " + price_per_unit)
            return

        item_price_per_kilo = float(price_per_unit.split(" ")[0].replace(',',''))

        department_name = hit["department_name"]

        items_price_per_kilo[hit["name"]]={"ippk":item_price_per_kilo, "d_n":department_name}

def processByDiscount(hit, dep_filter):
    if checkStringForFilter(hit["department_name"], dep_filter):
        #print(hit["name"] + " " + price_per_unit)
        return

    if hit["pricing"]["is_on_discount"]:
        p = hit["pricing"]["price"]
        np = hit["pricing"]["normal_price"]

        ppc = pricePerCalorie(hit)

        percentage_discount = int(round((np-p)/np*100, 0))

        items_price_per_percentage_discount[hit["name"]]={"d_n": hit["department_name"], "cp": p, "np": np, "p_dscnt": percentage_discount, "ppc": ppc}

        #print(padString(hit["department_name"],25)+"\t"+padString(hit["name"],30)+"\t cp: " + padString(str(p),5) + "\t np: " + padString(str(np),5)+"\t pdc: " + colorTextByPercentage(int(round((np-p)/np*100, 0))))
        #print("-"*104)

def pricePerCalorie(hit):

    calories = getInt(hit["nutrition_info"][0]["value"].split("/")[1].strip().split(" "))

    cp = hit["pricing"]["price"]

    calories_per_price = round(calories/cp,1)

    return calories_per_price

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def getInt(lot):
    for i in lot:
        if RepresentsInt(i):
            return int(i)

def getItemsPricePerKilo():
    return items_price_per_kilo

def getItemsPricePerPercentageDiscount():
    return items_price_per_percentage_discount
