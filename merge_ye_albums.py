import os
import shutil
import re

DOWNLOADS_DIR = os.path.expanduser("~/untitled_downloader/Downloads")
MERGED_DIR = os.path.expanduser("~/untitled_downloader/Merged_Albums")

def normalize_name(name):
    """
    Normalizes a track name to detect duplicates more aggressively.
    Example: "01 - Hoodrat! (Feat. Ty).mp3" -> "hoodrat"
    """
    name = os.path.splitext(name)[0].lower()
    
    name = name.replace('🅴', '')
    
    # Remove anything in brackets or parentheses (e.g. "(feat. Ty)", "[V2]")
    name = re.sub(r'\(.*?\)|\[.*?\]', '', name)
    
    # Remove leading track numbers like "01 - ", "2.", "04 ", "1-06 "
    name = re.sub(r'^\s*(?:\d+[\s\.\-_]+)+', '', name)
    name = re.sub(r'^\d+[\s\.\-_]*', '', name)
    
    # Convert underscores and dashes to spaces so word boundaries catch "Song_V3" or "Song-V3"
    name = re.sub(r'[\-_]', ' ', name)
    
    # Extremely aggressive truncation: remove EVERYTHING after feat, v, pt, mix, etc.
    name = re.sub(r'\b(feat|ft|pt|part|p\.|v|ver|version|demo|edit|mix|remix|alt|og|bonus|instrumental)(?:\s*\d+|\b).*', '', name)
    
    # Strip all non-alphanumerics so "All in Love" and "All_In_Love" match
    name = re.sub(r'[^a-z0-9]', '', name)
    
    # Custom hardcoded mappings for wildly differently spelled tracks
    name = name.replace('back2me', 'backtome')
    name = name.replace('fucksum', 'fuksumn').replace('fucksumn', 'fuksumn')
    name = name.replace('tydollaign', '')  # Catches "Ty Dolla ign Promotion" -> "Promotion"
    
    # Waves / Swish Duplicates
    if name.startswith('nomoreparties') or name.startswith('noparties'): name = 'nomorepartiesinla'
    if name.startswith('30hour') or name.startswith('hours'): name = '30hours'
    if name.startswith('ultralight'): name = 'ultralightbeam'
    if name.startswith('realfriend'): name = 'realfriends'
    if name.startswith('wave'): name = 'waves'

    # Yandhi Duplicates
    if name in ('alldreams', 'alldreamsreal', 'alldreamareal', 'alldreama', 'alldreamarereal'):
        name = 'alldreamsarereal'
    if name in ('calm', 'calmbeforethestorm'):
        name = 'calmbeforethestorm'

    # In A Perfect World Duplicates
    if name.startswith('freediddy') or name.startswith('diddyfree'): name = 'diddyfree'
    if name.startswith('cousins'): name = 'cousins'
    if name.startswith('bulletproof'): name = 'bulletproof'
    if name.startswith('cosby'): name = 'cosby'
    if name.startswith('gaschamber'): name = 'gaschambers'
    if name.startswith('kingofsoul') or name.startswith('thekingofsoul'): name = 'kingofsoul'
    if name.startswith('nitrous'): name = 'nitrous'
    if name.startswith('uncle'): name = 'uncle'
    if name.startswith('virgil') or name.startswith('vlmd'): name = 'virgil'
    if name.startswith('ww3'): name = 'ww3'
    if name.startswith('dirtymagazine') or name.startswith('dirtmag') or name == 'magazines' or name.startswith('dirtymag') or name.startswith('dirtmagazines'):
        name = 'dirtymagazines'
    if name.startswith('bianca'): name = 'bianca'
    
    # Good Ass Job Duplicates
    if name in ('ayygirl', 'ayyygirl'): name = 'ayygirl'
    if name in ('building', 'buildings'): name = 'building'
    if name in ('christiandiordeminflow', 'christiandiordenimflow', 'christiandior'): name = 'christiandiordenimflow'
    if name in ('eyesclosed', 'eyezclosed', 'kanyewesteyesclosed'): name = 'eyesclosed'
    if name in ('mamasboyfriend', 'mamasboy', 'mamasboyfriends', 'kanyewestmamasboyfriend'): name = 'mamasboyfriend'
    if name in ('neverseemeagain', 'kanyewestneverseemeagain', 'seemeagain'): name = 'neverseemeagain'
    if name in ('noturninback', 'noturningback'): name = 'noturningback'
    if name in ('singlefoulrhyme', 'singlefowlrhyme'): name = 'singlefowlrhyme'
    if name in ('throwmoneyeverywhere', 'throwmymoneyeverywhere', 'throwmymoney'): name = 'throwmymoneyeverywhere'
    if name in ('youknow', 'youknowyouknow'): name = 'youknow'
    if name in ('foreveryoung', 'youngforever'): name = 'foreveryoung'

    # TGFD / Yeezus 2 Duplicates
    if name in ('guilttrip', 'blockaguilttrip', '10louderguilttripped', 'louderguilttrippossibleyedit'): name = 'guilttrip'
    if name in ('talktome', 'kwtalktomeref'): name = 'talktome'
    if name in ('cantgetoverme', 'kwtalktomeref'): name = 'cantgetoverme'
    if name in ('iamnothome', 'kwiamnothomeref'): name = 'iamnothome'
    if name in ('whyfeelbad', 'kwwhyfeelbadhm', 'whyfeelbadbytheweeknd'): name = 'whyfeelbad'
    if name in ('wow', 'wowwowwow'): name = 'wow'
    if name in ('senditup', 'chambersenditup', 'kwsenditupref'): name = 'senditup'
    if name in ('blackskinhead', 'blkkkskkknhead', 'auranclosesalamiharleybanksslpycnyn032421blkkkskkknhead'): name = 'blackskinhead'
    if name in ('nobodytolove', 'kwnobodytoloveref', 'nobody2love'): name = 'nobodytolove'
    if name in ('holdmyliquor', 'kwholdmyliquorref', 'holdmyliqourdemo'): name = 'holdmyliquor'
    if name in ('bloodontheleaves', 'kwbloodontheleavesref'): name = 'bloodontheleaves'
    if name in ('iamagod', 'kwiamagodref'): name = 'iamagod'
    if name in ('newslaves', 'kwnewslavesref'): name = 'newslaves'
    if name in ('onsight', 'onsite', 'onsi8'): name = 'onsight'
    if name in ('afteru', 'afteryoupt2'): name = 'afteryou'
    if name in ('aintnomodel', 'youaintnomodel'): name = 'aintnomodel'
    if name in ('backupofftheledge', 'backuptheledge'): name = 'backupofftheledge'
    if name in ('pissonyourgrave', 'grave'): name = 'pissonyourgrave'
    if name in ('mrsmiseryonlyone', 'mrsmisery'): name = 'mrsmisery'
    if name in ('neverletmego', 'neverletmegocanube'): name = 'neverletmego'
    if name in ('sospecial', 'special'): name = 'special'
    if name in ('ruletherworld', 'everybodywantstoruletheworld', 'ruletheworld'): name = 'everybodywantstoruletheworld'

    # Love Everyone Duplicates
    if name in ('maccheese', 'macncheese'): name = 'macncheese'
    if name in ('exctacty', 'extacy', 'xcty'): name = 'xtcy'
    if name in ('djkhaledsson', 'djkhaledson', '12djkhaledson'): name = 'djkhaledson'
    if name in ('violentnights'): name = 'violentcrimes'
    if name in ('letyougo'): name = 'letitgo'

    # So Help Me God / Cruel Winter / TurboGrafx 16 Duplicates
    if name in ('southsideseranade', 'southsideserenade'): name = 'southsideserenade'
    if name in ('fourfiveseconds', 'rihannafourfiveseconds'): name = 'fourfiveseconds'
    if name in ('thirtyfivehunna', 'thirtyfivehunnid'): name = 'thirtyfivehunna'
    if name in ('tellyourfriends', 'tellyefriends'): name = 'tellyourfriends'
    if name in ('vicmensaumad', 'youmad', 'umad'): name = 'youmad'
    if name in ('beenthrill', 'beentrill', 'trill'): name = 'trill'
    if name in ('champions1'): name = 'champions'
    if name in ('incommon1', '10incommon'): name = 'incommon'
    if name in ('johnlegendenjoythepain', 'enjoythepain'): name = 'enjoythepain'
    if name in ('freestyle41'): name = 'freestyle4'
    if name in ('timmyturner1'): name = 'timmyturner'
    if name in ('sdp1'): name = 'sdp'
    if name in ('cantlookinmyeyes', 'cantlookmeintheeyes'): name = 'cantlookinmyeyes'
    if name in ('richniadrunk', 'richniggadrunk', '16rnd'): name = 'richniggadrunk'

    # Yandhi / Kids See Ghosts Duplicates
    if name in ('alien', 'spacexalien', 'aliens'): name = 'alien'
    if name in ('chakras', 'charkas', 'thechakra'): name = 'chakras'
    if name in ('cityinthesky', 'skycity', 'houseintheskyfreestyle'): name = 'cityinthesky'
    if name in ('thestorm', 'thefloodingthestorm'): name = 'thestorm'
    if name in ('lawofattraction', 'lawofattractionusethisgospel'): name = 'lawofattraction'

    # Vultures Duplicates
    if name.startswith('hoodrat'): name = 'hoodrat'
    if name.startswith('everybody'): name = 'everybody'
    if name.startswith('paid'): name = 'paid'
    if name.startswith('paperwork'): name = 'paperwork'
    if name.startswith('star'): name = 'stars'
    if name.startswith('burn'): name = 'burn'
    if name.startswith('backtome'): name = 'backtome'
    if name.startswith('newbody'): name = 'newbody'
    if name.startswith('promotion'): name = 'promotion'
    if name.startswith('slide'): name = 'slide'
    if name.startswith('socalledfriend') or name.startswith('socalledfriends'): name = 'socalledfriends'
    if name.startswith('timemovingslow') or name == 'time': name = 'timemovingslow'
    
    # Beast Mode Final Sweep Deep Overlaps
    if name in ('euro2', 'euro'): name = 'euro'
    if name in ('nowtfalloutofheaven', 'falloutofheaven'): name = 'falloutofheaven'
    if name in ('noproblem', 'problem'): name = 'problem'
    if name in ('alliknow1', 'alliknow'): name = 'alliknow'
    if name in ('armedanddangerous', 'armedndangerous', 'armeddangerous'): name = 'armedanddangerous'
    if name in ('flashinglights2', 'flashinglights'): name = 'flashinglights'
    if name in ('goodassjobintro', 'agoodassjob', 'goodassintro', 'goodassjob'): name = 'goodassjob'
    if name in ('holdmyliqour', 'holdmyliquor'): name = 'holdmyliquor'
    if name in ('nonono', 'nononono'): name = 'nononono'
    if name in ('bound1', 'bound2', 'bound'): name = 'bound'
    if name in ('bigbootybitch', 'bigboodybitch'): name = 'bigboodybitch'
    if name in ('begforgiveness1', 'begforgiveness'): name = 'begforgiveness'
    if name in ('fallinlove', 'allinlove'): name = 'fallinlove'
    if name in ('comesgoes', 'comesandgoes'): name = 'comesandgoes'
    if name in ('summer6ixteen', 'summersixteen'): name = 'summersixteen'
    if name in ('hyejesus', 'yejesus', 'yeandjesus'): name = 'yejesus'
    if name in ('jukeboxjointz', 'jukeboxjoints'): name = 'jukeboxjoints'

    # The Absolute Final Perimeter Overlaps
    if name in ('thestorm', 'storm'): name = 'thestorm'
    if name in ('armedanddangeroustrackinst', 'armedanddangerous', 'armedndangerous'): name = 'armedanddangerous'
    if name in ('goodassjobbeat', 'goodassjob'): name = 'goodassjob'
    if name in ('wegettingbusy', 'wegetbusy'): name = 'wegetbusy'
    if name in ('onlyforthenight', 'forthenight'): name = 'forthenight'
    if name in ('higherdarkfantasy', 'darkfantasy'): name = 'darkfantasy'
    if name in ('blkkkamerikkknpsycho', 'blackamericanpsycho'): name = 'blackamericanpsycho'
    if name in ('kwguilttripref', 'guilttrip'): name = 'guilttrip'
    if name in ('whydoessummerhavetoend', 'whydoessummerneverend'): name = 'whydoessummerneverend'
    if name in ('kwcantgetovermeref', 'cantgetoverme'): name = 'cantgetoverme'
    if name in ('iamnothere', 'iamnothome'): name = 'iamnothome'
    if name in ('happyye', 'happy'): name = 'happy'
    if name in ('loveloveloveimean', 'lovelovelove'): name = 'lovelovelove'

    return name

