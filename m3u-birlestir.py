import requests
import re
from collections import defaultdict

# M3U dosyalarının URL'leri
urls = [
    "https://raw.githubusercontent.com/MDuymaz/goltv/refs/heads/main/gol.m3u",
    "https://raw.githubusercontent.com/MDuymaz/Clone/refs/heads/main/output.m3u",
    "https://raw.githubusercontent.com/MDuymaz/efendikaptan/refs/heads/main/mac_verileri.m3u"
]

# Birleştirilmiş M3U dosyasının içeriği
merged_content = ""
extm3u_added = False  # #EXTM3U etiketi zaten eklendi mi kontrolü
grouped_lines = defaultdict(list)  # tvg-name ve group-title'a göre gruplayacağız

# Her bir dosyayı indirip içeriğini birleştirme
for url in urls:
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        # Eğer #EXTM3U etiketi varsa, sadece bir kez ekleyelim
        if "#EXTM3U" in content:
            if not extm3u_added:
                merged_content += "#EXTM3U\n\n\n"  # İlk #EXTM3U ekleniyor ve ardından 2 boş satır ekleniyor
                extm3u_added = True
            content = content.replace("#EXTM3U", "")  # Diğer #EXTM3U etiketlerini kaldır
        
        # Satırlara ayırma
        lines = content.splitlines()
        buffer = []  # Bir `#EXTINF` ve `#EXTVLCOPT` bloğunu toplamak için kullanılacak
        for line in lines:
            if line.startswith("#EXTINF"):  # Eğer satır #EXTINF ise
                if buffer:  # Eğer bir önceki satırlar varsa, bunları tvg-name ve group-title'a göre grupla
                    # tvg-name ve group-title değerlerine göre gruplama
                    match_name = re.search(r'tvg-name="([^"]+)"', buffer[0])  # tvg-name bul
                    match_group = re.search(r'group-title="([^"]+)"', buffer[0])  # group-title bul
                    if match_name and match_group:
                        tvg_name = match_name.group(1).upper()  # tvg-name'i al ve büyük harfe çevir
                        group_title = match_group.group(1).upper()  # group-title'ı al ve büyük harfe çevir
                        # Düzeltilmiş tvg-name ve group-title değerlerini güncelliyoruz
                        buffer[0] = buffer[0].replace(match_name.group(1), tvg_name)
                        buffer[0] = buffer[0].replace(match_group.group(1), group_title)
                        grouped_lines[(tvg_name, group_title)].append("\n".join(buffer))  # Satırları grupla
                    buffer = []  # Buffer'ı sıfırla
                # Yeni #EXTINF satırını ekle
                line = line.replace('group-title="7/24 TV"', 'group-title="CANLI"')
                # tvg-name içinde bulunan "- " karakterini sil
                line = re.sub(r'tvg-name=" - (.*?)"', r'tvg-name="\1"', line)
                line = line.replace(' - ', ' ')  # Ayrıca " - " karakterini silip yerine boşluk bırak
                buffer.append(line)
            elif line.startswith("#EXTVLCOPT"):  # Eğer satır #EXTVLCOPT ise
                buffer.append(line)  # #EXTVLCOPT satırını da ekle
            else:  # Diğer satırlar
                buffer.append(line)  # Normal satırı da ekle
        # Son grup için de işlemi yapalım
        if buffer:
            match_name = re.search(r'tvg-name="([^"]+)"', buffer[0])  # tvg-name bul
            match_group = re.search(r'group-title="([^"]+)"', buffer[0])  # group-title bul
            if match_name and match_group:
                tvg_name = match_name.group(1).upper()  # tvg-name'i al ve büyük harfe çevir
                group_title = match_group.group(1).upper()  # group-title'ı al ve büyük harfe çevir
                # Düzeltilmiş tvg-name ve group-title değerlerini güncelliyoruz
                buffer[0] = buffer[0].replace(match_name.group(1), tvg_name)
                buffer[0] = buffer[0].replace(match_group.group(1), group_title)
                grouped_lines[(tvg_name, group_title)].append("\n".join(buffer))  # Son satırları da grupla

# Gruplanmış verileri sırayla yazalım
for (tvg_name, group_title) in sorted(grouped_lines.keys()):
    for group in grouped_lines[(tvg_name, group_title)]:
        merged_content += group + "\n"

# Sonuçları 'playlist.m3u' dosyasına UTF-8 formatında kaydetme
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(merged_content)

print("M3U dosyaları başarıyla birleştirildi ve 'playlist.m3u' olarak kaydedildi.")
