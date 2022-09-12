import argparse
from shops import remashop


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "shop", type=str, help="Which shop to gather items from [rema]")

    parser.add_argument("num_items", type=int,
                        help="Number of items to be listed")
    parser.add_argument("type_processing", type=str,
                        help="Processing type [ppkg/dscnt]")
    parser.add_argument(
        "sort_by", type=str, help="If 'dscnt' is specified: Sort items by [d_n/cp/np/p_dscnt/ppc]")
    parser.add_argument(
        "--filter", type=str, help='Departments to filter out of the data (Codes seperated by comma; Standard is all of them): ["a": "Husholdning", "b": "Pers. pleje", "c": "Baby og småbørn", "d": "Kiosk", "e": "Drikkevarer"]')

    dep_filter = ["Husholdning", "Pers. pleje",
                  "Baby og småbørn", "Kiosk", "Drikkevarer"]

    args = parser.parse_args()

    if args.filter is not None:
        dep_filter = []
        filters = {'a': "Husholdning", 'b': "Pers. pleje",
                   'c': "Baby og småbørn", 'd': "Kiosk", 'e': "Drikkevarer"}
        found_filters = args.filter.split(',')
        for filter_code in found_filters:
            dep_filter.append(filters[filter_code])

    if args.shop == "rema":
        rema = remashop.Rema()
        rema.gatherItems(args.num_items, args.type_processing,
                         args.sort_by, dep_filter)


if __name__ == "__main__":
    main()