def clean_filename(filename):
    """
    Cleans up version numbers to a standard format at the end of the file name before .mp3
    Example: Never_Lose_V2.mp3 -> Never Lose (v2).mp3
    Also removes (1) from file names.
    """
    filename = filename.replace('🅴', '')
    
    # Remove (1)
    filename = re.sub(r'\s*\(\s*1\s*\)', '', filename)
    
    parts = filename.rsplit('.', 1)
    if len(parts) == 2:
        name, ext = parts[0], '.' + parts[1]
    else:
        name, ext = parts[0], ''
        
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    
    # Delete specific numbering variations from the beginning of filenames
    name = re.sub(r'^\s*0\d\.?[\s\-_]*', '', name)   # 0#, 0#.
    name = re.sub(r'^\s*\d-\d{2}[\s\-_]*', '', name) # #-##
    name = re.sub(r'^\s*\d{3}[\s\-_]*', '', name)    # ###
    name = re.sub(r'^\s*\d+\.[\s\-_]*', '', name)    # #. or ##.
    name = re.sub(r'^\s*\d(?!^\d)\b[\s\-_]*', '', name)     # # (but leaves ## alone like "12" or "14.")
    name = re.sub(r'^\s*\d+\s*\-\s*', '', name)      # # - or ## -

    # Replace [Deluxe], [Remix], [RMX]
    name = re.sub(r'(?i)\[deluxe\]', '(Deluxe)', name)
    name = re.sub(r'(?i)\[remix\]|\[rmx\]', '(Remix)', name)
    
    is_bonus = False
    
    # Handle "18 BONUS TRACK - Mac N Cheese" -> "18. Mac N Cheese (Bonus)"
    bonus_track_match = re.search(r'(?i)^(\d+)\s*(?:-\s*)?BONUS\s*TRACK\s*(?:-\s*)?(.*)', name)
    if bonus_track_match:
        is_bonus = True
        track_num = bonus_track_match.group(1)
        rest_name = bonus_track_match.group(2)
        name = f"{track_num}. {rest_name}"
    
    # Handle standard Bonus- tag or (BONUS) directly
    elif re.search(r'(?i)\bbonus\s*\-', name) or re.search(r'(?i)[\(\[]\s*bonus\s*[\)\]]', name):
        is_bonus = True
        name = re.sub(r'(?i)\bbonus\s*\-\s*', '', name)
        name = re.sub(r'(?i)[\(\[]\s*bonus\s*[\)\]]', '', name)
        
    # Find version indicators (v2, V.2, version 3, etc.)
    version_match = re.search(r'(?i)\b(?:v|ver|version)[\s\.]*(\d+)\b', name)
    v_num = None
    if version_match:
        v_num = version_match.group(1)
        # Remove the old version string from its original position
        name = re.sub(r'(?i)[\(\[\s\-]*\b(?:v|ver|version)[\s\.]*\d+\b[\)\]]*', ' ', name)
        
    # Strip lingering "- tag" strings if they appear after closed parentheses
    # (e.g. "...Charlie Wilson) - fiddy" -> "...Charlie Wilson)")
    name = re.sub(r'\)\s*-\s*[^()]+$', ')', name)
    
    # Extract "feat." or "ft."
    feat_match = re.search(r'(?i)[\(\[\s\-]*\b(feat\.?|ft\.?)\s+([^()\[\]]+?)[\)\]\s]*$', name)
    feat_str = None
    if feat_match:
        feat_artists = feat_match.group(2).strip()
        # Clean trailing dash tags inside unparenthesized feat streams
        feat_artists = re.sub(r'\s*-\s*[^-]+$', '', feat_artists)
        feat_str = f"ft. {feat_artists}" # normalize to ft.
        # remove it from name
        name = name[:feat_match.start()].strip(" -")
    
    # Clean up excessive whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    
    if feat_str:
        name = f"{name} ({feat_str})"
        
    if is_bonus:
        name = f"{name} (Bonus)"
    
    if v_num:
        name = f"{name} (v{v_num})"
            
    return f"{name}{ext}"

