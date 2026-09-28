import re
from pypdf import PdfReader


def pdf_metnini_oku(pdf_yolu):
    reader = PdfReader(pdf_yolu)

    sayfalar = []

    for sayfa_no, sayfa in enumerate(reader.pages, start=1):
        metin = sayfa.extract_text() or ""

        sayfalar.append(
            {
                "sayfa": sayfa_no,
                "metin": metin,
            }
        )

    return sayfalar


def sayfa_metnini_bul(sayfalar, aranan_ifade):
    for sayfa in sayfalar:
        if aranan_ifade.lower() in sayfa["metin"].lower():
            return sayfa

    return None
def son_ay_sarj_verilerini_cikar(sayfalar):
    sayfa = sayfa_metnini_bul(
        sayfalar,
        "Aylara Göre Şarj Hizmeti Verileri",
    )

    if not sayfa:
        raise ValueError("Şarj hizmeti verileri sayfası bulunamadı.")

    metin = sayfa["metin"]

    satirlar = {
        "toplam_elektrik_tuketimi_mwh": r"Toplam Elektrik Tüketimi \(MWh\)\s+([0-9.\s]+)",
        "toplam_sarj_suresi_saat": r"Toplam Şarj Süresi \(saat\)\s+([0-9.\s]+)",
        "toplam_sarj_adedi": r"Toplam Şarj Adedi\s+([0-9.\s]+)",
        "sarj_basina_tuketim_kwh": r"Şarj Başına Tüketim \(kWh/şarj adet\)\s+([0-9,.\s]+)",
        "sarj_basina_sure_saat": r"Şarj Başına Süre \(saat/şarj adet\)\s+([0-9,.\s]+)",
    }

    sonuc = {}

    for alan, desen in satirlar.items():
        eslesme = re.search(desen, metin)

        if not eslesme:
            sonuc[alan] = None
            continue

        degerler = eslesme.group(1).split()

        if not degerler:
            sonuc[alan] = None
            continue

        sonuc[alan] = degerler[-1]

    return sonuc

def pazar_altyapi_verilerini_cikar(sayfalar):
    sonuc = {}

    # Elektrikli araç sayısı
    ea_sayfasi = sayfa_metnini_bul(
        sayfalar,
        "Aylık Bazda Elektrikli Araç Sayıları",
    )

    if ea_sayfasi:
        metin = ea_sayfasi["metin"]

        baslangic = metin.find("Kaynak: Türkiye İstatistik Kurumu (TÜİK)")
        bitis = metin.find("\n0", baslangic)

        if baslangic != -1 and bitis != -1:
            veri_bolumu = metin[baslangic:bitis]

            degerler = re.findall(
                r"\b\d{1,3}(?:\.\d{3})+\b",
                veri_bolumu,
            )

            if degerler:
                sonuc["elektrikli_arac_sayisi"] = degerler[-1]

    # Şarj noktası sayıları
    sarj_sayfasi = sayfa_metnini_bul(
        sayfalar,
        "Toplam Şarj Noktası (Soket) Sayısı",
    )

    if sarj_sayfasi:
        metin = sarj_sayfasi["metin"]

        toplam_bitis = metin.find("\n0")

        if toplam_bitis != -1:
            toplam_bolum = metin[:toplam_bitis]

            toplam_degerler = re.findall(
                r"\b\d{1,3}(?:\.\d{3})+\b",
                toplam_bolum,
            )

            if toplam_degerler:
                sonuc["toplam_sarj_noktasi"] = toplam_degerler[-1]

                        # AC şarj noktası serisi
        satirlar = metin.splitlines()

        ac_baslik_index = None

        for i, satir in enumerate(satirlar):
            if satir.strip() == "AC Şarj Noktası Sayısı":
                ac_baslik_index = i
                break

        if ac_baslik_index is not None:
            for satir in reversed(satirlar[:ac_baslik_index]):
                degerler = satir.split()

                if len(degerler) == 13 and all(
                    re.fullmatch(r"\d{1,3}(?:\.\d{3})+", deger)
                    for deger in degerler
                ):
                    sonuc["ac_sarj_noktasi"] = degerler[-1]
                    break

    # Toplam kurulu güç (MW)
    kurulu_guc_sayfasi = sayfa_metnini_bul(
        sayfalar,
        "Şarj İstasyonları Toplam Kurulu Gücü",
    )

    if kurulu_guc_sayfasi:
        satirlar = kurulu_guc_sayfasi["metin"].splitlines()

        for satir in satirlar:
            degerler = satir.split()

            if len(degerler) == 13 and all(
                re.fullmatch(r"\d{1,3}(?:\.\d{3})+", deger)
                for deger in degerler
            ):
                sonuc["toplam_kurulu_guc_mw"] = degerler[-1]
                break

        # Kurulu g?? / elektrikli ara? (kW/EA)
        for satir in satirlar:
            degerler = satir.split()

            if len(degerler) == 13 and all(
                re.fullmatch(r"\d+,\d+", deger)
                for deger in degerler
            ):
                sonuc["kurulu_guc_kw_arac"] = degerler[-1]
                break

    # DC = Toplam - AC
    if (
        "toplam_sarj_noktasi" in sonuc
        and "ac_sarj_noktasi" in sonuc
    ):
        toplam = int(
            sonuc["toplam_sarj_noktasi"].replace(".", "")
        )
        ac = int(
            sonuc["ac_sarj_noktasi"].replace(".", "")
        )

        dc = toplam - ac

        sonuc["dc_sarj_noktasi"] = (
            f"{dc:,}".replace(",", ".")
        )

    return sonuc


if __name__ == "__main__":
    pdf_yolu = "data/epdk_agustos_2026.pdf"

    sayfalar = pdf_metnini_oku(pdf_yolu)

    print(f"Okunan sayfa sayısı: {len(sayfalar)}")

    sarj_verileri_sayfasi = sayfa_metnini_bul(
        sayfalar,
        "Aylara Göre Şarj Hizmeti Verileri",
    )

    if sarj_verileri_sayfasi:
        print(
            f"Şarj hizmeti verileri bulundu: "
            f"Sayfa {sarj_verileri_sayfasi['sayfa']}"
        )
    else:
        print("Şarj hizmeti verileri bulunamadı.")