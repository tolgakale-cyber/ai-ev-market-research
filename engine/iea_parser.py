import csv


def iea_ev_satis_verilerini_oku(csv_yolu):
    veriler = []

    with open(csv_yolu, "r", encoding="utf-8-sig", newline="") as dosya:
        satirlar = dosya.readlines()

    baslik_index = None

    for index, satir in enumerate(satirlar):
        if satir.strip().startswith(";China;"):
            baslik_index = index
            break

    if baslik_index is None:
        raise ValueError("IEA CSV başlık satırı bulunamadı.")

    csv_metni = "".join(satirlar[baslik_index:])

    okuyucu = csv.DictReader(
        csv_metni.splitlines(),
        delimiter=";",
    )

    for satir in okuyucu:
        yil_raw = satir[""].strip()

        tahmin = yil_raw.endswith("e")
        yil = int(yil_raw.rstrip("e"))

        veriler.append(
            {
                "yil": yil,
                "tahmin": tahmin,
                "cin_milyon": float(satir["China"]),
                "avrupa_milyon": float(satir["Europe"]),
                "abd_milyon": float(satir["United States"]),
                "diger_dunya_milyon": float(satir["Rest of world"]),
            }
        )

    return {
        "kaynak": "IEA",
        "birim": "million vehicles",
        "veriler": veriler,
    }


if __name__ == "__main__":
    csv_yolu = "data/raw/global-electric-car-sales-2020-2026.csv"

    sonuc = iea_ev_satis_verilerini_oku(csv_yolu)

    print(f"Kaynak: {sonuc['kaynak']}")
    print(f"Birim: {sonuc['birim']}")
    print(f"Toplam yıl sayısı: {len(sonuc['veriler'])}")
    print()

    for veri in sonuc["veriler"]:
        tahmin = " (tahmin)" if veri["tahmin"] else ""

        print(
            f"{veri['yil']}{tahmin}: "
            f"Çin={veri['cin_milyon']}, "
            f"Avrupa={veri['avrupa_milyon']}, "
            f"ABD={veri['abd_milyon']}, "
            f"Diğer={veri['diger_dunya_milyon']}"
        )