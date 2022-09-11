import argparse
from shops import remashop

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("shop", type=str, help="Which shop to gather items from [rema]")

    parser.add_argument("num_items", type=int,
                        help="Number of items to be listed")
    parser.add_argument("type_processing", type=str,
                        help="Processing type [ppkg/dscnt]")
    parser.add_argument(
        "sort_by", type=str, help="If 'dscnt' is specified: Sort items by [d_n/cp/np/p_dscnt/ppc]")
    args = parser.parse_args()

    if args.shop == "rema":
        rema = remashop.Rema()
        rema.gatherItems(args.num_items, args.type_processing, args.sort_by)


if __name__ == "__main__":
    main()