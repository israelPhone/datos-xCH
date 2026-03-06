import requests, re, os, time

# v11.6 - Warlock 🔞 (Forzar 1080p + Resumen Visual Corregido)
ruta_trabajo = "./cams.txt"    
ruta_local = "./lista_tcl.m3u"
agente_iptv = 'VLC/3.0.18 LibVLC/3.0.18'

def generar():
    # --- RECOGER PORTAPAPELES AL INICIO ---
    os.system("pbpaste > ./cams.txt")

    modelos_a_buscar = []
    enlaces_directos = {} 
    encontrados_ahora = 0

    if not os.path.exists(ruta_trabajo) or os.path.getsize(ruta_trabajo) == 0:
        print("❌ Error: El portapapeles estaba vacío o no hay datos.")
        return

    print("🔍 Warlock 🔞 analizando el botín en HD...")
    
    with open(ruta_trabajo, "r") as f:
        lineas = f.readlines()

    nombre_temporal = None
    for line in lineas:
        line = line.strip().replace('\\/', '/') 
        if not line or line == "#EXTM3U": continue
        
        if line.startswith("#EXTINF"):
            nombre_temporal = line.split(",")[-1].strip().lower()
        elif line.startswith("http") and ".m3u8" in line:
            if nombre_temporal:
                # Aplicamos parámetro de calidad a enlaces directos existentes
                link_limpio = line.replace('\\', '')
                if "?" in link_limpio:
                    link_limpio += "&quality=1080p"
                else:
                    link_limpio += "?quality=1080p"
                enlaces_directos[nombre_temporal] = link_limpio
                nombre_temporal = None
        else:
            nombre = line.lower()
            if nombre not in modelos_a_buscar:
                modelos_a_buscar.append(nombre)

    modelos_a_buscar = [m for m in modelos_a_buscar if m not in enlaces_directos]
    
    with open(ruta_local, "w") as f_m3u:
        f_m3u.write("#EXTM3U\n")
        
        for nombre, link in enlaces_directos.items():
            f_m3u.write(f'#EXTINF:-1 group-title="Favoritas", {nombre.upper()} (HD)\n{link}\n\n')

        for i, m in enumerate(modelos_a_buscar):
            try:
                r = requests.get(f"https://es.chaturbate.com/{m}/", headers={'User-Agent': agente_iptv}, timeout=5).text
                match = re.search(r'(https:[^"\']+.m3u8)', r)
                
                if match:
                    # Forzamos 1080p en los nuevos enlaces encontrados
                    url = match.group(0).replace("\\u002D", "-").replace("\\", "")
                    url_hd = f"{url}?quality=1080p"
                    f_m3u.write(f'#EXTINF:-1 group-title="Favoritas", {m.upper()} (HD)\n{url_hd}\n\n')
                    print(f"[{i+1}/{len(modelos_a_buscar)}] ✅ {m} (1080p)")
                    encontrados_ahora += 1
                else:
                    print(f"[{i+1}/{len(modelos_a_buscar)}] ❌ {m}")
                
                time.sleep(0.4)
            except:
                continue

    # 3. NOTIFICACIÓN VISUAL Y RESUMEN FINAL (Indentación corregida)
    total = len(enlaces_directos) + encontrados_ahora
    print("\n" + "="*40)
    print(f"📊 RESUMEN DE LIMPIEZA v11.6 HD")
    print(f"✅ Enlaces directos: {len(enlaces_directos)}")
    print(f"📡 Buscados y OK: {encontrados_ahora}")
    print(f"📂 Total en lista: {total}")
    print("="*40)

    os.system(f"say 'Lista completada de  {total}.'")

if __name__ == "__main__":
    generar()
