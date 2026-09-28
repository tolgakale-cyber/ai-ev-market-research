from datetime import datetime, timezone


EPDK_KAYNAK = {
    "kurum": "Enerji Piyasası Düzenleme Kurumu (EPDK)",
    "kaynak_adi": "Şarj Hizmeti Piyasası Resmi İstatistikleri",
    "kapsam": "Türkiye",
    "kaynak_turu": "Resmi istatistik",
    "url": "https://www.epdk.gov.tr/Detay/Icerik/3-0-237/resmi-istatistikleri",
}


def epdk_kaynak_bilgisi_olustur():
    return {
        "kaynak": EPDK_KAYNAK,
        "toplanma_tarihi": datetime.now(timezone.utc).isoformat(),
        "veri_durumu": "Kaynak doğrulandı",
    }

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def epdk_rapor_baglantilarini_topla():
    sayfa_url = EPDK_KAYNAK["url"]

    response = requests.get(sayfa_url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    baglantilar = []

    for link in soup.find_all("a", href=True):
        metin = link.get_text(" ", strip=True)
        href = urljoin(sayfa_url, link["href"])

        if "şarj" in metin.lower() or "sarj" in metin.lower():
            baglantilar.append(
                {
                    "baslik": metin,
                    "url": href,
                }
            )

    return baglantilar


if __name__ == "__main__":
    raporlar = epdk_rapor_baglantilarini_topla()

    print(f"Bulunan EPDK bağlantısı: {len(raporlar)}")

    for rapor in raporlar:
        print(f"- {rapor['baslik']}")
        print(f"  {rapor['url']}")

def epdk_aylik_raporlari_topla():
    istatistik_url = (
        "https://www.epdk.gov.tr/Detay/Icerik/"
        "3-0-222-1040/enerji-donusumusarj-hizmeti-piyasasi--istatistik"
    )

    response = requests.get(istatistik_url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    raporlar = []
    gorulen_url = set()

    for link in soup.find_all("a", href=True):
        href = link.get("href", "")

        if "/Detay/DownloadDocument?id=" not in href:
            continue

        url = urljoin(istatistik_url, href)

        if url in gorulen_url:
            continue

        gorulen_url.add(url)

        # EPDK'da indirme linklerinin kendi metni boş olduğu için
        # rapor bilgisini linkin bulunduğu HTML satırından alıyoruz.
        parent = link.parent
        baglam = parent.get_text(" ", strip=True) if parent else ""

        raporlar.append(
            {
                "baslik": baglam or "EPDK Şarj Hizmeti Piyasası Raporu",
                "url": url,
                "kurum": "EPDK",
            }
        )

    return raporlar

def epdk_raporu_indir(rapor, dosya_yolu):
    response = requests.get(rapor["url"], timeout=30)
    response.raise_for_status()

    if not response.content.startswith(b"%PDF"):
        raise ValueError("EPDK raporu PDF formatında değil.")

    with open(dosya_yolu, "wb") as dosya:
        dosya.write(response.content)

    return dosya_yolu

if __name__ == "__main__":
    print("\nEPDK aylık raporları:")

    aylik_raporlar = epdk_aylik_raporlari_topla()

    print(f"Bulunan aylık rapor: {len(aylik_raporlar)}")

    for rapor in aylik_raporlar:
        print(f"- {rapor['baslik']}")
        print(f"  {rapor['url']}")