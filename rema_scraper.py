import requests
import json
import time
import sys
from termcolor import colored
from colorama import init
from data_processing import *

init()

main_page_contents = "https://cphapp.rema1000.dk/api/v1/catalog/store/1/departments-v2"
general_department_url = "https://3i8g24dm3n-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.21.1&x-algolia-application-id=3I8G24DM3N&x-algolia-api-key=f692051765ea56d2c8a55537448fa3a2"

main_page_req = requests.get(main_page_contents)
main_page_req_json = json.loads(main_page_req.text)

gen_req_format = {"indexName":"aws-prod-products","params":""}

def getDepartmentParams(department_id, category_id):

    return "query=&hitsPerPage=20&facets=%5B%22labels%22%5D&facetFilters=%5B%22department_id%3A{}%22%2C%22category_id%3A{}%22%5D&filters=".format(department_id,category_id)

items_price_per_kilo = {}

def getDepartmentCategories(department_data, dep_filter, type_processing):

    dep_id = department_data["id"]

    categories = department_data["categories"]

    requests_data_form = {"requests":[]}

    for category in categories:
        cat_id = category["id"]

        category_form_data = gen_req_format.copy()

        category_form_data["params"]=getDepartmentParams(dep_id,cat_id)

        requests_data_form["requests"].append(category_form_data)

    #Now request items from the category site

    request_category = requests.post(general_department_url, data=json.dumps(requests_data_form))

    request_category_json = json.loads(request_category.text)

    request_category_json_results = request_category_json["results"]

    for section_data in request_category_json_results:

        for hit in section_data["hits"]:

            if type_processing=="ppkg":
                processByPricePerKilo(hit,dep_filter)
            elif type_processing=="dscnt":
                processByDiscount(hit,dep_filter)
            else:
                print("Unknown processing method...")
                exit()

def padString(str,l):
    return str.ljust(l, ' ')

def colorTextByPercentage(value):
    #red -> yellow -> blue -> green
    # ]0 , 25]  ]25 , 50]   ]50 , 75]   ]75 , 100]

    if value <= 25:
        return colored(str(value), 'red')
    elif value <= 50:
        return colored(str(value), 'yellow')
    elif value <= 75:
        return colored(str(value), 'cyan')
    elif value <= 100:
        return colored(str(value), 'green')

def gatherItems(n_items, type_processing, sort_by):
    dep_filter=["Husholdning", "Pers. pleje", "Baby og småbørn", "Kiosk", "Drikkevarer"]
    #dep_filter=[] "Kolonial",


    print("Getting items...")
    print("\n"*3)

    for i in main_page_req_json:
        getDepartmentCategories(i, dep_filter, type_processing)

    if type_processing=="ppkg":
        showPricePerKilo(n_items)
    elif type_processing=="dscnt":
        showPricePerPercentageDiscount(sort_by)

def showPricePerPercentageDiscount(sort_by):

    items_price_per_percentage_discount = getItemsPricePerPercentageDiscount()

    sort_items = sorted(items_price_per_percentage_discount.items(), key=lambda x: x[1][sort_by], reverse=True)

    for i in sort_items:
        name = i[0]
        d_n = i[1]["d_n"]
        cp = i[1]["cp"]
        np = i[1]["np"]
        p_dscnt = i[1]["p_dscnt"]
        ppc = i[1]["ppc"]

        print(padString(d_n,25)+"\t"+padString(name,30)+"\t cp: " + padString(str(cp),5) + "\t np: " + padString(str(np),5)+"\t"+"ppc: "+padString(str(ppc),10)+"\t pdc: " + colorTextByPercentage(p_dscnt))
        print("-"*120)


def showPricePerKilo(n_items):

    items_price_per_kilo = getItemsPricePerKilo()

    sort_items = sorted(items_price_per_kilo.items(), key=lambda x: x[1]["ippk"])

    head = "v\tidx\tf1\tf2\n"
    fmt = "{dp:s}\t{v:s}\t{f1:s}\n"

    print("")
    print("")
    print("SHOWING THE FIRST " +str(n_items) + " RESULTS")
    print("")
    print("")
    print("DEPARTMENT NAME".ljust(22, ' ') + "|\t" + "ITEM NAME".ljust(40, ' ') + "\t" + "ITEM PRICE PER KILO/LITER")
    print("----------------------------------------------------------------------------------------------")

    for i in sort_items:

        print(fmt.format(dp=i[1]["d_n"].ljust(20, ' ')+"  |",v=i[0].ljust(40, ' '), f1=str(i[1]["ippk"])))

if len(sys.argv)==1:
    print("Please enter number of items to show")
else:
    gatherItems(int(sys.argv[1]), sys.argv[2], sys.argv[3])