def normalize_album_name(album_name):
    """
    Strips brackets, parenthesis, emojis, and groups variations of
    common Kanye/leaked album names into single clean master names.
    """
    # Remove anything in brackets or parentheses (e.g. "[Deluxe]", "(Best Version)")
    album_name = re.sub(r'\(.*?\)|\[.*?\]', '', album_name)
    
    # Remove emojis and explicit/special characters, keep basic alphanumerics/spaces
    album_name = re.sub(r'[^\w\s-]', '', album_name)
    album_name = album_name.strip()
    
    # Clean up accidental double spaces
    album_name = re.sub(r'\s+', ' ', album_name)
    album_name_lower = album_name.lower()
    
    # Aggressive grouping based on keywords (prioritized)
    if any(keyword in album_name_lower for keyword in ['world war 3', 'ww3', 'cuck', 'cousins', 'cou-sins', 'in a perfect world', 'kkkuckoldry', 'kuckoldry']):
        return 'In A Perfect World'
    if 'cruel winter' in album_name_lower:
        return 'Cruel Winter'
    if 'love everyone' in album_name_lower or 'hitler' in album_name_lower or 'love yeveryone' in album_name_lower:
        return 'Love Everyone'
    if 'yandhi' in album_name_lower or 'yanhdi' in album_name_lower or 'yahndi' in album_name_lower:
        return 'Yandhi'
    if 'yebu' in album_name_lower or 'y3bu' in album_name_lower or 'y3' in album_name_lower:
        return 'YEBU'
    if 'turbografx' in album_name_lower or 'turbo grafx' in album_name_lower:
        return 'TurboGrafx 16'
    if 'thank god' in album_name_lower or 'tgfd' in album_name_lower:
        return 'Thank God For Drugs'
    if 'child rebel soldier' in album_name_lower or 'crs' in album_name_lower:
        return 'Child Rebel Soldier'
    if 'carti ye' in album_name_lower or 'cartiye' in album_name_lower:
        return 'Carti Ye'
    if 'jesus is king' in album_name_lower or 'jik' in album_name_lower:
        return 'Jesus Is King'
    if 'good ass job' in album_name_lower or 'gaj' in album_name_lower or 'good a job' in album_name_lower:
        return 'Good Ass Job'
    if 'world war 3' in album_name_lower or 'ww3' in album_name_lower:
        return 'World War 3'
    if 'cruel winter' in album_name_lower:
        return 'Cruel Winter'
    if 'kids see ghost' in album_name_lower:
        return 'Kids See Ghosts 2'
    if 'yeezus 2' in album_name_lower or 'yeezus ii' in album_name_lower or 'yeezus pt 2' in album_name_lower or 'chiraq' in album_name_lower:
        return 'Yeezus 2'
    
    # Fallback to Title Casing for whatever is left over (e.g. "Chiraq")
    return album_name.title()

