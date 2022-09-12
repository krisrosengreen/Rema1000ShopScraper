import matplotlib.pyplot as plt
import numpy as np
from shops import remashop

rema = remashop.Rema()
rema.gatherItems(100, "ppkg", "d_n")

items_ppkg = rema.items_all["items_ppkg"]


def dictToArray(items):
    L = []

    for key in items.keys():
        L.append(list(rema.items_all["items_ppkg"][key].values())[1:])

    return np.array(L)


def covarianceMap():
    data = dictToArray(items_ppkg)
    num_columns = len(data[0])

    _, axs = plt.subplots(num_columns, num_columns)

    columns_labels = ["cp", "np", "ppc", "p_dscnt", "ippk"]

    for i in range(num_columns):
        for j in range(num_columns):
            ax = axs[i][j]

            xs = data[:, i]
            ys = data[:, j]

            ax.scatter(xs, ys, s=1)

            if i == 0:
                ax.set_title(columns_labels[j])
            if j == 0:
                ax.set_ylabel(columns_labels[i])

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    covarianceMap()
