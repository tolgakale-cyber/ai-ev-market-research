import json

from iea_parser import iea_ev_satis_verilerini_oku


def iea_verisini_jsona_aktar(csv_yolu, json_yolu):
    veri = iea_ev_satis_verilerini_oku(csv_yolu)

    with open(json_yolu, "w", encoding="utf-8") as dosya:
        json.dump(
            veri,
            dosya,
            ensure_ascii=False,
            indent=4,
        )


if __name__ == "__main__":
    csv_yolu = "data/raw/global-electric-car-sales-2020-2026.csv"
    json_yolu = "outputs/iea_ev_sales.json"

    iea_verisini_jsona_aktar(csv_yolu, json_yolu)

    print(f"JSON oluşturuldu: {json_yolu}")