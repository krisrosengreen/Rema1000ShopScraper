import requests
import json
from termcolor import colored
from colorama import init
import os
import time

class Rema:
    def __init__(self):
        init()

        with open("config.json", "r") as f:
            self.config = json.load(f)["Rema1000"]

        self.items_filename = self.config["items_filename"]
        main_page_contents = self.config["main_page_contents"]
        self.general_department_url = self.config["general_department_url"]
        main_page_req = requests.get(main_page_contents)
        self.main_page_req_json = json.loads(main_page_req.text)
        self.gen_req_format = {"indexName": "aws-prod-products", "params": ""}
        self.items_price_per_kilo = {}
        self.items_price_per_percentage_discount = {}

    def getDepartmentParams(self, department_id, category_id):
        return self.config["query_template"].format(department_id, category_id)

    def getDepartmentCategories(self, department_data, dep_filter, type_processing):
        dep_id = department_data["id"]
        categories = department_data["categories"]
        requests_data_form = {"requests": []}

        for category in categories:
            cat_id = category["id"]
            category_form_data = self.gen_req_format.copy()
            category_form_data["params"] = self.getDepartmentParams(
                dep_id, cat_id)
            requests_data_form["requests"].append(category_form_data)

        # Now request items from the category site
        request_category = requests.post(
            self.general_department_url, data=json.dumps(requests_data_form))
        request_category_json = json.loads(request_category.text)
        request_category_json_results = request_category_json["results"]

        for section_data in request_category_json_results:
            for hit in section_data["hits"]:
                attr_name = f"processing_{type_processing}"
                if hasattr(self, attr_name):
                    getattr(self, attr_name)(hit, dep_filter)
                else:
                    print("Unknown processing method...")
                    exit()

    def padString(self, str, l):
        return str.ljust(l, ' ')

    def colorTextByPercentage(self, value):
        # red -> yellow -> blue -> green
        # [0 , 25]  ]25 , 50]   ]50 , 75]   ]75 , 100]

        if value <= 25:
            return colored(str(value), 'red')
        elif value <= 50:
            return colored(str(value), 'yellow')
        elif value <= 75:
            return colored(str(value), 'cyan')
        elif value <= 100:
            return colored(str(value), 'green')

    def saveItems(self, items_ppkg, items_ppdiscount):
        dict_save = {"items_ppkg": items_ppkg,
                     "items_ppdiscount": items_ppdiscount}
        with open(self.items_filename, "w") as file:
            file.write(json.dumps(dict_save))

    def loadItems(self):
        with open(self.items_filename, "r") as file:
            items_all = json.load(file)

            self.setItemsPricePerKilo(items_all["items_ppkg"])
            self.setItemsPricePerPercentageDiscount(items_all["items_ppdiscount"])

    def gatherItems(self, n_items, type_processing, sort_by, dep_filter):
        print("Getting items...")
        print("\n"*3)

        def fetch():
            for i in self.main_page_req_json:
                self.getDepartmentCategories(
                    i, dep_filter, type_processing)
            self.saveItems(self.items_price_per_kilo,
                            self.items_price_per_percentage_discount)

        if os.path.exists(self.items_filename):
            if time.time() - os.path.getmtime(self.items_filename) > self.config["requests_latency"]:
                fetch()
            else:
                self.loadItems()
        else:
            fetch()

        attr_name = f"show_{type_processing}"
        if hasattr(self, attr_name):
            getattr(self, f"show_{type_processing}")(n_items, sort_by)

    def show_dscnt(self, n_items, sort_by):
        items_price_per_percentage_discount = self.getItemsPricePerPercentageDiscount()
        sort_items = sorted(items_price_per_percentage_discount.items(
        ), key=lambda x: x[1][sort_by], reverse=True)

        for i in sort_items:
            name = i[0]
            d_n = i[1]["d_n"]
            cp = i[1]["cp"]
            np = i[1]["np"]
            p_dscnt = i[1]["p_dscnt"]
            ppc = i[1]["ppc"]

            print(self.padString(d_n, 25)+"\t"+self.padString(name, 30)+"\t cp: " + self.padString(str(cp), 5) + "\t np: " +
                  self.padString(str(np), 5)+"\t"+"ppc: "+self.padString(str(ppc), 10)+"\t pdc: " + self.colorTextByPercentage(p_dscnt))
            print("-"*120)

    def show_ppkg(self, n_items, sort_by):
        items_price_per_kilo = self.getItemsPricePerKilo()

        sort_items = sorted(items_price_per_kilo.items(),
                            key=lambda x: x[1]["ippk"])

        fmt = "{dp:s}\t{v:s}\t{f1:s}\n"
        title = "DEPARTMENT NAME".ljust(
            22, ' ') + "|\tITEM NAME".ljust(40, ' ') + "\tITEM PRICE PER KILO/LITER"

        print("\n\n")
        print(f"SHOWING THE FIRST {str(n_items)} RESULTS")
        print("\n\n")
        print(title)
        print("-"*len(title))

        for i in sort_items:
            print(fmt.format(dp=i[1]["d_n"].ljust(20, ' ')+"  |",
                             v=i[0].ljust(40, ' '), f1=str(i[1]["ippk"])))

    # From dataprocessing file
    def checkStringForFilter(self, str, filter):
        for i in filter:
            if i in str:
                return True

        return False

    def processing_ppkg(self, hit, dep_filter):
        price_per_unit = hit["pricing"]["price_per_unit"]

        if "per Kg." not in price_per_unit and "per Ltr." not in price_per_unit:
            return

        if self.checkStringForFilter(hit["department_name"], dep_filter):
            return

        item_price_per_kilo = float(
            price_per_unit.split(" ")[0].replace(',', ''))
        department_name = hit["department_name"]
        self.items_price_per_kilo[hit["name"]] = {
            "ippk": item_price_per_kilo, "d_n": department_name}

    def processing_dscnt(self, hit, dep_filter):
        if self.checkStringForFilter(hit["department_name"], dep_filter):
            return

        if hit["pricing"]["is_on_discount"]:
            p = hit["pricing"]["price"]
            np = hit["pricing"]["normal_price"]

            ppc = self.pricePerCalorie(hit)
            percentage_discount = int(round((np-p)/np*100, 0))
            self.items_price_per_percentage_discount[hit["name"]] = {
                "d_n": hit["department_name"], "cp": p, "np": np, "p_dscnt": percentage_discount, "ppc": ppc}

    def pricePerCalorie(self, hit):
        calories = self.getInt(hit["nutrition_info"][0]
                          ["value"].split("/")[1].strip().split(" "))
        cp = hit["pricing"]["price"]
        calories_per_price = round(calories/cp, 1)

        return calories_per_price

    def RepresentsInt(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def getInt(self, lot):
        for i in lot:
            if self.RepresentsInt(i):
                return int(i)

    def getItemsPricePerKilo(self):
        return self.items_price_per_kilo

    def getItemsPricePerPercentageDiscount(self):
        return self.items_price_per_percentage_discount

    def setItemsPricePerKilo(self, items_ppkg):
        self.items_price_per_kilo = items_ppkg

    def setItemsPricePerPercentageDiscount(self, items_ppdiscount):
        self.items_price_per_percentage_discount = items_ppdiscount