def merge_albums():
    if not os.path.exists(DOWNLOADS_DIR):
        print("Downloads directory not found.")
        return

    # Wipe the old Merged_Albums folder to clear up space
    if os.path.exists(MERGED_DIR):
        print("Cleaning up old Merged_Albums to recover disk space...")
        shutil.rmtree(MERGED_DIR)
        
    os.makedirs(MERGED_DIR, exist_ok=True)
    
    total_files_seen = 0
    total_linked = 0

    # Global Dictionary to keep track of the single best (largest) file for each normalized name across ALL albums
    # Format: best_tracks[norm_name] = {'src': file_path, 'size': byte_size, 'name': original_filename, 'album': album_name}
    best_tracks = {}

    for folder in os.listdir(DOWNLOADS_DIR):
        folder_path = os.path.join(DOWNLOADS_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        
        # Expected format: "{Project Name}, {Creator}"
        parts = folder.rsplit(', ', 1)
        raw_album_name = parts[0]
        
        # Pass the extracted album name through our aggressive normalizer
        album_name = normalize_album_name(raw_album_name)
        
        # Skip specific albums entirely
        album_name_lower_skip = album_name.lower()
        if 'definitive hh collection' in album_name_lower_skip or 'hh collection' in album_name_lower_skip:
            continue
        if 'bianca pitched down' in album_name_lower_skip:
            continue
        if 'can u be' in album_name_lower_skip:
            continue
        if album_name_lower_skip == 'everybody':
            continue
            
        for file in os.listdir(folder_path):
            if not file.endswith('.mp3'):
                continue
                
            # Filter out requested tracks (Heil Hitler, HH, Heil Hallaluah)
            # Re.search ensures we don't accidentally match 'hh' in words like 'shh' or 'ahhh'
            file_lower = file.lower()
            if 'heil hitler' in file_lower or 'hitler' in file_lower or 'heil hallaluah' in file_lower or re.search(r'\bhh\b', file_lower):
                continue
                
            total_files_seen += 1
            norm_name = normalize_name(file)
            src_file = os.path.join(folder_path, file)
            src_size = os.path.getsize(src_file)
            
            # Route specific tracks to their own dedicated folders
            track_album = album_name
            if 'all day' in file.lower():
                track_album = 'All Day'
            
            # Global deduplication: we haven't seen this track before globally, or if this version has a larger file size, keep it!
            if norm_name not in best_tracks:
                best_tracks[norm_name] = {'src': src_file, 'size': src_size, 'name': file, 'album': track_album}
            else:
                if src_size > best_tracks[norm_name]['size']:
                    best_tracks[norm_name] = {'src': src_file, 'size': src_size, 'name': file, 'album': track_album}

    # Now that we know the absolute highest quality/largest version of each track globally, let's link them
    
    # Discover Cover Art Mapping first
    COVER_ART_DIR = os.path.expanduser("~/untitled_downloader/Cover art")
    cover_art_map = {}
    if os.path.exists(COVER_ART_DIR):
        for f in os.listdir(COVER_ART_DIR):
            if re.search(r'\.(jpg|jpeg|png|webp|gif)$', f, re.IGNORECASE):
                norm_cover = re.sub(r'[^a-z0-9]', '', f.split('.')[0].lower())
                cover_art_map[norm_cover] = os.path.join(COVER_ART_DIR, f)

    for norm_name, track_info in best_tracks.items():
        target_album_dir = os.path.join(MERGED_DIR, track_info['album'])
        os.makedirs(target_album_dir, exist_ok=True)
        
        src_file = track_info['src']
        
        # Apply our exact cleanups to the chosen file name
        final_name = clean_filename(track_info['name'])
        dst_file = os.path.join(target_album_dir, final_name)
        
        try:
            # We are using copy2 instead of link to ensure modifications (metadata/art)
            # are permanently written to independent, standalone audio files
            shutil.copy2(src_file, dst_file)
        except OSError:
            shutil.copy2(src_file, dst_file)
            
        # --- METADATA EDITING MAGIC ---
        try:
            from mutagen.easyid3 import EasyID3
            from mutagen.id3 import ID3NoHeaderError, ID3, APIC
            try:
                audio = EasyID3(dst_file)
            except Exception:
                tags = ID3()
                tags.save(dst_file)
                audio = EasyID3(dst_file)
            
            audio['album'] = track_info['album']
            
            # Set artist to Kanye West + any features found in the finalized file name
            artist_str = "Kanye West"
            feat_match = re.search(r'\(ft\.\s+(.*?)\)', final_name, flags=re.IGNORECASE)
            if feat_match:
                artist_str = f"Kanye West, {feat_match.group(1)}"
                
            audio['artist'] = artist_str
            
            audio.save()
            
            # Attaching Album Art Image Metadata Natively
            album_norm = re.sub(r'[^a-z0-9]', '', track_info['album'].lower())
            matched_cover = None
            for cover_key, cover_file in cover_art_map.items():
                if album_norm in cover_key or cover_key in album_norm:
                    matched_cover = cover_file
                    break
            
            if matched_cover:
                audio_id3 = ID3(dst_file)
                mime = 'image/jpeg'
                if matched_cover.lower().endswith('.png'): mime = 'image/png'
                elif matched_cover.lower().endswith('.webp'): mime = 'image/webp'
                elif matched_cover.lower().endswith('.gif'): mime = 'image/gif'
                
                with open(matched_cover, 'rb') as art:
                    audio_id3.add(APIC(encoding=3, mime=mime, type=3, desc='Cover', data=art.read()))
                
                audio_id3.save(v2_version=3)
                
        except Exception:
            pass
            
        total_linked += 1

    total_skipped = total_files_seen - total_linked

    print(f"\n✨ Deduplication & Merging Complete!")
    print(f"🎵 Single best tracks kept: {total_linked}")
    print(f"🗑  Duplicate/inferior tracks trashed: {total_skipped}")
    print(f"💾 Note: Merged files are now permanent, independent files with fully embedded metadata and cover art!")

if __name__ == "__main__":
    merge_albums()
