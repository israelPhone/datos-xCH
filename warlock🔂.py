import requests, re, os, time
from datetime import datetime, timedelta

# v11.7 - Warlock 🔂 (Pausas Inteligentes + Calidad HD + Fix 3h)
ruta_trabajo = "./cams.txt"    
ruta_local = "./lista_tcl.m3u"
agente_iptv = 'VLC/3.0.18 LibVLC/3.0.18'

def generar():
    modelos_a_buscar = []
    enlaces_directos = {} 
    ignorar_viejos = False
    encontrados_ahora = 0

    # 1. ACUMULAR DEL PORTAPAPELES
    os.system("pbpaste >> ./cams.txt")

    # 2. CONTROL DE TIEMPO REALISTA
    # Si el archivo existe, comprobamos si es "viejo" para limpiar
    if os.path.exists(ruta_local):
        mtime = os.path.getmtime(ruta_local)
        diferencia = datetime.now() - datetime.fromtimestamp(mtime)
        
        # Solo si han pasado 3h reales desde la última vez que decidimos revalidar todo
        if diferencia > timedelta(hours=3):
            print(f"🕒 Ciclo de 3h cumplido: Revalidando enlaces caducados...")
            ignorar_viejos = True

    if not os.path.exists(ruta_trabajo):
        print("❌ Error: No hay datos en cams.txt.")
        return

    print("🔍 Warlock 🔂 analizando botín acumulado...")
    
    with open(ruta_trabajo, "r") as f:
        lineas = f.readlines()

    nombre_temporal = None
    for line in lineas:
        line = line.strip().replace('\\/', '/')
        if not line or line == "#EXTM3U": continue
        
        if line.startswith("#EXTINF"):
            nombre_temporal = line.split(",")[-1].strip().lower()
        elif line.startswith("http") and ".m3u8" in line:
            if nombre_temporal and not ignorar_viejos:
                # Aseguramos que el enlace mantenido tenga el tag 1080p
                link = line.replace('\\', '')
                enlaces_directos[nombre_temporal] = link if "quality" in link else f"{link}?quality=1080p"
                nombre_temporal = None
            else:
                nombre_temporal = None 
        else:
            nombre = line.lower()
            if nombre not in modelos_a_buscar:
                modelos_a_buscar.append(nombre)

    modelos_a_buscar = [m for m in modelos_a_buscar if m not in enlaces_directos]
    
    print(f"✅ {len(enlaces_directos)} enlaces activos mantenidos.")
    print(f"📡 Comprobando {len(modelos_a_buscar)} modelos (Pausas cada 30)...")

    # 3. GENERAR LISTA ACTUALIZADA
    with open(ruta_local, "w") as f_m3u:
        f_m3u.write("#EXTM3U\n")
        
        for nombre, link in enlaces_directos.items():
            f_m3u.write(f'#EXTINF:-1 group-title="Favoritas", {nombre.upper()} (HD)\n{link}\n\n')

        for i, m in enumerate(modelos_a_buscar):
            # --- TRUCO DE PAUSA CADA 30 COMPROBACIONES ---
            if i > 0 and i % 30 == 0:
                print(f"☕ Pausa de seguridad (8s) para evitar bloqueos...")
                time.sleep(8)

            try:
                r = requests.get(f"https://es.chaturbate.com/{m}/", headers={'User-Agent': agente_iptv}, timeout=5).text
                match = re.search(r'(https:[^"\']+.m3u8)', r)
                
                if match:
                    url = match.group(0).replace("\\u002D", "-").replace("\\", "")
                    url_hd = f"{url}?quality=1080p"
                    f_m3u.write(f'#EXTINF:-1 group-title="Favoritas", {m.upper()} (HD)\n{url_hd}\n\n')
                    print(f"[{i+1}/{len(modelos_a_buscar)}] ✅ {m} (1080p)")
                    encontrados_ahora += 1
                    
                    # Guardamos con el formato correcto para que el script lo lea la próxima vez
                    with open(ruta_trabajo, "a") as f_h:
                        f_h.write(f'\n#EXTINF:-1, {m}\n{url_hd}\n')
                else:
                    print(f"[{i+1}/{len(modelos_a_buscar)}] ❌ {m} (Offline)")
                
                time.sleep(0.4)
            except:
                continue

    # 4. RESUMEN FINAL
    total_total = len(enlaces_directos) + encontrados_ahora
    print("\n" + "="*40)
    print(f"📊 RESUMEN v11.7 HD")
    print(f"✅ Mantenidos: {len(enlaces_directos)}")
    print(f"📡 Nuevos: {encontrados_ahora}")
    print(f"📂 Total: {total_total}")
    print("="*40)

    os.system(f"say 'Hecho. {total_total} modelos listos.'")

if __name__ == "__main__":
    generar()
